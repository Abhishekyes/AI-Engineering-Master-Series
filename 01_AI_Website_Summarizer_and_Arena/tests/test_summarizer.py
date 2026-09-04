"""
Unit Tests for Website Summarizer Module.
Tests end-to-end integration between scraper, prompt formatting, and LLM generation.
"""

from unittest.mock import patch, MagicMock
from src.summarizer import WebsiteSummarizer, SUMMARY_PERSONALITIES
from src.llm_wrapper import LLMClient, LLMResponse


@patch("src.summarizer.fetch_website_contents")
def test_summarizer_success_flow(mock_fetch):
    """Test successful summarization with custom tone and metadata generation."""
    mock_fetch.return_value = "Title: Sample Web\n\nPage Contents: We build amazing AI apps."

    mock_llm_client = MagicMock(spec=LLMClient)
    mock_llm_client.generate.return_value = LLMResponse(
        content="## Sample Web Summary\n- Builds AI apps.",
        model="gpt-4o-mini",
        provider="OpenAI",
        latency_seconds=0.45,
        is_success=True,
    )

    summarizer = WebsiteSummarizer(llm_client=mock_llm_client)
    res = summarizer.summarize(
        url="https://sample.ai",
        personality="💼 Executive Brief (TL;DR for Leaders)",
        provider="OpenAI",
        model="gpt-4o-mini",
    )

    assert res["is_success"] is True
    assert "Sample Web Summary" in res["summary"]
    assert "0.45s" in res["metadata"]
    assert "OpenAI" in res["metadata"]

    # Verify LLMClient was called with executive prompt instructions
    call_args = mock_llm_client.generate.call_args[1]
    assert "Executive" in call_args["system_prompt"] or "Chief of Staff" in call_args["system_prompt"]


@patch("src.summarizer.fetch_website_contents")
def test_summarizer_scraping_error_flow(mock_fetch):
    """Test summarizer behavior when scraper encounters a failure."""
    mock_fetch.return_value = "Error: Request timed out after 15 seconds."

    mock_llm_client = MagicMock(spec=LLMClient)
    summarizer = WebsiteSummarizer(llm_client=mock_llm_client)

    res = summarizer.summarize(url="https://timedout-site.com")

    assert res["is_success"] is False
    assert "Error: Request timed out" in res["summary"]
    # LLM should not be called if scraping failed
    mock_llm_client.generate.assert_not_called()
