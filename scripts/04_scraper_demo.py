"""
Script 04: Web Scraper Standalone Demo
--------------------------------------------------
Demonstrates scraping and stripping clean text from any URL.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scraper import fetch_website_contents

target_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.python.org"

print(f"🕷️ Scraping website: {target_url} ...\n")
result = fetch_website_contents(target_url)

print("=" * 60)
print(result[:1500])
if len(result) > 1500:
    print(f"\n... [Truncated: Total length {len(result)} characters] ...")
print("=" * 60)
