"""
LLM Battle Arena Module.
Enables side-by-side model benchmarking, response timing, and voting.
"""

from typing import Any, Dict, Optional, Tuple
from src.llm_wrapper import LLMClient, LLMResponse


class LLMArena:
    """
    Manages head-to-head battles between two AI models.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.client = llm_client or LLMClient()
        self.vote_history: list = []

    def battle(
        self,
        prompt: str,
        provider_a: str = "OpenAI",
        model_a: str = "gpt-4o-mini",
        provider_b: str = "Groq",
        model_b: str = "llama-3.3-70b-versatile",
        system_prompt: str = "You are a helpful, witty, and concise AI assistant.",
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Sends the same prompt to both Model A and Model B.

        Returns:
            Tuple of results: (result_a, result_b)
        """
        # Execute Model A
        resp_a: LLMResponse = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=provider_a,
            model=model_a,
        )

        # Execute Model B
        resp_b: LLMResponse = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=provider_b,
            model=model_b,
        )

        result_a = {
            "content": resp_a.content,
            "provider": resp_a.provider,
            "model": resp_a.model,
            "latency": resp_a.latency_seconds,
            "is_success": resp_a.is_success,
            "metadata": f"⏱️ **{resp_a.latency_seconds}s** | Provider: `{resp_a.provider}` | Model: `{resp_a.model}`",
        }

        result_b = {
            "content": resp_b.content,
            "provider": resp_b.provider,
            "model": resp_b.model,
            "latency": resp_b.latency_seconds,
            "is_success": resp_b.is_success,
            "metadata": f"⏱️ **{resp_b.latency_seconds}s** | Provider: `{resp_b.provider}` | Model: `{resp_b.model}`",
        }

        return result_a, result_b

    def record_vote(self, winner: str, prompt: str, model_a_label: str, model_b_label: str) -> str:
        """
        Records a user vote between Model A and Model B.
        """
        record = {
            "winner": winner,
            "prompt": prompt,
            "model_a": model_a_label,
            "model_b": model_b_label,
        }
        self.vote_history.append(record)
        return f"🗳️ **Vote Recorded!** You chose: **{winner}** (Total votes logged: {len(self.vote_history)})"
