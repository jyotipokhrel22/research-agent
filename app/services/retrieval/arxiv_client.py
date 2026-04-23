import xml.etree.ElementTree as ET
from typing import List
import httpx
from httpx import HTTPStatusError

from app.schemas.paper import RetrievedPaper
from app.services.extraction.normalizer import clean_text, filter_papers


ARXIV_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _node_text(node, path: str) -> str | None:
    found = node.find(path, ATOM_NS)
    if found is None or found.text is None:
        return None
    return clean_text(found.text)


async def search_arxiv(
    topic: str,
    *,
    year: int | None = None,
    venue: str | None = None,
    limit: int = 10,
    timeout: int = 20,
) -> List[RetrievedPaper]:
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": min(max(limit * 2, limit), 20),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(ARXIV_URL, params=params)
            response.raise_for_status()
            root = ET.fromstring(response.text)
    except (HTTPStatusError, httpx.RequestError, ET.ParseError):
        return []

    papers: List[RetrievedPaper] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title = _node_text(entry, "atom:title")
        if not title:
            continue

        entry_id = _node_text(entry, "atom:id")
        published = _node_text(entry, "atom:published")
        paper_year = int(published[:4]) if published and len(published) >= 4 and published[:4].isdigit() else None
        authors = [
            clean_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        authors = [author for author in authors if author]

        pdf_url = None
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href")
                break

        papers.append(
            RetrievedPaper(
                source="arxiv",
                external_id=entry_id.rsplit("/", 1)[-1] if entry_id else None,
                title=title,
                abstract=_node_text(entry, "atom:summary"),
                authors=authors,
                year=paper_year,
                venue="arXiv",
                url=entry_id,
                pdf_url=pdf_url,
                citation_count=None,
            )
        )

    return filter_papers(papers, year=year, venue=venue)[:limit]
