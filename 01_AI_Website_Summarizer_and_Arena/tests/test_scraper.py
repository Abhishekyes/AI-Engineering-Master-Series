"""
Unit Tests for Web Scraper Module.
Tests HTML sanitization, tag stripping, and error handling without making external network calls.
"""

from unittest.mock import patch, MagicMock
import requests
from src.scraper import fetch_website_contents


def test_empty_url_handling():
    """Test that empty or None URLs return appropriate error strings."""
    assert "Invalid or empty URL" in fetch_website_contents("")
    assert "Invalid or empty URL" in fetch_website_contents(None)  # type: ignore


@patch("src.scraper.requests.get")
def test_successful_scraping_and_tag_stripping(mock_get):
    """Test HTML parsing and removal of script, style, nav, and footer tags."""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python Software Foundation</title>
        <style>body { background: red; }</style>
        <script>alert('malicious script');</script>
    </head>
    <body>
        <nav><a href="/home">Home</a><a href="/about">About</a></nav>
        <header><h1>Welcome to Python</h1></header>
        <main>
            <p>Python is a powerful programming language that lets you work quickly.</p>
            <p>It supports multiple paradigms including object-oriented and functional.</p>
        </main>
        <footer><p>Copyright 2026 PSF</p></footer>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = sample_html
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = fetch_website_contents("python.org")

    # Assertions
    assert "Title: Python Software Foundation" in result
    assert "Python is a powerful programming language" in result
    assert "object-oriented and functional" in result
    # Assert noise tags were stripped
    assert "alert('malicious script')" not in result
    assert "background: red" not in result
    assert "Copyright 2026 PSF" not in result


@patch("src.scraper.requests.get")
def test_http_timeout_handling(mock_get):
    """Test graceful handling of network timeouts."""
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out.")
    result = fetch_website_contents("https://slow-site.com")
    assert "Error: Request timed out" in result


@patch("src.scraper.requests.get")
def test_http_404_error_handling(mock_get):
    """Test graceful handling of HTTP errors like 404 Not Found."""
    mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found")
    result = fetch_website_contents("https://non-existent-site.com")
    assert "Error: Could not fetch website contents" in result
