# CONN-IMMICH-API — Quickstart

Scenario: serve the connector, read the packaged content, then confirm a write.

1. Run `uv run pytest tests/test_immich_content.py::test_native_prompt_skill_shapes_and_tool_discovery` to render prompts and skills through the production server (CONN-IMMICH-API-R004).
2. Run `uv run pytest tests/test_destructive_confirmation_transports.py` to see a client that cannot elicit refused cleanly and then confirmed with `confirm=true` (CONN-IMMICH-API-R009.3).
