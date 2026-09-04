"""
==============================================================================
🌌 AI ENGINEERING MASTER SERIES · CENTRAL PORTAL & APP
Class 01: Multi-Provider LLM Wrapper, Anti-Scrape Summarizer & Model Arena
==============================================================================
"""

import time
import gradio as gr
from src.config import Config
from src.summarizer import WebsiteSummarizer, SUMMARY_PERSONALITIES
from src.arena import LLMArena
from src.llm_wrapper import LLMClient

# Initialize backend instances
client = LLMClient()
summarizer = WebsiteSummarizer(llm_client=client)
arena = LLMArena(llm_client=client)

# Provider & Model Definitions
PROVIDERS = ["OpenAI", "Groq", "Anthropic"]
PERSONALITY_CHOICES = list(SUMMARY_PERSONALITIES.keys())

SAMPLE_URLS = [
    ["https://www.python.org/"],
    ["https://groq.com/"],
    ["https://openai.com/"],
    ["https://news.ycombinator.com/"],
    ["https://github.com/"],
]

SAMPLE_PROMPTS = [
    ["Explain quantum computing to a 10-year-old using a pizza analogy in 2 sentences."],
    ["Write a witty 4-line cyberpunk poem about debugging an AI agent at 3 AM."],
    ["Why are Groq LPUs so fundamentally faster for LLM inference than traditional GPUs?"],
    ["Compare REST APIs vs GraphQL in 3 bullet points with a punchline."],
]

# ----------------------------------------------------------------------------
# Backend Handlers
# ----------------------------------------------------------------------------
def handle_summarize(url: str, personality: str, provider: str, model: str, custom_prompt: str):
    if not url or not url.strip():
        return (
            "⚠️ **Please enter a valid website URL to analyze.**",
            "<div class='status-pill warn'>⚠️ Waiting for Input</div>",
        )
    
    result = summarizer.summarize(
        url=url.strip(),
        personality=personality,
        provider=provider,
        model=model if model else None,
        custom_instructions=custom_prompt,
    )
    
    if result["is_success"]:
        badge = f"<div class='status-pill success'>✅ Completed · {result['metadata']}</div>"
    else:
        badge = f"<div class='status-pill error'>❌ Error · {result['metadata']}</div>"
        
    return result["summary"], badge


def handle_arena_battle(prompt: str, prov_a: str, mod_a: str, prov_b: str, mod_b: str, sys_prompt: str):
    if not prompt or not prompt.strip():
        return (
            "⚠️ Enter a battle prompt above to begin the contest!",
            "<div class='latency-badge'>⏱️ Standby</div>",
            "⚠️ Enter a battle prompt above to begin the contest!",
            "<div class='latency-badge'>⏱️ Standby</div>",
            "<div class='status-pill warn'>⚠️ No Prompt Submitted</div>"
        )
    
    res_a, res_b = arena.battle(
        prompt=prompt.strip(),
        provider_a=prov_a,
        model_a=mod_a,
        provider_b=prov_b,
        model_b=mod_b,
        system_prompt=sys_prompt,
    )
    
    speed_winner = "⚡ Contender B (Groq)" if res_b["latency"] < res_a["latency"] else "🤖 Contender A (OpenAI)"
    status_html = (
        f"<div class='status-pill success'>🏆 Speed Winner: <b>{speed_winner}</b> "
        f"({min(res_a['latency'], res_b['latency'])}s vs {max(res_a['latency'], res_b['latency'])}s)</div>"
    )
    
    meta_a_html = f"<div class='latency-badge'>⚡ <b>{res_a['latency']}s</b> · {res_a['provider']} ({res_a['model']})</div>"
    meta_b_html = f"<div class='latency-badge'>⚡ <b>{res_b['latency']}s</b> · {res_b['provider']} ({res_b['model']})</div>"
    
    return res_a["content"], meta_a_html, res_b["content"], meta_b_html, status_html


def handle_vote(winner_choice: str, prompt: str, mod_a: str, mod_b: str):
    if not prompt:
        return "<div class='status-pill warn'>ℹ️ Run a battle first before casting your vote!</div>"
    msg = arena.record_vote(winner=winner_choice, prompt=prompt, model_a_label=mod_a, model_b_label=mod_b)
    return f"<div class='status-pill vote-success'>🗳️ <b>Vote Registered:</b> You crowned <b>{winner_choice}</b>! (Total votes logged: {len(arena.vote_history)})</div>"


def handle_playground(prompt: str, sys_prompt: str, provider: str, model: str, temperature: float, max_tokens: int):
    if not prompt or not prompt.strip():
        return "⚠️ Please enter a prompt.", "<div class='status-pill warn'>⚠️ Awaiting Input</div>"
    
    resp = client.generate(
        prompt=prompt.strip(),
        system_prompt=sys_prompt.strip(),
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=int(max_tokens),
    )
    meta = f"<div class='status-pill success'>⚡ Response in <b>{resp.latency_seconds}s</b> · Provider: <code>{resp.provider}</code> · Model: <code>{resp.model}</code></div>"
    return resp.content, meta


def update_model_dropdown(provider: str):
    models = Config.AVAILABLE_MODELS.get(provider, [])
    default_val = models[0] if models else None
    return gr.Dropdown(choices=models, value=default_val)


# ----------------------------------------------------------------------------
# Professional Studio Theme & Color Grading CSS
# ----------------------------------------------------------------------------
PROFESSIONAL_STUDIO_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-page: #f8fafc;
    --card-bg: #ffffff;
    --card-border: #e2e8f0;
    --card-border-hover: #cbd5e1;
    --text-heading: #0f172a;
    --text-body: #334155;
    --text-muted: #64748b;
    --brand-primary: #ff5722;
    --brand-primary-hover: #ea580c;
    --brand-indigo: #4f46e5;
    --brand-emerald: #059669;
}

body, .gradio-container {
    background-color: #f8fafc !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(255, 87, 34, 0.04) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(79, 70, 229, 0.05) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(5, 150, 105, 0.03) 0px, transparent 50%) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-body) !important;
    max-width: 1380px !important;
    margin: 0 auto !important;
}

/* Master Header Card */
.master-hero {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 32px 28px !important;
    box-shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.06), 0 2px 6px rgba(15, 23, 42, 0.02) !important;
    margin-bottom: 24px !important;
    text-align: center !important;
    position: relative !important;
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c2410c;
    background: #fff7ed;
    border: 1px solid #ffedd5;
    padding: 6px 14px;
    border-radius: 9999px;
    margin-bottom: 12px;
}

.hero-kicker .pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ea580c;
    box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.2);
}

.hero-title {
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #0f172a !important;
    margin: 6px 0 10px 0 !important;
}

.hero-title span {
    background: linear-gradient(135deg, #ff5722 0%, #d83c18 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.05rem !important;
    color: #475569 !important;
    max-width: 820px;
    margin: 0 auto 16px auto;
    line-height: 1.6 !important;
}

.series-tracker-bar {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}

.day-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #64748b;
    transition: all 0.2s ease;
}

.day-badge.active {
    background: #0f172a;
    border-color: #0f172a;
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
}

/* Professional White Surface Cards */
.pro-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02) !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
}

.pro-card:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08) !important;
}

/* Markdown High-Contrast Reader */
.pro-card .markdown {
    color: #0f172a !important;
    font-size: 0.96rem !important;
    line-height: 1.7 !important;
}

.pro-card .markdown h1,
.pro-card .markdown h2,
.pro-card .markdown h3,
.pro-card .markdown h4 {
    color: #0f172a !important;
    font-weight: 700 !important;
    margin-top: 1.1em !important;
    margin-bottom: 0.5em !important;
}

.pro-card .markdown strong {
    color: #0f172a !important;
    font-weight: 700 !important;
}

.pro-card .markdown p,
.pro-card .markdown li {
    color: #334155 !important;
}

.pro-card .markdown ul {
    padding-left: 1.3rem !important;
}

.pro-card .markdown li {
    margin-bottom: 0.4rem !important;
}

.pro-card .markdown code {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88em !important;
    padding: 2px 6px !important;
    border-radius: 6px !important;
    border: 1px solid #e2e8f0 !important;
}

/* Action Buttons */
.btn-primary-pro {
    background: linear-gradient(135deg, #ff5722 0%, #ea580c 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(234, 88, 12, 0.3) !important;
    transition: all 0.15s ease !important;
}

.btn-primary-pro:hover {
    background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(234, 88, 12, 0.4) !important;
}

.btn-secondary-pro {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.15s ease !important;
}

.btn-secondary-pro:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 600;
    margin-top: 8px;
}

.status-pill.success {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
}

.status-pill.warn {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
}

.status-pill.error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}

.status-pill.vote-success {
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    color: #3730a3;
}

.latency-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    margin-top: 6px;
}

/* Arena VS Divider */
.arena-vs-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: #0f172a;
    color: #ffffff;
    font-weight: 800;
    font-size: 1rem;
    margin: 0 auto;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2);
}

/* Clean Tabs Navigation */
.tabs {
    background: transparent !important;
}

.tab-nav {
    background: #f1f5f9 !important;
    border-radius: 14px !important;
    padding: 5px !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 20px !important;
}

.tab-nav button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: #64748b !important;
    transition: all 0.15s ease !important;
}

.tab-nav button.selected {
    background: #ffffff !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
}
"""

theme = gr.themes.Default(
    primary_hue="orange",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
).set(
    body_background_fill="#f8fafc",
    block_background_fill="#ffffff",
    block_border_width="1px",
    block_border_color="#e2e8f0",
    block_shadow="0 2px 8px rgba(15, 23, 42, 0.04)",
    input_background_fill="#ffffff",
    input_border_color="#cbd5e1",
)

with gr.Blocks(title="AI Engineering Master Series | Class 01", theme=theme, css=PROFESSIONAL_STUDIO_CSS) as demo:
    
    # Master Hero Header
    with gr.Column(elem_classes=["master-hero"]):
        gr.HTML(
            """
            <div class="hero-kicker"><span class="pulse-dot"></span> Production AI Engineering Architecture</div>
            <h1 class="hero-title">AI Website Summarizer & <span>Model Battle Arena</span></h1>
            <p class="hero-subtitle">
                A modular, enterprise-grade AI system featuring unified multi-provider routing 
                (<b>OpenAI</b>, <b>Groq LPU</b>, <b>Anthropic Claude</b>), intelligent DOM web content extraction, persona-driven summarization, and side-by-side model benchmarking.
            </p>
            <div class="series-tracker-bar">
                <span class="day-badge active">⚡ Multi-Provider Wrapper</span>
                <span class="day-badge active">🕷️ Anti-Scrape Cleaner</span>
                <span class="day-badge active">🎭 6 System Personas</span>
                <span class="day-badge active">🥊 Live LLM Arena</span>
                <span class="day-badge active">🧪 100% Mocked Tests</span>
            </div>
            """
        )

    with gr.Tabs(elem_classes=["tabs"]):
        # ====================================================================
        # TAB 1: FLAGSHIP AI WEBSITE SUMMARIZER
        # ====================================================================
        with gr.Tab("🔎 AI Website Summarizer", id="tab_summarizer"):
            with gr.Row():
                # Input Column
                with gr.Column(scale=5, elem_classes=["pro-card"]):
                    gr.Markdown("### 🌐 Target Web Page & Persona")
                    url_input = gr.Textbox(
                        label="Website URL",
                        placeholder="https://www.python.org/ or https://groq.com/ or https://news.ycombinator.com/",
                        lines=1,
                    )
                    
                    personality_dropdown = gr.Dropdown(
                        choices=PERSONALITY_CHOICES,
                        value=PERSONALITY_CHOICES[0],
                        label="Select System Persona & Tone",
                    )
                    
                    with gr.Accordion("⚙️ Model Engine & Provider Settings", open=False):
                        with gr.Row():
                            sum_provider = gr.Dropdown(
                                choices=PROVIDERS,
                                value="Groq",
                                label="Inference Provider",
                            )
                            sum_model = gr.Dropdown(
                                choices=Config.AVAILABLE_MODELS["Groq"],
                                value=Config.DEFAULT_GROQ_MODEL,
                                label="Target Model",
                            )
                        custom_instructions = gr.Textbox(
                            label="Custom System Prompt Rules (Optional)",
                            placeholder="e.g. Highlight pricing, technical architecture, or competitive moat...",
                            lines=2,
                        )

                    with gr.Row():
                        clear_sum_btn = gr.Button("🗑️ Clear", variant="secondary", elem_classes=["btn-secondary-pro"])
                        submit_sum_btn = gr.Button("✨ Extract & Summarize", variant="primary", elem_classes=["btn-primary-pro"])

                    gr.Markdown("#### 💡 Quick URL Examples:")
                    gr.Examples(
                        examples=SAMPLE_URLS,
                        inputs=[url_input],
                        label=None,
                    )

                # Output Column
                with gr.Column(scale=6, elem_classes=["pro-card"]):
                    gr.Markdown("### 📄 Structured AI Executive Summary")
                    sum_meta = gr.HTML(value="<div class='status-pill warn'>⚡ Ready for URL input</div>")
                    sum_output = gr.Markdown(value="*Paste any website URL and click **Extract & Summarize** to view the live result.*")

            # Wire Events
            sum_provider.change(update_model_dropdown, inputs=[sum_provider], outputs=[sum_model])
            submit_sum_btn.click(
                handle_summarize,
                inputs=[url_input, personality_dropdown, sum_provider, sum_model, custom_instructions],
                outputs=[sum_output, sum_meta],
            )
            clear_sum_btn.click(
                lambda: ("", "*Cleared output.*", "<div class='status-pill warn'>⚡ Cleared</div>"),
                outputs=[url_input, sum_output, sum_meta],
            )

        # ====================================================================
        # TAB 2: LLM BATTLE ARENA
        # ====================================================================
        with gr.Tab("🥊 LLM Battle Arena", id="tab_arena"):
            with gr.Column(elem_classes=["pro-card"]):
                gr.Markdown("### ⚔️ Side-by-Side Model Comparator & Latency Benchmark")
                gr.Markdown("Broadcast the identical prompt to two AI models simultaneously to evaluate output quality and execution latency.")
                
                arena_prompt = gr.Textbox(
                    label="Battle Prompt",
                    placeholder="Ask any complex architectural question, creative prompt, or coding logic...",
                    lines=2,
                )
                
                with gr.Row():
                    arena_sys_prompt = gr.Textbox(
                        label="System Persona / Guidelines",
                        value="You are a witty, concise, and highly knowledgeable AI assistant.",
                        lines=1,
                        scale=4,
                    )
                    battle_btn = gr.Button("⚔️ Launch Battle!", variant="primary", elem_classes=["btn-primary-pro"], scale=1)

                arena_status_badge = gr.HTML(value="<div class='status-pill warn'>⚔️ Select contenders and start battle</div>")

                with gr.Row():
                    # Contender A
                    with gr.Column(scale=1, elem_classes=["pro-card"]):
                        gr.Markdown("### 🤖 Contender A")
                        with gr.Row():
                            arena_prov_a = gr.Dropdown(choices=PROVIDERS, value="OpenAI", label="Provider A")
                            arena_mod_a = gr.Dropdown(choices=Config.AVAILABLE_MODELS["OpenAI"], value="gpt-4o-mini", label="Model A")
                        arena_prov_a.change(update_model_dropdown, inputs=[arena_prov_a], outputs=[arena_mod_a])
                        
                        arena_meta_a = gr.HTML(value="<div class='latency-badge'>⏱️ Standby</div>")
                        arena_out_a = gr.Markdown(value="*Contender A response will render here...*")
                        vote_a_up = gr.Button("👍 Crown Model A", variant="secondary", elem_classes=["btn-secondary-pro"])

                    # Center VS Emblem
                    with gr.Column(scale=0, min_width=70):
                        gr.HTML("<div style='margin-top: 100px;'><div class='arena-vs-badge'>VS</div></div>")

                    # Contender B
                    with gr.Column(scale=1, elem_classes=["pro-card"]):
                        gr.Markdown("### ⚡ Contender B")
                        with gr.Row():
                            arena_prov_b = gr.Dropdown(choices=PROVIDERS, value="Groq", label="Provider B")
                            arena_mod_b = gr.Dropdown(choices=Config.AVAILABLE_MODELS["Groq"], value="openai/gpt-oss-120b", label="Model B")
                        arena_prov_b.change(update_model_dropdown, inputs=[arena_prov_b], outputs=[arena_mod_b])
                        
                        arena_meta_b = gr.HTML(value="<div class='latency-badge'>⏱️ Standby</div>")
                        arena_out_b = gr.Markdown(value="*Contender B response will render here...*")
                        vote_b_up = gr.Button("👍 Crown Model B", variant="secondary", elem_classes=["btn-secondary-pro"])

                with gr.Row():
                    vote_tie = gr.Button("🤝 It's a Dead Tie", variant="secondary", elem_classes=["btn-secondary-pro"])
                    vote_verdict = gr.HTML(value="<div class='status-pill warn'>🗳️ Cast your vote after comparing outputs!</div>")

                gr.Markdown("#### 💡 Quick Battle Prompts:")
                gr.Examples(examples=SAMPLE_PROMPTS, inputs=[arena_prompt], label=None)

                # Arena Events Wiring
                battle_btn.click(
                    handle_arena_battle,
                    inputs=[arena_prompt, arena_prov_a, arena_mod_a, arena_prov_b, arena_mod_b, arena_sys_prompt],
                    outputs=[arena_out_a, arena_meta_a, arena_out_b, arena_meta_b, arena_status_badge],
                )
                vote_a_up.click(lambda p, ma, mb: handle_vote("Contender A", p, ma, mb), inputs=[arena_prompt, arena_mod_a, arena_mod_b], outputs=[vote_verdict])
                vote_b_up.click(lambda p, ma, mb: handle_vote("Contender B", p, ma, mb), inputs=[arena_prompt, arena_mod_a, arena_mod_b], outputs=[vote_verdict])
                vote_tie.click(lambda p, ma, mb: handle_vote("Tie", p, ma, mb), inputs=[arena_prompt, arena_mod_a, arena_mod_b], outputs=[vote_verdict])

        # ====================================================================
        # TAB 3: MULTI-PROVIDER PLAYGROUND
        # ====================================================================
        with gr.Tab("💬 Multi-Provider Playground", id="tab_playground"):
            with gr.Row():
                with gr.Column(scale=4, elem_classes=["pro-card"]):
                    gr.Markdown("### 🎛️ Provider & Hyperparameters")
                    play_provider = gr.Dropdown(choices=PROVIDERS, value="Groq", label="Inference Engine")
                    play_model = gr.Dropdown(choices=Config.AVAILABLE_MODELS["Groq"], value=Config.DEFAULT_GROQ_MODEL, label="Target Model")
                    play_provider.change(update_model_dropdown, inputs=[play_provider], outputs=[play_model])
                    
                    play_sys_prompt = gr.Textbox(
                        label="System Persona Prompt",
                        value="You are a senior AI software architect. Respond with high precision and concise code examples.",
                        lines=3,
                    )
                    play_temp = gr.Slider(minimum=0.0, maximum=1.5, value=0.7, step=0.1, label="Temperature (Creativity)")
                    play_tokens = gr.Slider(minimum=100, maximum=4000, value=1500, step=100, label="Max Output Tokens")
                    
                    play_btn = gr.Button("🚀 Generate Response", variant="primary", elem_classes=["btn-primary-pro"])

                with gr.Column(scale=7, elem_classes=["pro-card"]):
                    gr.Markdown("### 💬 Live Execution Output")
                    play_user_prompt = gr.Textbox(
                        label="User Prompt",
                        placeholder="Ask anything, test code generation, or evaluate reasoning...",
                        lines=4,
                    )
                    play_meta = gr.HTML(value="<div class='status-pill warn'>⚡ Standby for prompt</div>")
                    play_output = gr.Markdown(value="*Generation results will appear here...*")

            play_btn.click(
                handle_playground,
                inputs=[play_user_prompt, play_sys_prompt, play_provider, play_model, play_temp, play_tokens],
                outputs=[play_output, play_meta],
            )

        # ====================================================================
        # TAB 4: ARCHITECTURE & DEEP DIVE
        # ====================================================================
        with gr.Tab("🎓 Architecture & Code Guide", id="tab_guide"):
            with gr.Column(elem_classes=["pro-card"]):
                gr.Markdown(
                    """
                    # 🏗️ System Architecture & Engineering Principles
                    
                    ### 1. "The Brain is Swappable" Design Pattern
                    In modern AI engineering, business logic should never be tightly coupled to a single vendor. 
                    Our unified `LLMClient` wraps OpenAI, Groq, and Anthropic into a single standardized interface:
                    ```python
                    from src.llm_wrapper import LLMClient

                    client = LLMClient()
                    response = client.generate(
                        prompt="Explain recursion",
                        provider="Groq",     # Or 'OpenAI', 'Anthropic'
                        model="openai/gpt-oss-120b"
                    )
                    print(response.content, response.latency_seconds)
                    ```
                    
                    ### 2. Token-Saving DOM Noise Stripping
                    Raw HTML contains thousands of tokens in navigation bars, footers, stylesheets, and scripts. 
                    `src/scraper.py` parses and removes noise tags before constructing the prompt, saving **70%+ of token costs**:
                    ```python
                    # Strips: script, style, nav, footer, header, svg, form, iframe, aside
                    for tag in soup(["script", "style", "nav", "footer", "header", "svg"]):
                        tag.decompose()
                    ```
                    
                    ### 3. Strict Secret Safety Habits
                    - `.env` is isolated locally and blocked by `.gitignore`.
                    - `.env.example` provides public documentation without risking credential leaks.
                    """
                )

    # Footer
    gr.HTML(
        """
        <div style="text-align: center; padding: 20px 0; margin-top: 30px; border-top: 1px solid #e2e8f0;">
            <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
                🚀 <b>AI Engineering Project</b> · Professional Multi-Provider Architecture
            </p>
        </div>
        """
    )


if __name__ == "__main__":
    print("🚀 Launching AI Engineering Studio Hub...")
    demo.launch(share=False)
