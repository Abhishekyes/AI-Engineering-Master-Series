"""
Unit Tests for LLM Wrapper Module.
Tests provider auto-detection, response standardization, and mocked generations.
"""

from unittest.mock import MagicMock, patch
from src.llm_wrapper import LLMClient, LLMProvider, LLMResponse


def test_provider_auto_detection():
    """Test accurate provider detection from model names."""
    client = LLMClient(openai_api_key="test_key", groq_api_key="test_key")
    
    assert client.auto_detect_provider("gpt-4o-mini") == LLMProvider.OPENAI
    assert client.auto_detect_provider("gpt-4o") == LLMProvider.OPENAI
    assert client.auto_detect_provider("llama-3.3-70b-versatile") == LLMProvider.GROQ
    assert client.auto_detect_provider("mixtral-8x7b-32768") == LLMProvider.GROQ
    assert client.auto_detect_provider("claude-3-5-sonnet-20241022") == LLMProvider.ANTHROPIC


@patch("src.llm_wrapper.OpenAI")
def test_openai_generate_mock(mock_openai_cls):
    """Test OpenAI generation flow using mock client."""
    # Setup mock response
    mock_instance = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a mocked OpenAI response."
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 15
    mock_usage.completion_tokens = 25

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp.usage = mock_usage

    mock_instance.chat.completions.create.return_value = mock_resp
    mock_openai_cls.return_value = mock_instance

    client = LLMClient(openai_api_key="mock_key")
    response: LLMResponse = client.generate(
        prompt="Hello AI!",
        provider="OpenAI",
        model="gpt-4o-mini",
    )

    assert response.is_success is True
    assert response.content == "This is a mocked OpenAI response."
    assert response.provider == "OpenAI"
    assert response.model == "gpt-4o-mini"
    assert response.latency_seconds >= 0.0
    assert response.input_tokens == 15
    assert response.output_tokens == 25


@patch("src.llm_wrapper.OpenAI")
def test_groq_generate_mock(mock_openai_cls):
    """Test Groq generation flow using mock OpenAI client with Groq base URL."""
    mock_instance = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "⚡ Blazing fast Llama response from Groq!"
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp.usage = None

    mock_instance.chat.completions.create.return_value = mock_resp
    mock_openai_cls.return_value = mock_instance

    client = LLMClient(groq_api_key="mock_groq_key")
    response: LLMResponse = client.generate(
        prompt="Why Groq?",
        provider="Groq",
        model="llama-3.3-70b-versatile",
    )

    assert response.is_success is True
    assert response.content == "⚡ Blazing fast Llama response from Groq!"
    assert response.provider == "Groq"
    assert response.model == "llama-3.3-70b-versatile"


def test_error_handling_graceful_recovery():
    """Test that API errors do not crash the application and return structured failure responses."""
    client = LLMClient(openai_api_key="", groq_api_key="")
    response = client.generate(prompt="Test with no keys", provider="OpenAI")

    assert response.is_success is False
    assert "Error" in response.content or "OPENAI_API_KEY is not set" in response.content
