"""
Script 02: Groq High-Speed LLM Call
--------------------------------------------------
Demonstrates calling open models (Meta Llama 3.3 70B)
via Groq's blazing-fast OpenAI-compatible API.
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI
from dotenv import load_dotenv

# Step 1: Load environment variables
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("Missing GROQ_API_KEY in .env file! Sign up free at https://console.groq.com")

# Step 2: Point OpenAI client to Groq base_url
client = OpenAI(
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1",
)

# Step 3: Call Groq
target_model = os.getenv("GROQ_DEFAULT_MODEL", "openai/gpt-oss-120b")
print(f"⚡ Sending request to Groq ({target_model})...")
start_time = time.perf_counter()

response = client.chat.completions.create(
    model=target_model,
    messages=[
        {"role": "system", "content": "You are a witty, ultra-fast AI assistant."},
        {"role": "user", "content": "Why is Groq LPUs so fast compared to traditional GPUs? Explain in 2 sentences."},
    ],
)

elapsed = time.perf_counter() - start_time

# Step 4: Display output and latency
print("\n" + "=" * 50)
print(f"⚡ Groq Response (Latency: {elapsed:.3f}s):")
print("=" * 50)
print(response.choices[0].message.content)
print("=" * 50)
