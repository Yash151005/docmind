# DocMind ⚡
### Document-to-Action Engine

> Transform any unstructured document into clear, prioritized intelligence — powered by Claude, GPT-4o, or Gemini.

---

## What is DocMind?

DocMind is a generative AI tool that reads your documents and tells you **what to do next**. Instead of producing a generic summary, it extracts structured action items, surfaces red flags, identifies key decisions, maps entities, and builds a timeline — all in seconds.

Drop in a resume, contract, financial report, research paper, or meeting notes. DocMind does the rest.

---

## Features

- **Multi-Provider AI** — Switch between Anthropic Claude, OpenAI GPT-4o, and Google Gemini from the sidebar. Same output, your preferred model.
- **Document Ingestion** — Upload PDF, DOCX, or TXT files, or paste text directly. No preprocessing needed.
- **Structured Action Output** — Every analysis returns a consistent set of intelligence layers, not a freeform wall of text.
- **Priority Classification** — Every action item and finding is tagged High / Medium / Low with an owner and deadline hint.
- **Downloadable Report** — Export the full structured analysis as a JSON file.
- **No Backend, No Database** — Your API key lives only in the session. Nothing is stored.

---

## Output Layers

| Tab | What you get |
|---|---|
| ⚡ Actions | Prioritized action items with owner, deadline hint, and rationale |
| 🚩 Red Flags | Risks and concerns with Critical / Warning / Note severity |
| 🔀 Decisions | Decisions that must be made, with options and a recommendation |
| 🔍 Entities | Key people, organizations, dates, amounts, and terms |
| 📅 Timeline | Past, current, upcoming, and deadline events |
| 💡 Opportunities | Positive leverage points and an executive recommendation |
| 📋 JSON | Raw structured output with a one-click download |

---

## Supported AI Providers

| Provider | Model | Get API Key |
|---|---|---|
| Anthropic Claude | `claude-opus-4-5` | [console.anthropic.com](https://console.anthropic.com) |
| OpenAI ChatGPT | `gpt-4o` | [platform.openai.com](https://platform.openai.com) |
| Google Gemini | `gemini-1.5-pro` | [aistudio.google.com](https://aistudio.google.com) |

---

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/yourname/docmind.git
cd docmind
```

**2. Install dependencies**
```bash
pip install streamlit anthropic openai google-generativeai PyMuPDF python-docx
```

**3. Run the app**
```bash
streamlit run doc_action_engine.py
```

**4. Open your browser**
```
http://localhost:8501
```

---

## How to Use

1. Open the sidebar and select your **AI Provider**
2. Paste your **API key** for that provider
3. Choose a **document type hint** (or leave on Auto-detect)
4. Select your **focus areas** — actions, risks, decisions, etc.
5. Paste text or upload a file on the left panel
6. Hit **⚡ Generate Action Intelligence**
7. Browse the tabbed output on the right — download the JSON when done

---

## Use Cases

- **HR / Recruiting** — Analyze resumes and extract candidate action points
- **Legal** — Surface red flags and decision points in contracts
- **Finance** — Pull structured insights from financial reports
- **Research** — Convert dense papers into actionable next steps
- **Operations** — Turn meeting notes into an owner-assigned task list

---

## Requirements

```
streamlit
anthropic
openai
google-generativeai
PyMuPDF
python-docx
```

Python 3.9 or higher recommended.

---

## Project Structure

```
docmind/
│
├── doc_action_engine.py   # Single-file Streamlit application
└── README.md              # This file
```

---

## Privacy

DocMind sends your document text to the AI provider you select using the API key you enter. No data is stored by the app itself. Your key exists only for the duration of your browser session.

---

## License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  Built with Streamlit · Powered by Claude, GPT-4o & Gemini
</div>
