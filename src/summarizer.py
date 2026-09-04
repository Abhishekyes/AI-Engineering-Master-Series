"""
Website Summarizer Module.
Combines web scraping with customizable prompt engineering and multi-LLM generation.
"""

from typing import Dict, Optional
from src.scraper import fetch_website_contents
from src.llm_wrapper import LLMClient, LLMResponse

# Curated Prompt Personalities
SUMMARY_PERSONALITIES: Dict[str, str] = {
    "🎯 Standard (Professional & Balanced)": (
        "You are an expert content curator. Analyze the contents of the given website "
        "and provide a structured, crystal-clear summary in markdown.\n"
        "Include:\n"
        "- 📌 **Overview**: 1-2 sentence core premise\n"
        "- 🔑 **Key Highlights**: 3-5 distinct bullet points\n"
        "- 💡 **Why It Matters / Audience**: Who is this for?"
    ),
    "💼 Executive Brief (TL;DR for Leaders)": (
        "You are an executive Chief of Staff. Deliver an ultra-dense, actionable briefing "
        "of this website for a C-suite executive with zero fluff.\n"
        "Structure with:\n"
        "- **Core Value Proposition**\n"
        "- **Key Strategic Takeaways**\n"
        "- **Risks / Opportunities**"
    ),
    "🧸 Explain Like I'm 5 (ELI5)": (
        "You are a friendly, enthusiastic teacher. Explain what this website is about to a 5-year-old. "
        "Use simple words, fun analogies, and short sentences. Avoid jargon entirely!"
    ),
    "🔥 Snarky & Humorous": (
        "You are a witty, mildly sarcastic tech reviewer. Give a punchy, humorous, "
        "yet surprisingly accurate breakdown of this website. Roast buzzwords lightly while staying informative."
    ),
    "💻 Developer & Tech Digest": (
        "You are a senior software architect. Summarize this website focusing on technical aspects: "
        "core engineering concepts, tech stack, APIs, architecture, developer tools, and capabilities."
    ),
    "🇮🇳 Hindi / Hinglish Summary": (
        "Aap ek friendly AI assistant hain. Di gayi website ka summary clear Hinglish (Hindi + English) "
        "mein dijiye taaki koi bhi easily samajh sake. Main points ko bullet format mein explain kijiye."
    ),
}


class WebsiteSummarizer:
    """
    Website Summarizer powered by LLMClient.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.client = llm_client or LLMClient()

    def summarize(
        self,
        url: str,
        personality: str = "🎯 Standard (Professional & Balanced)",
        provider: str = "OpenAI",
        model: Optional[str] = None,
        custom_instructions: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Scrapes a URL and generates an AI summary using the selected tone and provider.

        Returns:
            dict containing summary markdown and operational metadata.
        """
        # Step 1: Scrape website text
        scraped_text = fetch_website_contents(url)
        if scraped_text.startswith("Error:"):
            return {
                "summary": scraped_text,
                "metadata": "❌ Failed during scraping phase.",
                "is_success": False,
            }

        # Step 2: Formulate prompt
        system_prompt = SUMMARY_PERSONALITIES.get(personality, SUMMARY_PERSONALITIES["🎯 Standard (Professional & Balanced)"])
        if custom_instructions and custom_instructions.strip():
            system_prompt += f"\n\nAdditional user guidelines:\n{custom_instructions.strip()}"

        user_prompt = f"Please analyze and summarize the following website contents:\n\n{scraped_text}"

        # Step 3: Run LLM Inference
        resp: LLMResponse = self.client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
        )

        if not resp.is_success:
            return {
                "summary": resp.content,
                "metadata": f"❌ Generation failed via {resp.provider} ({resp.model})",
                "is_success": False,
            }

        meta_info = f"⚡ *Generated in {resp.latency_seconds}s using **{resp.provider} ({resp.model})***"
        return {
            "summary": resp.content,
            "metadata": meta_info,
            "is_success": True,
        }
