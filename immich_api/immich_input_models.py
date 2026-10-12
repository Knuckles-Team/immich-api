#!/usr/bin/python
"""Pydantic input models for Immich Api API request parameters."""

from typing import Optional

from pydantic import BaseModel, Field


class SystemStatusInput(BaseModel):
    """Input model for system status queries."""

    verbose: Optional[bool] = Field(
        default=False, description="Return extended status details."
    )
