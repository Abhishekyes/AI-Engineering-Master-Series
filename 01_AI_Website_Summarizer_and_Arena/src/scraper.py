"""
Web Scraper Module.
Fetches and sanitizes HTML content from any URL for LLM processing.
"""

import requests
from bs4 import BeautifulSoup
from src.config import Config


def fetch_website_contents(url: str, max_chars: int = Config.SCRAPER_MAX_CHARS) -> str:
    """
    Fetches clean, readable text content from a given web URL.

    Args:
        url (str): The URL of the target web page.
        max_chars (int): Maximum length of returned text content.

    Returns:
        str: Extracted Title and clean text body ready for an LLM prompt.
    """
    if not url or not isinstance(url, str):
        return "Error: Invalid or empty URL provided."

    url = url.strip()

    # Automatically prepend scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            headers=Config.DEFAULT_HEADERS,
            timeout=Config.SCRAPER_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return f"Error: Request timed out after {Config.SCRAPER_TIMEOUT} seconds when fetching {url}."
    except requests.exceptions.SSLError:
        return f"Error: SSL Certificate verification failed for {url}."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not fetch website contents. Details: {e}"

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract page title
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"

        # Remove irrelevant non-content elements
        noise_tags = [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
            "svg",
            "form",
            "iframe",
            "aside",
            "button",
            "dialog",
        ]
        for tag in soup(noise_tags):
            tag.decompose()

        # Extract text separated by newlines
        body_text = soup.get_text(separator="\n", strip=True)

        # Condense multiple empty lines
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Truncate if content is excessively long
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "\n\n...[Content truncated for length]..."

        if not clean_text:
            return f"Title: {title}\n\nNotice: No readable text content found on the page."

        return f"Title: {title}\n\nPage Contents:\n{clean_text}"

    except Exception as e:
        return f"Error parsing HTML content from {url}: {e}"
