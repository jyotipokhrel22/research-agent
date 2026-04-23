import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PaperSearchRequest(BaseModel):
    topic: str = Field(..., examples=["multi agent rl"])
    year: Optional[str] = Field(default=None, examples=["2025", "2023-2026"])
    venue: Optional[str] = Field(default=None, examples=["NeurIPS", "ICLR"])
    max_results: int = Field(default=10, examples=[10])

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Topic must be at least 3 characters")
        return value

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()
        if not value:
            return None

        exact_match = re.fullmatch(r"\d{4}", value)
        range_match = re.fullmatch(r"(\d{4})\s*-\s*(\d{4})", value)

        if exact_match:
            if int(value) < 1:
                raise ValueError("year must be a positive integer")
            return value

        if range_match:
            start_year = int(range_match.group(1))
            end_year = int(range_match.group(2))
            if start_year < 1 or end_year < 1:
                raise ValueError("year range must contain positive integers")
            if start_year > end_year:
                raise ValueError("year range start must be less than or equal to end")
            return f"{start_year}-{end_year}"

        raise ValueError("year must be a 4 digit year or a range like 2023-2026")

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, value: int) -> int:
        if value < 1 or value > 20:
            raise ValueError("max_results must be between 1 and 20")
        return value


class RetrievedPaper(BaseModel):
    source: str
    external_id: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    citation_count: Optional[int] = None


class PaperSearchResponse(BaseModel):
    topic: str
    filters: dict
    sources_used: List[str]
    count: int
    papers: List[RetrievedPaper]
