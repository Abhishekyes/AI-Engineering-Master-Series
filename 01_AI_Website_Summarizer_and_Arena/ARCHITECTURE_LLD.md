# 📐 Low-Level Design (LLD): Multi-Provider AI Summarizer & Arena

**Project**: Multi-Provider LLM Wrapper, Anti-Scrape Web Sanitizer & Model Battle Arena  
**Version**: 1.0.0 · Production Architecture  
**Author**: AI Engineering Series

---

## 1. Class Diagram (UML)

```mermaid
classDiagram
    class LLMProvider {
        <<enumeration>>
        OPENAI: "OpenAI"
        GROQ: "Groq"
        ANTHROPIC: "Anthropic"
    }

    class LLMResponse {
        +str content
        +str model
        +str provider
        +float latency_seconds
        +bool is_success
        +str error_message
        +int input_tokens
        +int output_tokens
        +__str__() str
    }

    class Config {
        +str OPENAI_API_KEY$
        +str GROQ_API_KEY$
        +str ANTHROPIC_API_KEY$
        +str GROQ_BASE_URL$
        +str DEFAULT_OPENAI_MODEL$
        +str DEFAULT_GROQ_MODEL$
        +str DEFAULT_ANTHROPIC_MODEL$
        +dict AVAILABLE_MODELS$
        +int SCRAPER_TIMEOUT$
        +int SCRAPER_MAX_CHARS$
        +dict DEFAULT_HEADERS$
        +get_active_providers() list$
    }

    class LLMClient {
        -str openai_key
        -str groq_key
        -str anthropic_key
        -OpenAI _openai_client
        -OpenAI _groq_client
        -Anthropic _anthropic_client
        +openai_client() OpenAI
        +groq_client() OpenAI
        +anthropic_client() Any
        +auto_detect_provider(model: str) LLMProvider
        +generate(prompt, system_prompt, provider, model, temperature, max_tokens) LLMResponse
        +chat(messages, provider, model, temperature, max_tokens) LLMResponse
    }

    class WebsiteSummarizer {
        -LLMClient client
        +summarize(url, personality, provider, model, custom_instructions) dict
    }

    class LLMArena {
        -LLMClient client
        +list vote_history
        +battle(prompt, provider_a, model_a, provider_b, model_b, system_prompt) tuple
        +record_vote(winner, prompt, model_a_label, model_b_label) str
    }

    class ScraperModule {
        <<module>>
        +fetch_website_contents(url: str, max_chars: int) str
    }

    LLMClient ..> LLMProvider : uses
    LLMClient ..> LLMResponse : produces
    LLMClient ..> Config : reads
    WebsiteSummarizer --> LLMClient : delegates inference
    WebsiteSummarizer ..> ScraperModule : calls fetch_website_contents
    LLMArena --> LLMClient : delegates battles
```

---

## 2. Sequence Diagrams

### 2.1 Website Scraping & Summarization Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User / Gradio UI
    participant App as 🖥️ app.py / handle_summarize
    participant Sum as 🎭 WebsiteSummarizer
    participant Scrap as 🕷️ fetch_website_contents
    participant Client as 🔄 LLMClient
    participant ExtAPI as ☁️ Groq / OpenAI API

    User->>App: Submits URL + selects Persona
    App->>Sum: summarize(url, personality, provider, model)
    
    Sum->>Scrap: fetch_website_contents(url)
    Scrap->>Scrap: Send HTTP GET with Headers
    Scrap->>Scrap: BeautifulSoup.decompose(["script", "style", "nav", "footer"])
    Scrap-->>Sum: Returns clean markdown string
    
    Sum->>Sum: Lookup personality system prompt template
    Sum->>Client: generate(prompt, system_prompt, provider, model)
    
    Client->>Client: Start latency timer (time.perf_counter)
    Client->>ExtAPI: chat.completions.create(...)
    ExtAPI-->>Client: Returns completion response & token metrics
    Client->>Client: Compute elapsed latency (round(s, 3))
    Client-->>Sum: Returns standardized LLMResponse dataclass
    
    Sum-->>App: Returns {summary, metadata, is_success}
    App-->>User: Renders Markdown Output + Latency Badge
```

---

### 2.2 LLM Battle Arena & Voting Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User / Gradio UI
    participant Arena as 🥊 LLMArena
    participant Client as 🔄 LLMClient
    participant ModelA as 🤖 Model A (OpenAI)
    participant ModelB as ⚡ Model B (Groq LPU)

    User->>Arena: battle(prompt, prov_a, mod_a, prov_b, mod_b)
    
    par Concurrent/Sequential Dispatch to Model A
        Arena->>Client: generate(prompt, prov="OpenAI", mod="gpt-4o-mini")
        Client->>ModelA: chat.completions.create(...)
        ModelA-->>Client: Response A payload
        Client-->>Arena: LLMResponse A (Latency: 1.25s)
    and Dispatch to Model B
        Arena->>Client: generate(prompt, prov="Groq", mod="llama-3.3-70b")
        Client->>ModelB: chat.completions.create(...)
        ModelB-->>Client: Response B payload
        Client-->>Arena: LLMResponse B (Latency: 0.28s)
    end

    Arena-->>User: Renders Side-by-Side Outputs + Speed Metrics
    
    User->>Arena: record_vote("Contender B", prompt, mod_a, mod_b)
    Arena->>Arena: Append vote record to vote_history[]
    Arena-->>User: Displays confirmation badge with total votes logged
```

---

## 3. Detailed Component Specifications

### 3.1 `LLMResponse` (Dataclass)
```python
@dataclass
class LLMResponse:
    content: str                  # Generated markdown/text
    model: str                    # Target model string (e.g. gpt-4o-mini)
    provider: str                 # Provider name (OpenAI, Groq, Anthropic)
    latency_seconds: float        # Execution round-trip time in seconds
    is_success: bool = True       # Boolean flag indicating execution status
    error_message: Optional[str]  # Error traceback / details if is_success is False
    input_tokens: Optional[int]   # Prompt token count
    output_tokens: Optional[int]  # Completion token count
```

### 3.2 `fetch_website_contents(url: str, max_chars: int) -> str`
- **Algorithm**:
  1. Validate URL scheme (`http://` or `https://`). Auto-prepend `https://` if absent.
  2. Perform HTTP `GET` with spoofed User-Agent (`timeout=15s`).
  3. Parse DOM tree using `BeautifulSoup(html, "html.parser")`.
  4. Decompose noisy nodes: `["script", "style", "nav", "footer", "header", "noscript", "svg", "form", "iframe", "aside", "button"]`.
  5. Extract stripped text lines and collapse duplicate newlines.
  6. Truncate text at `max_chars` limit (`25,000` chars default).

---

## 4. Design Patterns Implemented

| Pattern | Where Applied | Purpose |
| :--- | :--- | :--- |
| **Facade Pattern** | `src/llm_wrapper.py::LLMClient` | Simplifies complex multi-SDK protocols into a single `.generate()` method. |
| **Adapter Pattern** | `LLMClient.chat()` | Adapts disparate API schemas (OpenAI vs Anthropic message formats) into a unified interface. |
| **Strategy Pattern** | `src/summarizer.py::SUMMARY_PERSONALITIES` | Allows dynamic interchangeable prompt behaviors at runtime. |
| **Singleton / Registry** | `src/config.py::Config` | Provides centralized, immutable access to environment configurations and model lists. |

---

## 5. Error Handling & Recovery Matrix

| Scenario | System Behavior | User Impact |
| :--- | :--- | :--- |
| **Invalid URL or 404** | Scraper catches `RequestException`, returns structured error string. | Clean warning message rendered; no uncaught exceptions. |
| **Scraper Timeout (>15s)** | Scraper catches `Timeout`, returns timeout notice. | User alerted that target website is unresponsive. |
| **Missing API Key** | Wrapper raises `ValueError`, catches in `.generate()`, sets `is_success=False`. | UI displays error badge explaining how to configure `.env`. |
| **Provider Rate Limit / Outage** | LLM client catches exception, sets `is_success=False`, returns latency metrics. | App does not crash; other provider in Arena continues functioning. |
