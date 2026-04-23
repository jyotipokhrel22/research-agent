import os
from typing import List

import httpx
from dotenv import load_dotenv
from httpx import HTTPStatusError

from app.schemas.paper import RetrievedPaper
from app.services.extraction.normalizer import clean_text, filter_papers


load_dotenv()

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_FIELDS = ",".join(
    [
        "paperId",
        "title",
        "abstract",
        "authors",
        "year",
        "venue",
        "publicationVenue",
        "journal",
        "url",
        "citationCount",
        "openAccessPdf",
    ]
)


def _query_with_venue(topic: str, venue: str | None) -> str:
    cleaned_topic = clean_text(topic) or topic
    cleaned_venue = clean_text(venue)
    if not cleaned_venue:
        return cleaned_topic
    return f"{cleaned_topic} {cleaned_venue}"


def _extract_venue(item: dict) -> str | None:
    publication_venue = item.get("publicationVenue") or {}
    journal = item.get("journal") or {}
    return clean_text(
        item.get("venue")
        or publication_venue.get("name")
        or journal.get("name")
    )


async def search_semantic_scholar(
    topic: str,
    *,
    year: int | None = None,
    venue: str | None = None,
    limit: int = 10,
    timeout: int = 20,
) -> List[RetrievedPaper]:
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": _query_with_venue(topic, venue),
        "limit": min(max(limit * 5, limit), 50),
        "fields": SEMANTIC_SCHOLAR_FIELDS,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(SEMANTIC_SCHOLAR_URL, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except (HTTPStatusError, httpx.RequestError):
        return []

    papers: List[RetrievedPaper] = []
    for item in payload.get("data", []):
        title = clean_text(item.get("title"))
        if not title:
            continue

        authors = [author.get("name", "").strip() for author in item.get("authors", []) if author.get("name")]
        pdf = item.get("openAccessPdf") or {}

        papers.append(
            RetrievedPaper(
                source="semantic_scholar",
                external_id=item.get("paperId"),
                title=title,
                abstract=clean_text(item.get("abstract")),
                authors=authors,
                year=item.get("year"),
                venue=_extract_venue(item),
                url=item.get("url"),
                pdf_url=pdf.get("url"),
                citation_count=item.get("citationCount"),
            )
        )

    return filter_papers(papers, year=year, venue=venue)[:limit]
