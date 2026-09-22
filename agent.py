"""
agent.py (PydanticAI + OpenAI Version - Streamlit Cloud Safe)
-------------------------------------------------------------
Uses environment variable injection to bypass internal pydantic-ai import errors.
"""

import os
import time
from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from duckduckgo_search import DDGS
import openai


# ---------------------------------------------------------------------------
# 1. THE SEARCH TOOL
# ---------------------------------------------------------------------------
def duckduckgo_search(query: str) -> str:
    """
    Searches the web using DuckDuckGo. Use this whenever you need current 
    information, facts, or context. Call it multiple times with specific queries.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
    except Exception as exc:
        return f"Search failed for query '{query}': {exc}"

    if not results:
        return f"No results found for '{query}'."

    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        link = r.get("href", "")
        snippet = r.get("body", "")[:250]
        formatted.append(f"{i}. {title}\n   Link: {link}\n   {snippet}")

    return "\n\n".join(formatted)


# ---------------------------------------------------------------------------
# 2. STRUCTURED OUTPUT MODEL (Guarantees perfect Markdown structure)
# ---------------------------------------------------------------------------
class ReportSection(BaseModel):
    heading: str = Field(
        description="The Markdown heading for this section (e.g., 'Key Findings', 'Market Trends')")
    content: str = Field(
        description="The detailed Markdown content for this section. Use bullet points or paragraphs as appropriate.")


class ResearchReport(BaseModel):
    introduction: str = Field(
        description="A concise 1-2 paragraph introduction to the topic.")
    sections: List[ReportSection] = Field(
        description="The core body of the report, broken into logical sections with headings.")
    conclusion: str = Field(
        description="A brief summary wrapping up the key takeaways.")
    sources: List[str] = Field(
        description="A list of the actual URLs/links you used from the search tool.")


def format_report_to_markdown(report: ResearchReport) -> str:
    """Converts the structured Pydantic model into a clean Markdown string."""
    md_parts = [
        "## Introduction",
        report.introduction,
        ""
    ]

    for section in report.sections:
        md_parts.append(f"## {section.heading}")
        md_parts.append(section.content)
        md_parts.append("")

    md_parts.extend([
        "## Conclusion",
        report.conclusion,
        "",
        "## Sources"
    ])

    for src in report.sources:
        md_parts.append(f"- {src}")

    return "\n".join(md_parts)


# ---------------------------------------------------------------------------
# 3. BUILDING AND RUNNING THE AGENT
# ---------------------------------------------------------------------------
def run_research(
    topic: str,
    api_key: str,
    category: str = "General",
    format_instruction: str = "",
) -> str:
    """
    Public function used by the Streamlit UI.
    Builds a PydanticAI agent, runs it, and returns the final Markdown report.
    """

    # FIX: Inject the API key into the environment so pydantic-ai can find it 
    # without needing to import the internal OpenAIModel class.
    os.environ["OPENAI_API_KEY"] = api_key

    # 2. Build the System Prompt
    system_prompt = f"""
    You are an expert Research Analyst. Your job is to research the topic: '{topic}' 
    (Domain: {category}).
    
    INSTRUCTIONS:
    1. You MUST use the `duckduckgo_search` tool multiple times with different, 
       specific queries to gather up-to-date facts and perspectives.
    2. Cross-check important claims.
    3. Extract the actual URLs from the search results to use in your 'sources' list.
    """

    if format_instruction.strip():
        system_prompt += f"""
        ADDITIONAL FORMATTING REQUIREMENTS:
        {format_instruction.strip()}
        Ensure these specific requirements are met in your 'sections' output.
        """

    # 3. Initialize the PydanticAI Agent using the string model name
    # This completely bypasses the `from pydantic_ai.models.openai import OpenAIModel` error.
    agent = Agent(
        'openai:gpt-4o',  # String initialization is universally supported
        system_prompt=system_prompt,
        tools=[duckduckgo_search],
        result_type=ResearchReport,  # Forces the LLM to output valid JSON matching our schema
        model_settings={"temperature": 0.4, "max_tokens": 2000}
    )

    # 4. Execute with Retry Logic for OpenAI Rate Limits
    max_attempts = 3
    wait_seconds = 15
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            # Run the agent. PydanticAI handles the tool-calling loop internally.
            result = agent.run_sync(
                user_prompt=f"Please research and generate the final structured report for: {topic}"
            )

            # Convert the validated Pydantic object into a Markdown string
            final_markdown = format_report_to_markdown(result.data)
            return final_markdown

        except openai.RateLimitError as exc:
            last_error = exc
            if attempt < max_attempts:
                time.sleep(wait_seconds)
                wait_seconds *= 2
            else:
                raise RuntimeError(
                    "OpenAI's rate limit was hit multiple times. "
                    "Please wait a minute and try again, or use a narrower topic."
                ) from exc

        except Exception as exc:
            # Catch any other unexpected PydanticAI/OpenAI errors
            last_error = exc
            if attempt < max_attempts:
                time.sleep(5)
            else:
                raise RuntimeError(
                    f"Agent failed after {max_attempts} attempts: {exc}") from exc