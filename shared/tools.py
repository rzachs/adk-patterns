import os
import requests


def web_search(query: str) -> dict:
    """Search the web for current information on a query.

    Args:
        query: The search query string.

    Returns:
        Success: {"results": [{"title": ..., "snippet": ..., "link": ...}, ...]}
        Error: {"error": "..."}
    """
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not set"}
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query},
            timeout=10,
        )
        resp.raise_for_status()
        organic = resp.json().get("organic", [])
        return {
            "results": [
                {"title": r["title"], "snippet": r.get("snippet", ""), "link": r["link"]}
                for r in organic[:5]
            ]
        }
    except requests.RequestException as e:
        return {"error": str(e)}
