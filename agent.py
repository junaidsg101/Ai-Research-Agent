"""
agent.py
--------
Defines:
  1. A free DuckDuckGo search tool (no API key needed).
  2. A single CrewAI Agent ("Senior Research Analyst").
  3. A single Task that tells the agent how to research and write the report.
  4. A `run_research()` function that the Streamlit UI calls.
"""

import time

import litellm
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from ddgs import DDGS


# ---------------------------------------------------------------------------
# WORKAROUND for crewai cache_breakpoint bug (see previous version).
# ---------------------------------------------------------------------------
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda message: dict(message)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1. THE SEARCH TOOL
# ---------------------------------------------------------------------------
@tool("DuckDuckGo Search")
def duckduckgo_search(query: str) -> str:
    """
    Searches the web using DuckDuckGo and returns the top results
    (title, link, and a short snippet for each). Use this whenever you
    need current information, facts, statistics, or context about a topic.
    Call it several times with different, specific queries to gather
    enough material for a good report.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
    except Exception as exc:
        return f"Search failed for query '{query}': {exc}"

    if not results:
        return f"No results found for '{query}'."

    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        link = r.get("href", "")
        snippet = r.get("body", "")[:220]
        formatted.append(f"{i}. {title}\n   Link: {link}\n   {snippet}")

    return "\n\n".join(formatted)


# ---------------------------------------------------------------------------
# 2 & 3. BUILDING THE AGENT, TASK AND CREW
# ---------------------------------------------------------------------------
def build_crew(
    topic: str,
    groq_api_key: str,
    category: str = "General",
    format_instruction: str = "",
) -> Crew:
    """Creates and returns a single-agent Crew ready to research `topic`."""

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=groq_api_key,
        temperature=0.5,
        max_completion_tokens=1500,   # bumped a bit to fit multi-format reports
    )

    researcher = Agent(
        role="Senior Research Analyst",
        goal=(
            f"Research the topic '{topic}' (domain: {category}) thoroughly "
            "using web search, and produce an accurate, well-organized, "
            "up-to-date report in the exact structure requested by the user."
        ),
        backstory=(
            "You are a meticulous research analyst with years of experience "
            "turning messy web search results into clear, trustworthy reports "
            "for a general audience. You always double-check facts and cite "
            "your sources. You are especially careful to respect the exact "
            "output structure the user asks for."
        ),
        tools=[duckduckgo_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,   # slightly higher — multi-format reports need more steps
    )

    # Build the task description dynamically.
    description_parts = [
        f"Research the topic: '{topic}'.",
        f"Domain / category: {category}.",
        "",
        "Follow these steps:",
        "1. Use the DuckDuckGo Search tool multiple times with different, "
        "specific queries to gather up-to-date facts, figures, and "
        "different perspectives on the topic.",
        "2. Cross-check important claims against more than one source when possible.",
        "3. Write a clear, well-structured report in Markdown.",
        "",
        "The final report MUST include:",
        "- A short introduction to the topic",
        "- Key findings, organized under clear headings/subheadings",
        "- Relevant facts, statistics, or recent developments you found",
        "- A 'Sources' section at the end listing the links you actually used",
    ]

    if format_instruction.strip():
        description_parts += [
            "",
            "=== REQUIRED OUTPUT STRUCTURE ===",
            format_instruction.strip(),
            "=== END REQUIRED OUTPUT STRUCTURE ===",
            "",
            "Make sure each requested section is present and clearly labeled "
            "with a Markdown heading. Do NOT skip any requested section.",
        ]

    research_task = Task(
        description="\n".join(description_parts),
        expected_output=(
            "A well-formatted Markdown report, roughly 600–1200 words, "
            "with an introduction, the user-requested sections (Paragraph / "
            "Bullet / Table / Summary / Comparison / etc.), a conclusion, "
            "and a Sources section containing real links returned by the "
            "search tool."
        ),
        agent=researcher,
    )

    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew


def run_research(
    topic: str,
    groq_api_key: str,
    category: str = "General",
    format_instruction: str = "",
) -> str:
    """
    Public function used by the Streamlit UI.
    Builds a crew for the given topic, runs it, and returns the final
    report text. Retries a couple of times if Groq's free-tier TPM
    limit is hit.
    """
    max_attempts = 3
    wait_seconds = 20

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        crew = build_crew(
            topic=topic,
            groq_api_key=groq_api_key,
            category=category,
            format_instruction=format_instruction,
        )
        try:
            result = crew.kickoff()
            return str(result)
        except litellm.RateLimitError as exc:
            last_error = exc
            if attempt < max_attempts:
                time.sleep(wait_seconds)
                wait_seconds *= 2

    raise RuntimeError(
        "Groq's free-tier rate limit (tokens per minute) was hit several "
        "times in a row. Wait about a minute and try again, or try a more "
        "specific/narrower topic so the agent needs fewer search steps."
    ) from last_error
