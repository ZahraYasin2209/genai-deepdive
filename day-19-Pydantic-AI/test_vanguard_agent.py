import asyncio
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


load_dotenv()


vanguard_server = MCPServerStdio(
    command="python", args=["vanguard_mcp_bridge.py"], env=os.environ.copy()
)


def get_agent():
    """Provides a configured Pydantic AI agent with real-time research capabilities."""
    return Agent(
        "google-gla:gemini-2.5-flash",
        retries=3,
        toolsets=[vanguard_server],
        model_settings={"temperature": 0.0},
        system_prompt=(
            "# IDENTITY\n"
            "You are Vanguard Research, a high-precision intelligence agent providing verified, real-time data.\n\n"
            "# PROTOCOL\n"
            "You must follow this 'Tool-First' reasoning process for every query:\n"
            "1. ANALYSIS: Determine if the query involves current events, recent news, volatile facts or complex math.\n"
            "2. EXECUTION:\n"
            " - For ANY factual request involving real-time information or events likely to have changed since your last training update: Call 'web_search' immediately.\n"
            " - For ANY numerical calculation or mathematical formula: Call 'calculator'.\n"
            "3. SYNTHESIS: Base 100% of your response on the tool's output. If a tool returns no data, report that clearly rather than speculating.\n\n"
            "# GUARDRAILS\n"
            " - NO DISCLOSURES: Never mention knowledge cutoff, training dates.\n"
            " - NO FILLER: Avoid preambles like 'Sure,' or 'Based on my research.' Start directly with the answer.\n"
            " - NO HALLUCINATIONS: If the tool provides a specific name or a score, use it exactly as provided.\n"
            "# OUTPUT FORMAT\n"
            " - Use concise, technical bullet points.\n"
            " - Use Markdown (headings, bold text, tables) for structure."
        ),
    )


async def main():
    agent = get_agent()
    async with vanguard_server:
        result = await agent.run(
            "Who is the current Prime Minister of Punjab, Pakistan?"
        )
        print(f"Agent Output: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
