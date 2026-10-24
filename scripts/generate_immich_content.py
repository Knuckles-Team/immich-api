#!/usr/bin/env python3
"""Derive a conservative structural projection from the pinned OpenAPI contract.

This generates declarations, not graph observations. The selected properties are
an explicit privacy/relevance policy; types, requiredness and reference targets
come from the source schema. Run with --check to detect stale generated content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "immich_api"
SCHEMA_HASH = "7db8383741eeb5c5c8c87a6221cd1cdd1206c8b1190b83363c64223a00bb020b"
POLICY = {
    "AssetResponseDto": (
        "ImmichAsset",
        "id type originalMimeType duration width height fileCreatedAt updatedAt isFavorite isArchived isTrashed visibility owner people tags stack",
    ),
    "AlbumResponseDto": (
        "ImmichAlbum",
        "id albumName assetCount shared hasSharedLink createdAt updatedAt albumUsers albumThumbnailAssetId",
    ),
    "PersonResponseDto": (
        "ImmichPersonRecord",
        "id name isHidden isFavorite updatedAt",
    ),
    "UserResponseDto": ("ImmichUser", "id name"),
    "LibraryResponseDto": ("ImmichLibrary", "id name assetCount createdAt updatedAt"),
    "AlbumUserResponseDto": ("ImmichAlbumMembership", "role user"),
    "TagResponseDto": ("ImmichTag", "id name createdAt updatedAt"),
    "AssetStackResponseDto": ("ImmichAssetStack", "id assetCount primaryAssetId"),
}
PREFIXES = """@prefix : <http://knuckles.team/kg#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

"""


def literal(value):
    return json.dumps(value, ensure_ascii=False)


def unwrap(schema, definitions):
    """Preserve nullability while unwrapping generated scalar/reference forms."""
    nullable = False
    while True:
        if "anyOf" in schema:
            choices = schema["anyOf"]
            non_null = [item for item in choices if item.get("type") != "null"]
            if len(non_null) != 1:
                raise ValueError("Unsupported structural union")
            nullable = len(non_null) != len(choices)
            schema = non_null[0]
        elif "allOf" in schema and len(schema["allOf"]) == 1:
            schema = schema["allOf"][0]
        elif "$ref" in schema and schema["$ref"].split("/")[-1] not in POLICY:
            schema = definitions[schema["$ref"].split("/")[-1]]
        else:
            return schema, nullable


def artifacts():
    contract = json.loads((PACKAGE / "openapi_contract.json").read_text())
    if contract["source_sha256"] != SCHEMA_HASH:
        raise ValueError(
            "Review the structural selection before changing source schema"
        )
    definitions = contract["definitions"]
    source = f"urn:sha256:{SCHEMA_HASH}"
    ontology = [
        PREFIXES,
        f'<{source}> a prov:Entity ; rdfs:label "Immich 3.2.2 OpenAPI source bytes" .\n',
    ]
    ontology.append(
        f'<http://knuckles.team/kg/immich> a owl:Ontology ; prov:wasDerivedFrom <{source}> ; rdfs:comment "Selected structural DTO model. No live ingestion or identity equivalence is asserted." .\n'
    )
    shapes = [PREFIXES]
    resources, mappings, provenance = [], {}, []
    for schema_name, (class_name, selection) in POLICY.items():
        dto = definitions[schema_name]
        pointer = f"#/components/schemas/{schema_name}"
        class_comment = f"Structural projection of {schema_name}."
        if schema_name == "PersonResponseDto":
            class_comment += " A vendor person record; no equivalence to a verified real-world Person is inferred."
        ontology.append(
            f":{class_name} a owl:Class ; rdfs:comment {literal(class_comment)} ; prov:wasDerivedFrom <{source}{pointer}> .\n"
        )
        shape_fields, relations, fields = [], [], {}
        for field in selection.split():
            original = dto["properties"][field]
            schema, nullable = unwrap(original, definitions)
            array = schema.get("type") == "array"
            if array:
                schema, _ = unwrap(schema["items"], definitions)
            name = (
                "immich"
                + class_name.removeprefix("Immich")
                + field[0].upper()
                + field[1:]
            )
            field_pointer = f"{pointer}/properties/{field}"
            required = field in dto.get("required", []) and not nullable
            terms = [f"sh:path :{name}"]
            if not array:
                terms.append("sh:maxCount 1")
            if required and "$ref" not in schema:
                # An empty required array is permitted unless minItems says otherwise.
                minimum = original.get("minItems", 0) if array else 1
                if minimum:
                    terms.append(f"sh:minCount {minimum}")
            if "$ref" in schema:
                target = POLICY[schema["$ref"].split("/")[-1]][0]
                terms.append(f"sh:class :{target}")
                ontology.append(
                    f":{name} a owl:ObjectProperty ; rdfs:domain :{class_name} ; rdfs:range :{target} ; prov:wasDerivedFrom <{source}{field_pointer}> .\n"
                )
                relations.append({"name": name, "target": target, "label": field})
                target_kind = target
            else:
                kind = schema.get("type")
                if kind == "string":
                    datatype = (
                        "dateTime" if schema.get("format") == "date-time" else "string"
                    )
                else:
                    datatype = {
                        "integer": "integer",
                        "number": "decimal",
                        "boolean": "boolean",
                    }[kind]
                target_kind = "xsd:" + datatype
                fields[name] = target_kind
                terms.append("sh:datatype " + target_kind)
                for keyword, predicate in (
                    ("minimum", "minInclusive"),
                    ("maximum", "maxInclusive"),
                ):
                    if keyword in schema:
                        terms.append(f"sh:{predicate} {schema[keyword]}")
                if "enum" in schema:
                    terms.append(
                        "sh:in ("
                        + " ".join(literal(item) for item in schema["enum"])
                        + ")"
                    )
                # Preserve exact UUID patterns. Other OpenAPI regex dialects are
                # not silently translated into SHACL/XPath regular expressions.
                if schema.get("format") == "uuid":
                    terms.append("sh:pattern " + literal(schema["pattern"]))
                ontology.append(
                    f":{name} a owl:DatatypeProperty ; rdfs:domain :{class_name} ; rdfs:range {target_kind} ; prov:wasDerivedFrom <{source}{field_pointer}> .\n"
                )
            shape_fields.append("[ " + " ; ".join(terms) + " ]")
            provenance.append(
                {
                    "class": class_name,
                    "property": name,
                    "source_pointer": field_pointer,
                    "range": target_kind,
                    "array": array,
                    "nullable": nullable,
                    "source_required": field in dto.get("required", []),
                    "presence_enforced": required and "$ref" not in schema,
                }
            )
        shapes.append(
            f":{class_name}Shape a sh:NodeShape ; sh:targetClass :{class_name} ;\n    sh:property "
            + ",\n    ".join(shape_fields)
            + " .\n"
        )
        resources.append({"name": class_name, "relations": relations})
        mappings[class_name] = {"ontology_class": class_name, "fields": fields}
    ontology_text, shapes_text = "\n".join(ontology), "\n".join(shapes)
    evidence = {
        "status": "schema-derived; live ingestion unverified",
        "source_version": "3.2.2",
        "source_sha256": SCHEMA_HASH,
        "contract_sha256": hashlib.sha256(
            (PACKAGE / "openapi_contract.json").read_bytes()
        ).hexdigest(),
        "properties": provenance,
        "excluded_by_policy": [
            "paths",
            "email",
            "EXIF",
            "GPS",
            "birth dates",
            "face geometry",
            "share keys/passwords",
            "credentials",
        ],
        "inferences_not_made": [
            "album contains assets",
            "person record equals a verified real-world person",
            "shared permission inherited by related objects",
        ],
    }
    return {
        PACKAGE / "ontology/immich.ttl": ontology_text,
        PACKAGE / "ontology/shapes/immich.ttl": shapes_text,
        PACKAGE / "ontology/schema-provenance.json": json.dumps(
            evidence, indent=2, sort_keys=True
        )
        + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in artifacts().items():
        if args.check:
            if not path.is_file() or path.read_text() != content:
                raise SystemExit(f"Stale content: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)


if __name__ == "__main__":
    main()
