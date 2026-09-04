"""
Multi-Provider LLM Wrapper Module.
Provides a unified, provider-agnostic interface for OpenAI, Groq, and Anthropic Claude.
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from openai import OpenAI
from src.config import Config

# Optional Anthropic import with graceful fallback
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "OpenAI"
    GROQ = "Groq"
    ANTHROPIC = "Anthropic"


@dataclass
class LLMResponse:
    """Standardized response dataclass across all LLM providers."""
    content: str
    model: str
    provider: str
    latency_seconds: float
    is_success: bool = True
    error_message: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    def __str__(self) -> str:
        return self.content


class LLMClient:
    """
    Unified LLM Client providing a single entry point to communicate
    with OpenAI, Groq, Anthropic Claude, and local endpoints.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        self.openai_key = openai_api_key if openai_api_key is not None else Config.OPENAI_API_KEY
        self.groq_key = groq_api_key if groq_api_key is not None else Config.GROQ_API_KEY
        self.anthropic_key = anthropic_api_key if anthropic_api_key is not None else Config.ANTHROPIC_API_KEY

        # Initialize clients lazily or directly
        self._openai_client: Optional[OpenAI] = None
        self._groq_client: Optional[OpenAI] = None
        self._anthropic_client: Optional[Any] = None

    @property
    def openai_client(self) -> OpenAI:
        """Returns initialized OpenAI client."""
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env file.")
        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=self.openai_key)
        return self._openai_client

    @property
    def groq_client(self) -> OpenAI:
        """Returns initialized Groq client (using OpenAI-compatible SDK)."""
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
        if self._groq_client is None:
            self._groq_client = OpenAI(
                api_key=self.groq_key,
                base_url=Config.GROQ_BASE_URL,
            )
        return self._groq_client

    @property
    def anthropic_client(self) -> Any:
        """Returns initialized Anthropic client."""
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package is not installed. Install via: pip install anthropic")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment or .env file.")
        if self._anthropic_client is None:
            self._anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        return self._anthropic_client

    def auto_detect_provider(self, model: str) -> LLMProvider:
        """Auto-detects the provider based on the model name."""
        model_lower = model.lower()
        if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
            return LLMProvider.OPENAI
        if "llama" in model_lower or "mixtral" in model_lower or "gemma" in model_lower:
            return LLMProvider.GROQ
        if "claude" in model_lower:
            return LLMProvider.ANTHROPIC
        # Default fallback
        return LLMProvider.OPENAI

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful, precise AI assistant. Respond in clear Markdown.",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        """
        Unified single-turn generation method.

        Args:
            prompt (str): The user's input prompt.
            system_prompt (str): Instructions defining AI persona and constraints.
            provider (str, optional): Target provider (OpenAI, Groq, Anthropic).
            model (str, optional): Specific model name.
            temperature (float): Sampling temperature (0.0 to 1.0).
            max_tokens (int): Maximum output tokens.

        Returns:
            LLMResponse: Formatted response object with content, timing, and metadata.
        """
        # Resolve target provider and model
        if provider:
            target_provider = LLMProvider(provider)
        elif model:
            target_provider = self.auto_detect_provider(model)
        else:
            target_provider = LLMProvider.OPENAI

        if not model:
            if target_provider == LLMProvider.OPENAI:
                model = Config.DEFAULT_OPENAI_MODEL
            elif target_provider == LLMProvider.GROQ:
                model = Config.DEFAULT_GROQ_MODEL
            elif target_provider == LLMProvider.ANTHROPIC:
                model = Config.DEFAULT_ANTHROPIC_MODEL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        return self.chat(
            messages=messages,
            provider=target_provider.value,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: str = "OpenAI",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        """
        Unified multi-turn chat completions across all providers.
        """
        start_time = time.perf_counter()
        target_provider = LLMProvider(provider)

        try:
            # 1. OpenAI Handler
            if target_provider == LLMProvider.OPENAI:
                target_model = model or Config.DEFAULT_OPENAI_MODEL
                resp = self.openai_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency = time.perf_counter() - start_time
                content = resp.choices[0].message.content or ""
                in_tok = resp.usage.prompt_tokens if resp.usage else None
                out_tok = resp.usage.completion_tokens if resp.usage else None

                return LLMResponse(
                    content=content,
                    model=target_model,
                    provider="OpenAI",
                    latency_seconds=round(latency, 3),
                    is_success=True,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                )

            # 2. Groq Handler (High speed, OpenAI compatible)
            elif target_provider == LLMProvider.GROQ:
                target_model = model or Config.DEFAULT_GROQ_MODEL
                resp = self.groq_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency = time.perf_counter() - start_time
                content = resp.choices[0].message.content or ""
                in_tok = resp.usage.prompt_tokens if resp.usage else None
                out_tok = resp.usage.completion_tokens if resp.usage else None

                return LLMResponse(
                    content=content,
                    model=target_model,
                    provider="Groq",
                    latency_seconds=round(latency, 3),
                    is_success=True,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                )

            # 3. Anthropic Claude Handler
            elif target_provider == LLMProvider.ANTHROPIC:
                target_model = model or Config.DEFAULT_ANTHROPIC_MODEL

                # Separate system prompt from conversational messages
                system_text = ""
                chat_messages = []
                for msg in messages:
                    if msg.get("role") == "system":
                        system_text += msg.get("content", "") + "\n"
                    else:
                        chat_messages.append({"role": msg.get("role"), "content": msg.get("content")})

                resp = self.anthropic_client.messages.create(
                    model=target_model,
                    system=system_text.strip() if system_text else "You are a helpful assistant.",
                    messages=chat_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency = time.perf_counter() - start_time
                content = resp.content[0].text if resp.content else ""
                in_tok = resp.usage.input_tokens if resp.usage else None
                out_tok = resp.usage.output_tokens if resp.usage else None

                return LLMResponse(
                    content=content,
                    model=target_model,
                    provider="Anthropic",
                    latency_seconds=round(latency, 3),
                    is_success=True,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                )

            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            latency = time.perf_counter() - start_time
            error_text = f"❌ [{provider} Error]: {str(e)}"
            return LLMResponse(
                content=error_text,
                model=model or "unknown",
                provider=provider,
                latency_seconds=round(latency, 3),
                is_success=False,
                error_message=str(e),
            )
