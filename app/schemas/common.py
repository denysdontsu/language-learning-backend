from pydantic import BaseModel, Field


class Options(BaseModel):
    """Answer options for multiple choice exercises."""
    A: str = Field(min_length=1)
    B: str = Field(min_length=1)
    C: str | None = Field(None, min_length=1)
    D: str | None = Field(None, min_length=1)