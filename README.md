# 🚀 AI Engineering Projects Series · From Scratch to Production

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-brightgreen.svg)](https://platform.openai.com)
[![Groq LPU](https://img.shields.io/badge/Groq-Ultra--Fast_LPU-orange.svg)](https://console.groq.com)
[![Anthropic Claude](https://img.shields.io/badge/Anthropic-Claude--3.5-purple.svg)](https://console.anthropic.com)
[![Gradio Studio](https://img.shields.io/badge/UI-Gradio_Studio_Light-FF5722.svg)](https://gradio.app)
[![Pytest Suite](https://img.shields.io/badge/Tests-100%25_Mocked_Passing-0A9EDC.svg)](https://docs.pytest.org)
[![Security Protected](https://img.shields.io/badge/Security-.env_Protected-success.svg)](#-security--secret-protection)

Welcome to the **AI Engineering Projects Series**! This repository hosts production-ready, hands-on AI projects built from scratch. Each project is contained within its own dedicated directory.

---

## 📁 Projects Index

| # | Project Name | Key Skills & Tech Stack | Link |
| :-: | :--- | :--- | :-: |
| **01** | **AI Website Summarizer & Model Battle Arena** | Multi-Provider LLM Routing, DOM Noise Sanitizer, 6 Prompt Personas, Side-by-Side Model Arena, Pytest Mocking | [**Explore Project 01 ➔**](./01_AI_Website_Summarizer_and_Arena) |
| **02** | *Enterprise RAG Knowledge Assistant* | Vector Embeddings, Chunking Strategies, ChromaDB, Grounded Prompting | *(Coming Soon)* |
| **03** | *Autonomous AI Agents & Tool Calling* | JSON Schema Function Calling, Dynamic Tool Registry, ReAct Loops | *(Coming Soon)* |

---

## 🚀 Quickstart: Running Project 01

### 1. Enter Project 01 Folder
```bash
cd 01_AI_Website_Summarizer_and_Arena
```

### 2. Set Up Virtual Environment & Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and fill in your keys:
```powershell
copy .env.example .env
```

### 4. Launch the Web Application
```bash
python app.py
```
Open **`http://127.0.0.1:7860`** in your browser.

### 5. Run Unit Tests (Zero Token Cost)
```bash
python -m pytest tests/ -v
```

---

## 🔐 Security & Secret Protection
- Real API keys are strictly loaded via `.env` files.
- Root `.gitignore` shields all `.env` files, `.venv`, and cache from ever being pushed to GitHub.

---

## 📜 License
MIT License — Feel free to use, modify, and build upon these projects.
