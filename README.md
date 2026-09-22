# 🔎 AI Research Agent

> A single-agent AI researcher that performs live web searches and produces structured, multi-format reports on any topic — powered by CrewAI, Groq, and DuckDuckGo.

---

## 1. 📌 Project Definition

**AI Research Agent** is a lightweight, web-based research assistant that uses a single CrewAI agent to investigate any user-specified topic via live DuckDuckGo web searches. It synthesizes findings into a well-organized Markdown report, structured according to the user's chosen **category** (IT / Medical / Engineering / Other) and **output format(s)** (Paragraph, Bullet, Table, Summary, Comparison, or custom).

The project is designed as a **beginner-friendly reference implementation** of a modern AI agent pipeline — demonstrating how to combine:

- An LLM "brain" (Groq-hosted `openai/gpt-oss-120b`)
- A tool-use loop (DuckDuckGo search)
- A task orchestration framework (CrewAI)
- A clean web UI (Streamlit)

…into a single, deployable application with no paid search APIs required.

---

## 2. 🔭 Scope

### ✅ In Scope

| Area | Coverage |
|------|----------|
| **Topic domain** | Any general-knowledge topic (IT, Medical, Engineering, or user-defined "Other") |
| **Information source** | Live web via DuckDuckGo (free, no API key) |
| **Output formats** | Paragraph, Bullet, Table, Summary, Diff Comparison, and custom "Other" |
| **User interface** | Single-page Streamlit web app |
| **Deployment targets** | Local machine (`streamlit run`) and Streamlit Community Cloud |
| **Agent architecture** | Single-agent, single-task, sequential process |
| **Report length** | ~600–1200 words per report |

### ❌ Out of Scope (by design)

- Multi-agent collaboration or delegation
- Paid search APIs (Google, Bing, Serper)
- Persistent memory / long-term knowledge base
- Authentication, user accounts, or usage quotas
- PDF / DOCX export (Markdown only)
- Real-time streaming of agent thoughts to the UI

---

## 3. 🎯 Problem to Solve

### The Pain Point

Researchers, students, and professionals often need **quick, structured overviews** of unfamiliar topics — but assembling one manually means:

1. Opening dozens of browser tabs
2. Copy-pasting snippets from different sources
3. Re-formatting the same information into bullets, tables, and summaries
4. Losing track of which source said what

Existing AI chatbots can summarize text, but they **hallucinate facts**, have **stale knowledge**, and don't cite sources reliably. Enterprise research tools are powerful but **expensive and overkill** for a quick investigation.

### How This Project Solves It

The AI Research Agent provides a **focused, single-purpose workflow**:

- 🔍 **Grounded in live data** — every claim comes from a real DuckDuckGo search result
- 🧱 **Structured output** — the user picks the format(s) they actually need
- 🏷️ **Domain-aware** — category selection helps the agent focus on the right kind of sources
- 💸 **Free to run** — uses Groq's free tier + DuckDuckGo (no paid search API)
- 🚀 **One-click deployment** — works locally or on Streamlit Cloud in minutes

It's not a replacement for deep academic research — it's a **fast first pass** that saves 30–60 minutes of manual work per topic.

---

## 4. ⭐ Features

### Core Capabilities

- 🤖 **Single CrewAI Agent** — a "Senior Research Analyst" persona with a clear role, goal, and backstory
- 🔎 **Live Web Search Tool** — custom DuckDuckGo integration (no API key required)
- 🧠 **Groq-Powered LLM** — fast inference using `openai/gpt-oss-120b`
- 🛡️ **Rate-Limit Resilience** — automatic retry with exponential backoff for Groq's free-tier TPM limits
- 🐛 **Cache-Breakpoint Workaround** — patches a known CrewAI bug for non-Anthropic providers

### User Interface

- 📝 **Topic input** — free-text research question
- 🗂️ **Category selector** — `IT_Technology` · `Medical` · `Engineering` · `Other` (with custom label)
- 📊 **Multi-format output** — pick any combination of:
  - Paragraph (long-form prose)
  - Bullet (key facts)
  - Table (structured data)
  - Summary (executive overview)
  - Diff Comparison (pros/cons, before/after)
  - Other (user-defined format)
- 💾 **Markdown download** — one-click export of the generated report
- 📋 **Session persistence** — last report stays visible across reruns

### Developer Experience

- 📁 **Clean 3-file architecture** — `app.py` (launcher) · `ui.py` (interface) · `agent.py` (logic)
- 📖 **Beginner-friendly comments** — every non-obvious line is explained
- 🔐 **Secrets via Streamlit** — no hardcoded API keys
- 🌐 **Cloud-ready** — deploy to Streamlit Community Cloud with zero config changes

---

## 5. 📝 Summary

The **AI Research Agent** is a compact, end-to-end demonstration of how to build a practical AI agent application in 2026. It takes a single user question, searches the live web for answers, and returns a report in whatever structure the user actually wants — all without requiring paid search APIs or complex infrastructure.

**Why it matters:**

- **For learners** — it's a minimal, readable blueprint for building CrewAI agents with tool use, structured prompts, and a Streamlit frontend.
- **For end users** — it turns 30–60 minutes of manual research into a 60-second wait.
- **For developers** — it shows how to handle real-world issues like rate limits, provider bugs, and dynamic prompt construction in a production-ish way.

**Next steps for extension:**

- Add multi-agent collaboration (researcher + reviewer + writer)
- Support PDF/DOCX export
- Integrate paid search APIs for higher-quality sources
- Add chat history and follow-up questions
- Stream agent thoughts to the UI in real time

---
