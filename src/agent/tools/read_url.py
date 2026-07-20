import httpx
from bs4 import BeautifulSoup
import markdownify
from agent.tools import tool

@tool
def read_url(url: str) -> str:
    """Reads a URL and returns clean markdown"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        page = httpx.get(url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, "html.parser")

        # Get rid of non-content elements
        for element in soup(["script", "style", "header", "footer", "nav", "form"]):
            element.decompose()

        markdown_text = markdownify.markdownify(str(soup))
        cleaned_markdown = "\n".join(
            line for line in markdown_text.splitlines() if line.strip()
        )
        if len(cleaned_markdown) > 4000:
            return cleaned_markdown[:4000] + "\n\n[Content truncated to 4000 characters]"
        return cleaned_markdown
    except Exception as e:
        return f"Error fetching URL: {str(e)}"
