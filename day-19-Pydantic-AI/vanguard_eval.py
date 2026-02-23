import asyncio
from dataclasses import dataclass

import logfire
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from test_vanguard_agent import get_agent, vanguard_server

logfire.configure(service_name="vanguard-eval-suite")


@dataclass
class LLMJudge(Evaluator):
    """Uses a second LLM to grade if the agent's answer is factually correct."""
    async def evaluate(self, ctx: EvaluatorContext) -> bool:
        judge_agent = Agent("google-gla:gemini-2.5-flash")

        instructions_prompt = (
            "You are a Senior Fact-Checker. Compare the 'Actual Output' to the 'Expected Answer'.\n"
            "Criteria: Check for semantic meaning, instead of 100% exact.\n"
            "Response Format:\n"
            "REASONING: [Explain the comparison]\n"
            "DECISION: [CORRECT/INCORRECT]\n\n"
            f"EXPECTED: {ctx.expected_output}\n"
            f"ACTUAL: {ctx.output}"
        )

        agent_response_checker = await judge_agent.run(instructions_prompt)

        return "DECISION: CORRECT" in agent_response_checker.output.upper()


cases = [
    Case(
        name="politics",
        inputs="Who is the current Chief Minister of Punjab, Pakistan?",
        expected_output="Maryam Nawaz Sharif",
    ),
    Case(
        name="sports",
        inputs="Who won the recent T20 WorldCup match between India vs. Pakistan?",
        expected_output="India won",
    ),
    Case(
        name="math_scientific", inputs="Calculate sqrt(144) * 5", expected_output="60"
    ),
    Case(name="math_basic", inputs="What is 15% of 2000?", expected_output="300"),
]


async def run_vanguard_task(question: str) -> str:
    """
    Asynchronous wrapper that executes the research agent for a single
    evaluation test case.
    """
    research_agent = get_agent()
    async with vanguard_server:
        agent_run_result = await research_agent.run(question)

        return agent_run_result.output


async def main():
    async with vanguard_server:
        print("Starting Professional Evaluation with LLM Judge...")
        agent_test_group = Dataset(cases=cases, evaluators=[LLMJudge()])
        evaluation_summary_report = await agent_test_group.evaluate(run_vanguard_task)
        evaluation_summary_report.print()


if __name__ == "__main__":
    asyncio.run(main())
