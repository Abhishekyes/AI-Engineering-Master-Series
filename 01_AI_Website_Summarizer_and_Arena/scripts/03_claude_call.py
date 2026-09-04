"""
Script 03: Anthropic Claude Call
--------------------------------------------------
Demonstrates calling Anthropic Claude 3.5 Sonnet
using the official anthropic SDK.
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# Step 1: Load environment variables
load_dotenv()

claude_key = os.getenv("ANTHROPIC_API_KEY")
if not claude_key or claude_key.startswith("sk-ant-your_"):
    print("ℹ️ Note: ANTHROPIC_API_KEY is not configured in .env yet.")
    print("Get your API key at: https://console.anthropic.com/settings/keys")
    exit(0)

try:
    import anthropic
except ImportError:
    print("⚠️ Please install the anthropic package: pip install anthropic")
    exit(1)

client = anthropic.Anthropic(api_key=claude_key)

print("🧠 Sending request to Anthropic (claude-3-5-sonnet-20241022)...")
start_time = time.perf_counter()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=300,
    system="You are an expert AI software architect.",
    messages=[
        {"role": "user", "content": "What is the key advantage of modular LLM wrapper architectures? Answer in 2 crisp sentences."},
    ],
)

elapsed = time.perf_counter() - start_time

print("\n" + "=" * 50)
print(f"🧠 Claude Response (Latency: {elapsed:.3f}s):")
print("=" * 50)
print(response.content[0].text)
print("=" * 50)
