"""
╔══════════════════════════════════════════════════════════════╗
║   Document-to-Action Engine  ·  PS3 Assignment               ║
║   Transforms any document into structured actionable output  ║
║                                                              ║
║   Supported AI Providers:                                    ║
║     • Anthropic Claude  (claude-opus-4-5)                   ║
║     • OpenAI ChatGPT    (gpt-4o)                            ║
║     • Google Gemini     (gemini-1.5-pro)                    ║
╚══════════════════════════════════════════════════════════════╝

Architecture:
  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────────┐
  │ Upload/Paste │──▶│ Text Extract │──▶│  AI Provider (your choice)  │
  └──────────────┘   └──────────────┘   └────────────┬────────────────┘
                                                      │ JSON
                      ┌───────────────────────────────▼──────────────┐
                      │  Structured Action Intelligence               │
                      │  · Action Items   · Red Flags   · Decisions  │
                      │  · Key Entities   · Timeline    · Opps       │
                      └──────────────────────────────────────────────┘
"""

# ─── Standard library ────────────────────────────────────────────────────────
import io
import json
import streamlit as st

# ─── Optional AI provider SDKs (graceful fallback) ───────────────────────────
try:
    import anthropic
    CLAUDE_OK = True
except ImportError:
    CLAUDE_OK = False

try:
    from openai import OpenAI
    OPENAI_OK = True
except ImportError:
    OPENAI_OK = False

try:
    from google import genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

# ─── Optional document parsing deps ──────────────────────────────────────────
try:
    import fitz
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from docx import Document as DocxDocument
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Doc Action Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg:       #0c0d0f;
    --surface:  #141518;
    --surface2: #1c1e24;
    --border:   #252730;
    --accent:   #f0c040;
    --accent2:  #3af0a0;
    --accent3:  #60b8ff;
    --danger:   #f05060;
    --muted:    #5a5f72;
    --text:     #e8eaf0;
    --textdim:  #9098b0;
}

html, body, .stApp { background: var(--bg) !important; color: var(--text); }
.block-container { padding-top: 2rem !important; max-width: 1280px !important; }

.eng-header {
    font-family: 'Syne', sans-serif; font-weight: 800;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    letter-spacing: -0.04em; line-height: 1.1;
    color: var(--text); margin-bottom: 0.15rem;
}
.eng-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    color: var(--accent); letter-spacing: 0.14em;
    text-transform: uppercase; margin-bottom: 1.8rem;
}
.eng-badge {
    display: inline-block; background: var(--accent); color: #0c0d0f;
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    font-weight: 600; padding: 2px 8px; border-radius: 2px;
    margin-right: 6px; vertical-align: middle;
}
.provider-pill {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    padding: 3px 12px; border-radius: 20px; border: 1px solid;
    margin-left: 8px; vertical-align: middle;
}
.pill-claude  { background: #1f1a0f; color: #f0c040; border-color: #f0c040; }
.pill-openai  { background: #0f1f17; color: #3af0a0; border-color: #3af0a0; }
.pill-gemini  { background: #0f1620; color: #60b8ff; border-color: #60b8ff; }

.action-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
    font-family: 'Inter', sans-serif; transition: border-color 0.2s;
}
.action-card:hover { border-color: var(--muted); }
.card-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.63rem;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.45rem;
}
.card-title {
    font-family: 'Syne', sans-serif; font-weight: 700;
    font-size: 1rem; color: var(--text); margin-bottom: 0.35rem;
}
.card-body { font-size: 0.88rem; color: var(--textdim); line-height: 1.65; }

.chip {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; margin: 2px;
}
.chip-high   { background:#3d1a1e; color:var(--danger);  border:1px solid var(--danger);  }
.chip-medium { background:#2d2a10; color:var(--accent);  border:1px solid var(--accent);  }
.chip-low    { background:#10281e; color:var(--accent2); border:1px solid var(--accent2); }

.metric-row { display:flex; gap:0.8rem; margin-bottom:1.4rem; flex-wrap:wrap; }
.metric-box {
    flex:1; min-width:110px;
    background:var(--surface); border:1px solid var(--border);
    border-radius:8px; padding:0.9rem 1.1rem;
}
.m-val {
    font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:800;
    color:var(--accent); line-height:1;
}
.m-label {
    font-family:'JetBrains Mono',monospace; font-size:0.62rem;
    color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; margin-top:4px;
}

.stTextArea textarea, .stTextInput input {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important; border-radius: 6px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(240,192,64,0.12) !important;
}
.stButton > button {
    background: var(--accent) !important; color: #0c0d0f !important;
    border: none !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.65rem 1.8rem !important; border-radius: 6px !important;
    width: 100%; transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stFileUploader section {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important; border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important; border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important; padding: 0.6rem 1rem !important;
}
.stTabs [aria-selected="true"] { color: var(--accent) !important; }
.stSidebar { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
label { color: var(--textdim) !important; font-family:'Inter',sans-serif !important; font-size:0.85rem !important; }
h1,h2,h3 { font-family:'Syne',sans-serif !important; }
div[data-testid="stSidebarContent"] { padding-top: 1.5rem !important; }
.eng-divider { border:none; border-top:1px solid var(--border); margin:1.2rem 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def extract_text_from_file(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    raw  = uploaded_file.read()
    if name.endswith(".pdf"):
        if not PDF_OK:
            return "[PDF support unavailable — pip install PyMuPDF]"
        doc = fitz.open(stream=raw, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if name.endswith(".docx"):
        if not DOCX_OK:
            return "[DOCX support unavailable — pip install python-docx]"
        d = DocxDocument(io.BytesIO(raw))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    return raw.decode("utf-8", errors="replace")


def build_prompt(doc_text: str, doc_type: str, focus_areas: list) -> str:
    focus_str = ", ".join(focus_areas) if focus_areas else "all relevant aspects"
    return f"""You are a senior strategic analyst. Analyze the following {doc_type} and produce a comprehensive action intelligence report.

DOCUMENT:
\"\"\"
{doc_text[:4000]}
\"\"\"

FOCUS AREAS: {focus_str}

Return ONLY valid JSON — no markdown fences, no preamble — with this exact schema:

{{
  "document_summary": "2-3 sentence executive summary",
  "document_type_detected": "e.g. Resume, Contract, Financial Report, etc.",
  "key_entities": [
    {{"name": "...", "type": "Person|Org|Date|Amount|Location|Term", "significance": "..."}}
  ],
  "critical_findings": [
    {{"finding": "...", "impact": "High|Medium|Low", "evidence": "exact quote or reference"}}
  ],
  "action_items": [
    {{"action": "...", "owner": "...", "priority": "High|Medium|Low",
      "deadline_hint": "immediately|within 1 week|within 1 month|no urgency",
      "rationale": "..."}}
  ],
  "decisions_required": [
    {{"decision": "...", "options": ["...", "..."], "recommended": "...", "reasoning": "..."}}
  ],
  "red_flags": [
    {{"flag": "...", "severity": "Critical|Warning|Note", "location": "..."}}
  ],
  "opportunities": [
    {{"opportunity": "...", "potential": "..."}}
  ],
  "timeline_events": [
    {{"event": "...", "date_or_period": "...", "status": "past|current|upcoming|deadline"}}
  ],
  "metrics_snapshot": {{
    "total_actions": 0,
    "high_priority_count": 0,
    "red_flag_count": 0,
    "decisions_needed": 0
  }},
  "executive_recommendation": "One-paragraph strategic recommendation"
}}

Be precise, evidence-based, and focused on real next steps."""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def call_claude(api_key: str, prompt: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(msg.content[0].text)

def call_openai(api_key: str, prompt: str) -> dict:
    from openai import OpenAI
    import json

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",  # 👈 important
        api_key=api_key,
    )

    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",  # 👈 OpenRouter model
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a strategic analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )

    return json.loads(resp.choices[0].message.content)

def call_gemini(api_key: str, prompt: str) -> dict:
    from google import genai
    import json, re

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    text = response.text

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def run_ai(provider: str, api_key: str, prompt: str) -> dict:
    if provider == "Claude (Anthropic)":
        return call_claude(api_key, prompt)
    elif provider == "ChatGPT (OpenAI)":
        return call_openai(api_key, prompt)
    elif provider == "Gemini (Google)":
        return call_gemini(api_key, prompt)
    raise ValueError(f"Unknown provider: {provider}")


def backfill_metrics(result: dict) -> dict:
    result.setdefault("metrics_snapshot", {})
    ms = result["metrics_snapshot"]
    ms["total_actions"]       = len(result.get("action_items", []))
    ms["high_priority_count"] = sum(1 for a in result.get("action_items", []) if a.get("priority") == "High")
    ms["red_flag_count"]      = len(result.get("red_flags", []))
    ms["decisions_needed"]    = len(result.get("decisions_required", []))
    return result


def priority_chip(p: str) -> str:
    cls = {"High": "chip-high", "Medium": "chip-medium", "Low": "chip-low"}.get(p, "chip-low")
    return f'<span class="chip {cls}">{p}</span>'

def severity_chip(s: str) -> str:
    cls = {"Critical": "chip-high", "Warning": "chip-medium", "Note": "chip-low"}.get(s, "chip-low")
    return f'<span class="chip {cls}">{s}</span>'

def provider_pill_html(provider: str) -> str:
    if "Claude" in provider:
        icon, cls = "◆", "pill-claude"
    elif "OpenAI" in provider or "ChatGPT" in provider:
        icon, cls = "◉", "pill-openai"
    else:
        icon, cls = "✦", "pill-gemini"
    return f'<span class="provider-pill {cls}">{icon} {provider}</span>'


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚡ Configuration")

    st.markdown("""<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;
    color:#5a5f72;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px'>
    AI Provider</div>""", unsafe_allow_html=True)

    provider = st.selectbox(
        "AI Provider",
        ["Claude (Anthropic)", "ChatGPT (OpenAI)", "Gemini (Google)"],
        label_visibility="collapsed",
    )

    provider_meta = {
        "Claude (Anthropic)": ("claude-opus-4-5",  "console.anthropic.com",  "#f0c040"),
        "ChatGPT (OpenAI)":   ("gpt-4o",           "platform.openai.com",    "#3af0a0"),
        "Gemini (Google)":    ("gemini-1.5-pro",   "aistudio.google.com",    "#60b8ff"),
    }
    model_name, key_hint, accent = provider_meta[provider]

    st.markdown(f"""
    <div style='background:#1c1e24;border:1px solid #252730;border-radius:6px;
    padding:0.6rem 0.9rem;margin-bottom:0.8rem'>
        <div style='font-family:Syne,sans-serif;font-weight:700;font-size:0.88rem;
        color:{accent}'>{provider}</div>
        <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#5a5f72;margin-top:3px'>
        Model: {model_name}</div>
        <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#5a5f72;margin-top:2px'>
        Key: {key_hint}</div>
    </div>""", unsafe_allow_html=True)

    key_label = {
        "Claude (Anthropic)": "Anthropic API Key",
        "ChatGPT (OpenAI)":   "OpenAI API Key",
        "Gemini (Google)":    "Google AI API Key",
    }[provider]

    key_placeholder = {
        "Claude (Anthropic)": "sk-ant-...",
        "ChatGPT (OpenAI)":   "sk-...",
        "Gemini (Google)":    "AIza...",
    }[provider]

    api_key = st.text_input(key_label, type="password", placeholder=key_placeholder)

    st.markdown("<hr class='eng-divider'>", unsafe_allow_html=True)

    doc_type = st.selectbox("Document Type (hint)", [
        "Auto-detect", "Resume / CV", "Contract / Agreement",
        "Financial Report", "Research Paper", "Business Proposal",
        "Legal Document", "Meeting Notes", "Product Spec", "Other",
    ])

    st.markdown("<hr class='eng-divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;
    color:#5a5f72;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px'>
    Focus Areas</div>""", unsafe_allow_html=True)

    focus_areas = []
    if st.checkbox("⚡ Action Items",     value=True):  focus_areas.append("Action Items")
    if st.checkbox("🚩 Risk & Red Flags", value=True):  focus_areas.append("Risk & Red Flags")
    if st.checkbox("🔀 Decisions",        value=True):  focus_areas.append("Decisions Required")
    if st.checkbox("🔍 Key Entities"):                  focus_areas.append("Key Entities")
    if st.checkbox("📅 Timeline Events"):               focus_areas.append("Timeline Events")
    if st.checkbox("💡 Opportunities"):                 focus_areas.append("Opportunities")

    st.markdown("<hr class='eng-divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='font-family:JetBrains Mono,monospace;font-size:0.68rem;
    color:#5a5f72;line-height:1.9'>PS3 · Document-to-Action Engine<br>
    Claude · GPT-4o · Gemini 1.5 Pro<br>
    No data stored · key in-session only</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="eng-header">Document→Action Engine'
    f'{provider_pill_html(provider)}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="eng-sub"><span class="eng-badge">PS3</span>'
    'Generative AI · Unstructured Text → Structured Intelligence</div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown("#### 📄 Input Document")
    tab_paste, tab_upload = st.tabs(["✏️  Paste Text", "📁  Upload File"])

    with tab_paste:
        doc_text_paste = st.text_area(
            "Paste document",
            height=310,
            placeholder="Paste any document — resume, contract, report, meeting notes…",
            label_visibility="collapsed",
        )

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload PDF, DOCX or TXT",
            type=["pdf", "docx", "txt", "md"],
            label_visibility="collapsed",
        )
        doc_text_file = ""
        if uploaded:
            with st.spinner("Extracting text…"):
                doc_text_file = extract_text_from_file(uploaded)
            st.success(f"✓ {len(doc_text_file):,} characters from **{uploaded.name}**")
            with st.expander("Preview extracted text"):
                st.code(doc_text_file[:1800] + ("…" if len(doc_text_file) > 1800 else ""), language=None)

    final_text = doc_text_file or doc_text_paste
    char_count = len(final_text)
    st.markdown(
        f"<div style='font-family:JetBrains Mono,monospace;font-size:0.68rem;"
        f"color:#5a5f72;margin-top:4px'>{char_count:,} chars · ~{char_count//4:,} tokens</div>",
        unsafe_allow_html=True,
    )

    sdk_missing = (
        (provider == "Claude (Anthropic)"  and not CLAUDE_OK) or
        (provider == "ChatGPT (OpenAI)"    and not OPENAI_OK) or
        (provider == "Gemini (Google)"     and not GEMINI_OK)
    )
    if sdk_missing:
        install_cmd = {
            "Claude (Anthropic)": "pip install anthropic",
            "ChatGPT (OpenAI)":   "pip install openai",
            "Gemini (Google)":    "pip install google-generativeai",
        }[provider]
        st.warning(f"SDK missing. Run: `{install_cmd}`")

    ready = bool(api_key) and bool(final_text.strip()) and not sdk_missing
    run_btn = st.button("⚡ Generate Action Intelligence", disabled=not ready)

    if not api_key:
        st.caption(f"↖ Enter your {key_label} in the sidebar")
    elif not final_text.strip():
        st.caption("Paste or upload a document above")


# ══════════════════════════════════════════════════════════════════════════════
#  OUTPUT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_out:
    st.markdown("#### 🎯 Action Intelligence Output")

    if "result" not in st.session_state:
        st.session_state.result   = None
        st.session_state.used_prov = None

    if run_btn and ready:
        dtype  = doc_type if doc_type != "Auto-detect" else "document"
        prompt = build_prompt(final_text, dtype, focus_areas)
        spinner_label = {
            "Claude (Anthropic)": "Analyzing with Claude…",
            "ChatGPT (OpenAI)":   "Analyzing with GPT-4o…",
            "Gemini (Google)":    "Analyzing with Gemini 1.5 Pro…",
        }[provider]

        with st.spinner(spinner_label):
            try:
                result = run_ai(provider, api_key, prompt)
                result = backfill_metrics(result)
                st.session_state.result    = result
                st.session_state.used_prov = provider
            except json.JSONDecodeError as e:
                st.error(f"JSON parse error: {e}")
            except Exception as e:
                err = str(e).lower()
                if "auth" in err or "key" in err or "401" in err or "invalid" in err:
                    st.error("❌ Invalid API key — please check your credentials.")
                elif "quota" in err or "limit" in err or "429" in err:
                    st.error("❌ API quota/rate limit exceeded. Check your billing.")
                elif "model" in err:
                    st.error(f"❌ Model error: {e}")
                else:
                    st.error(f"❌ Error: {e}")

    res = st.session_state.result

    if res:
        used_prov = st.session_state.get("used_prov", provider)

        # ── Summary card ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="action-card">
            <div class="card-label">
                Detected · {res.get('document_type_detected','—')}
                {provider_pill_html(used_prov)}
            </div>
            <div class="card-title">{res.get('document_type_detected','Document Analysis')}</div>
            <div class="card-body">{res.get('document_summary','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metrics ───────────────────────────────────────────────────────────
        ms = res.get("metrics_snapshot", {})
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="m-val">{ms.get('total_actions',0)}</div>
                <div class="m-label">Actions</div>
            </div>
            <div class="metric-box">
                <div class="m-val">{ms.get('high_priority_count',0)}</div>
                <div class="m-label">High Priority</div>
            </div>
            <div class="metric-box">
                <div class="m-val">{ms.get('red_flag_count',0)}</div>
                <div class="m-label">Red Flags</div>
            </div>
            <div class="metric-box">
                <div class="m-val">{ms.get('decisions_needed',0)}</div>
                <div class="m-label">Decisions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tabs = st.tabs([
            "⚡ Actions", "🚩 Red Flags", "🔀 Decisions",
            "🔍 Entities", "📅 Timeline", "💡 Opps", "📋 JSON",
        ])

        # TAB 1 – Actions
        with tabs[0]:
            items = res.get("action_items", [])
            if not items:
                st.info("No action items extracted.")
            for i, a in enumerate(items, 1):
                st.markdown(f"""
                <div class="action-card">
                    <div class="card-label">
                        Action #{i} · {priority_chip(a.get('priority',''))}
                        · {a.get('deadline_hint','')}
                    </div>
                    <div class="card-title">{a.get('action','')}</div>
                    <div class="card-body">
                        <b>Owner:</b> {a.get('owner','—')}<br>
                        <b>Why:</b> {a.get('rationale','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 2 – Red Flags
        with tabs[1]:
            flags = res.get("red_flags", [])
            if not flags:
                st.success("✓ No red flags detected.")
            for f in flags:
                st.markdown(f"""
                <div class="action-card">
                    <div class="card-label">Red Flag · {severity_chip(f.get('severity',''))}</div>
                    <div class="card-title">{f.get('flag','')}</div>
                    <div class="card-body">📍 {f.get('location','')}</div>
                </div>
                """, unsafe_allow_html=True)
            findings = res.get("critical_findings", [])
            if findings:
                st.markdown("<hr class='eng-divider'>", unsafe_allow_html=True)
                st.markdown("**Critical Findings**")
                for f in findings:
                    st.markdown(f"""
                    <div class="action-card">
                        <div class="card-label">Finding · {priority_chip(f.get('impact',''))}</div>
                        <div class="card-title">{f.get('finding','')}</div>
                        <div class="card-body"><em>"{f.get('evidence','')}"</em></div>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 3 – Decisions
        with tabs[2]:
            decisions = res.get("decisions_required", [])
            if not decisions:
                st.info("No decisions identified.")
            for d in decisions:
                opts = " · ".join(f"`{o}`" for o in d.get("options", []))
                st.markdown(f"""
                <div class="action-card">
                    <div class="card-label">Decision Required</div>
                    <div class="card-title">{d.get('decision','')}</div>
                    <div class="card-body">
                        <b>Options:</b> {opts}<br>
                        <b>Recommended:</b>
                        <span style="color:var(--accent2)">{d.get('recommended','')}</span><br>
                        <b>Reasoning:</b> {d.get('reasoning','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 4 – Entities
        with tabs[3]:
            entities = res.get("key_entities", [])
            if not entities:
                st.info("No entities extracted.")
            else:
                rows = "".join(
                    f"<tr>"
                    f"<td style='padding:6px 10px;color:var(--text)'>{e.get('name','')}</td>"
                    f"<td style='padding:6px 10px;color:var(--accent)'><code>{e.get('type','')}</code></td>"
                    f"<td style='padding:6px 10px;color:var(--textdim)'>{e.get('significance','')}</td>"
                    f"</tr>"
                    for e in entities
                )
                st.markdown(f"""
                <table style='width:100%;border-collapse:collapse;font-family:Inter,sans-serif;font-size:0.86rem'>
                    <thead><tr style='border-bottom:1px solid var(--border)'>
                        <th style='text-align:left;padding:6px 10px;color:var(--muted);
                        font-family:JetBrains Mono,monospace;font-size:0.65rem'>NAME</th>
                        <th style='text-align:left;padding:6px 10px;color:var(--muted);
                        font-family:JetBrains Mono,monospace;font-size:0.65rem'>TYPE</th>
                        <th style='text-align:left;padding:6px 10px;color:var(--muted);
                        font-family:JetBrains Mono,monospace;font-size:0.65rem'>SIGNIFICANCE</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
                """, unsafe_allow_html=True)

        # TAB 5 – Timeline
        with tabs[4]:
            events = res.get("timeline_events", [])
            if not events:
                st.info("No timeline events found.")
            sc_map = {
                "past":     "#5a5f72",
                "current":  "var(--accent2)",
                "upcoming": "var(--accent)",
                "deadline": "var(--danger)",
            }
            for ev in events:
                sc = sc_map.get(ev.get("status", "past"), "#5a5f72")
                st.markdown(f"""
                <div class="action-card" style="border-left:3px solid {sc}">
                    <div class="card-label" style="color:{sc}">
                        {ev.get('status','').upper()} · {ev.get('date_or_period','')}
                    </div>
                    <div class="card-title">{ev.get('event','')}</div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 6 – Opportunities
        with tabs[5]:
            opps = res.get("opportunities", [])
            if not opps:
                st.info("No opportunities identified.")
            for o in opps:
                st.markdown(f"""
                <div class="action-card" style="border-color:var(--accent2)">
                    <div class="card-label" style="color:var(--accent2)">Opportunity</div>
                    <div class="card-title">{o.get('opportunity','')}</div>
                    <div class="card-body">{o.get('potential','')}</div>
                </div>
                """, unsafe_allow_html=True)
            rec = res.get("executive_recommendation", "")
            if rec:
                st.markdown(f"""
                <div class="action-card" style="background:#0f1a12;border-color:var(--accent2);margin-top:0.5rem">
                    <div class="card-label" style="color:var(--accent2)">Executive Recommendation</div>
                    <div class="card-body">{rec}</div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 7 – Raw JSON + Download
        with tabs[6]:
            st.json(res)
            st.download_button(
                "⬇ Download JSON Report",
                data=json.dumps(res, indent=2),
                file_name="action_report.json",
                mime="application/json",
            )

    else:
        st.markdown("""
        <div style="border:1px dashed #252730;border-radius:8px;
        padding:3rem 2rem;text-align:center;color:#5a5f72;
        font-family:JetBrains Mono,monospace;font-size:0.78rem;line-height:2.2">
            ⚡ Output appears here<br>
            ── ⚡ action items<br>
            ── 🚩 red flags<br>
            ── 🔀 decisions<br>
            ── 🔍 key entities<br>
            ── 📅 timeline events<br>
            ── 💡 opportunities
        </div>
        """, unsafe_allow_html=True)

