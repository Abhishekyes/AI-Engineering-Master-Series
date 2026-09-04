"""
Script 01: First OpenAI Call
--------------------------------------------------
Demonstrates loading credentials securely from .env
and executing your first chat completion with OpenAI.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI
from dotenv import load_dotenv

# Step 1: Load environment variables from .env
load_dotenv()

# Step 2: Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env file! Please copy .env.example to .env and add your key.")

client = OpenAI(api_key=api_key)

print("🚀 Sending request to OpenAI (gpt-4o-mini)...")

# Step 3: Create chat completion
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a witty AI tutor welcoming a student to AI Engineering."},
        {"role": "user", "content": "Give me a high-energy 2-sentence welcome message!"},
    ],
    temperature=0.7,
)

# Step 4: Output response
print("\n" + "=" * 50)
print("🤖 OpenAI Response:")
print("=" * 50)
print(response.choices[0].message.content)
print("=" * 50)
