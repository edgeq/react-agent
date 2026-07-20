from ddgs import DDGS
from agent.tools.registry import tool

@tool
def web_search(query: str, max_results: int = 5):
    """Does a text search using the DuckDuckGo search service"""
    with DDGS() as ddgs:
        search = ddgs.text(query, max_results=max_results)
        formatted_results = []
        for result in search:
            title = result.get("title", "No Title")
            url = result.get("href", "No URL")
            snippet = result.get("body", "No Snippet")
            formatted_results.append(
                f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n--"
            )

    return "\n\n".join(formatted_results)
