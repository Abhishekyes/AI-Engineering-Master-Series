"""
Script 05: CLI Website Summarizer
--------------------------------------------------
Runs the complete scraping and AI summarization pipeline
directly from your terminal.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.summarizer import WebsiteSummarizer, SUMMARY_PERSONALITIES

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://news.ycombinator.com"
    tone_key = list(SUMMARY_PERSONALITIES.keys())[0]

    print("=" * 60)
    print(f"🔎 AI Website Summarizer (CLI Mode)")
    print(f"🌐 Target: {url}")
    print(f"🎭 Tone: {tone_key}")
    print("=" * 60)
    print("⏳ Scraping & Summarizing (calling LLM)...")

    summarizer = WebsiteSummarizer()
    result = summarizer.summarize(url=url, personality=tone_key, provider="OpenAI")

    print("\n" + result["summary"])
    print("\n" + "-" * 60)
    print(result["metadata"])
    print("=" * 60)

if __name__ == "__main__":
    main()
