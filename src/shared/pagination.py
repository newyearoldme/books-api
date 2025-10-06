from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(
        default=10, ge=0, le=100, description="Number of records to return (1-100)"
    )
    skip: int = Field(default=0, ge=0, description="Number of records to skip (min 0)")


PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
