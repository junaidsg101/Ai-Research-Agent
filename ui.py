"""
ui.py
-----
Streamlit user interface for the AI Research Agent.

Collects from the user:
  1. A research topic (free text)
  2. A category (single choice): IT_Technology / Medical / Engineering / Other
  3. One or more output formats:
        Paragraph, Bullet, Table, Summary, Diff Comparison, Other

Then hands all of that to `agent.run_research()` and renders the resulting
Markdown report with a download button.
"""

import streamlit as st

from agent import run_research


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CATEGORIES = ["IT_Technology", "Medical", "Engineering", "Other"]

OUTPUT_FORMATS = [
    "Paragraph",         # long-form prose (user wrote "Paragraphia")
    "Bullet",            # bulleted lists
    "Table",             # Markdown table(s)
    "Summary",           # short executive summary
    "Diff Comparison",   # side-by-side / pros-vs-cons comparison
    "Other",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_secret(key: str):
    """Safely read a Streamlit secret; return None if missing."""
    try:
        return st.secrets[key]
    except Exception:
        return None


def build_format_instruction(formats: list[str], other_format_text: str) -> str:
    """
    Turn the user's format selections into a clear instruction string
    that we inject into the agent's task description.
    """
    # Replace the placeholder "Other" with whatever the user typed.
    effective = list(formats)
    if "Other" in effective:
        if other_format_text.strip():
            effective[effective.index(
                "Other")] = f"Other ({other_format_text.strip()})"
        else:
            effective.remove("Other")

    if not effective:
        return ""

    mapping = {
        "Paragraph":       "- A 'Paragraph' section: well-written prose explaining the topic in depth.",
        "Bullet":          "- A 'Bullet Points' section: concise bulleted list of the most important facts/findings.",
        "Table":           "- A 'Table' section: at least one Markdown table that organizes key data or comparisons from the research.",
        "Summary":         "- A 'Summary' section at the very top: a tight 4–6 sentence executive summary of the whole report.",
        "Diff Comparison": "- A 'Comparison' section: a clear pros/cons, before/after, or side-by-side comparison relevant to the topic (use a table or structured bullets).",
    }

    lines = [
        "The report MUST be structured into the following sections, in this order:"]
    for fmt in effective:
        if fmt in mapping:
            lines.append(mapping[fmt])
        else:
            lines.append(
                f"- An additional '{fmt}' section, formatted appropriately for that style.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
groq_api_key = get_secret("GROQ_API_KEY")

with st.sidebar:
    st.header("⚙️ About")
    if groq_api_key:
        st.success("Groq API key loaded ✅")
    else:
        st.error("GROQ_API_KEY secret not found.")
        st.caption(
            "Add it in Streamlit Cloud under **App settings → Secrets**:\n\n"
            "```toml\nGROQ_API_KEY = \"your_real_key\"\n```"
        )

    st.markdown("---")
    st.markdown("**Model:** `openai/gpt-oss-120b` (via Groq)")
    st.markdown("**Search:** DuckDuckGo (free, no key needed)")
    st.markdown("---")
    st.caption(
        "This app sends your topic to a Groq-hosted LLM and performs live "
        "DuckDuckGo web searches. Don't enter sensitive information."
    )


# ---------------------------------------------------------------------------
# Main area — title
# ---------------------------------------------------------------------------
st.title("🔎 AI Research Agent")
st.caption(
    "Single-agent researcher · CrewAI + Groq + DuckDuckGo · "
    "configure category & output format below"
)


# ---------------------------------------------------------------------------
# Main area — inputs
# ---------------------------------------------------------------------------
with st.form("research_form", clear_on_submit=False):

    topic = st.text_input(
        "📌 What topic should the agent research?",
        placeholder="e.g. The impact of AI agents on software jobs in 2026",
    )

    st.markdown("### 🗂️ Category")
    category = st.radio(
        "Select one category (helps the agent focus on the right domain):",
        CATEGORIES,
        horizontal=True,
        index=0,
    )

    category_other_text = ""
    if category == "Other":
        category_other_text = st.text_input(
            "Please specify the category:",
            placeholder="e.g. Finance, Law, Education...",
        )

    st.markdown("### 📝 Output format")
    st.caption("Pick one or more — the report will include a section for each.")
    formats = st.multiselect(
        "Output format(s):",
        OUTPUT_FORMATS,
        default=["Paragraph", "Summary"],
    )

    other_format_text = ""
    if "Other" in formats:
        other_format_text = st.text_input(
            "Describe the 'Other' format you want:",
            placeholder="e.g. Timeline, FAQ, Q&A, Infographic outline...",
        )

    submitted = st.form_submit_button(
        "🚀 Run Research",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------------------------
# Main area — run the agent
# ---------------------------------------------------------------------------
if submitted:
    # ---- Validation ----
    if not groq_api_key:
        st.error(
            "GROQ_API_KEY is not set. Add it in Streamlit Cloud under "
            "App settings → Secrets, then reload the app."
        )
        st.stop()

    if not topic.strip():
        st.error("Please enter a research topic.")
        st.stop()

    if not formats:
        st.error("Please select at least one output format.")
        st.stop()

    # ---- Resolve "Other" category ----
    effective_category = category
    if category == "Other":
        effective_category = (
            category_other_text.strip() if category_other_text.strip() else "Other"
        )

    # ---- Build the format instruction block ----
    format_instruction = build_format_instruction(formats, other_format_text)

    # ---- Run ----
    with st.spinner(
        f"Researching '{topic}' in the {effective_category} domain… "
        "this usually takes 30–90 seconds ⏳"
    ):
        try:
            report = run_research(
                topic=topic.strip(),
                groq_api_key=groq_api_key,
                category=effective_category,
                format_instruction=format_instruction,
            )
            st.session_state["last_report"] = report
            st.session_state["last_topic"] = topic.strip()
            st.session_state["last_category"] = effective_category
            st.session_state["last_formats"] = formats
        except Exception as e:
            st.error(f"Something went wrong: {e}")


# ---------------------------------------------------------------------------
# Main area — render the last report
# ---------------------------------------------------------------------------
if "last_report" in st.session_state:
    st.markdown("---")
    st.subheader(f"📄 Report: {st.session_state['last_topic']}")

    meta_cols = st.columns(2)
    with meta_cols[0]:
        st.markdown(
            f"**Category:** `{st.session_state.get('last_category', '-')}`")
    with meta_cols[1]:
        fmts = st.session_state.get("last_formats", [])
        st.markdown(f"**Formats:** {', '.join(fmts) if fmts else '-'}")

    st.markdown(st.session_state["last_report"])

    st.download_button(
        "⬇️ Download report as Markdown",
        data=st.session_state["last_report"],
        file_name=f"research_{st.session_state.get('last_topic', 'report')[:30].replace(' ', '_')}.md",
        mime="text/markdown",
        use_container_width=True,
    )
