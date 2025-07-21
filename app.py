import json
import os
from pathlib import Path
from fastmcp.server import FastMCP
from pydantic import BaseModel

RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP = {r["id"]: r for r in RECORDS}


class SearchResult(BaseModel):
    id: str
    title: str
    text: str


class SearchResultPage(BaseModel):
    results: list[SearchResult]


class FetchResult(BaseModel):
    id: str
    title: str
    text: str
    url: str | None = None
    metadata: dict[str, str] | None = None


def create_server():
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    @mcp.tool()
    async def search(query: str) -> SearchResultPage:
        """
        Search for cupcake orders – keyword match.

        Returns a SearchResultPage containing a list of SearchResult items.
        """
        tokens = query.lower().split()
        results: list[SearchResult] = []
        for r in RECORDS:
            hay = " ".join(
                [r.get("title", ""), r.get("text", ""), " ".join(r.get("metadata", {}).values())]
            ).lower()
            if any(t in hay for t in tokens):
                results.append(SearchResult(id=r["id"], title=r.get("title", ""), text=r.get("text", "")))

        return SearchResultPage(results=results)

    @mcp.tool()
    async def fetch(id: str) -> FetchResult:
        """
        Fetch a cupcake order by ID.

        Returns a FetchResult model.
        """
        if id not in LOOKUP:
            raise ValueError("unknown id")

        r = LOOKUP[id]
        return FetchResult(
            id=r["id"],
            title=r.get("title", ""),
            text=r.get("text", ""),
            url=r.get("url"),
            metadata=r.get("metadata"),
        )

    return mcp


server = create_server()
app = server.http_app(path="/mcp", transport="streamable-http")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
