import datetime

APP_NAME = "Vanguard Research"
PAGE_ICON = "🛡️"
MODEL_NAME = "gemini-2.5-flash"
USER_ROLE = "user"
ASSISTANT_ROLE = "model"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"

LOGO_SIZE_SIDEBAR = 28
SIDEBAR_COLUMN_RATIO = [0.8, 0.2]
HEADER_COLUMN_RATIO = [0.25, 0.5, 0.25]
USER_INPUT_TEXT = "Request Research Intelligence..."
SEARCH_PROMPT = "Search the Core..."
MAX_RESPONSE_TOKENS = 4000
TEMPERATURE = 0.1


def get_dynamic_system_instructions():
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return (
        f"You are {APP_NAME}, a Senior Multi-Architecture Research Assistant. Today is {current_date}. "
        "\n\n--- OPERATIONAL DIRECTIVES ---"
        "\n1. GREETING: If greeted, identify as a Research Specialist. "
        "\n2. RESEARCH: For 2025/2026 events, use Search immediately. Do not ask for clarification. "
        "\n3. FORMATTING: Deliver final reports in Markdown with bold headers and tables. Avoid meta-talk."
        "\n4. INSTRUCTION: Give complete responses. Don't give continued responses."
    )


SUGGESTIONS = {
    "optimize": {
        "label": "Technical Report",
        "icon": ":material/analytics:",
        "prompt": "Detailed report on AI advancements in software development.",
    },
    "debug": {
        "label": "Medical Insight",
        "icon": ":material/medical_services:",
        "prompt": "Briefly explain 2026 healthcare innovations.",
    },
    "news": {
        "label": "Latest Events",
        "icon": ":material/news:",
        "prompt": "Latest news of 2026.",
    },
}

BOT_FAILURE_COMMENT = "Agent failed to provide a valid synthesized report."
EVALUATION_TEMPERATURE = 0.0
EVALUATION_THRESHOLD = 0.7
FAILURE_SCORE_FALLBACK = 0.0
LANGSMITH_DATASET_NAME = "Vanguard_Research_Benchmark_Chatbot"
PROTOCOL_SCORE_KEY = "protocol_adherence"

PROTOCOL_ADHERENCE_CRITERIA = """
1. Technical Depth: Does the response provide granular facts (dates, stats, specific names)?
2. Formatting: Are bold headings used? Is a Markdown table present for schedules or comparisons?
3. Scannability: Is the report concise and professional (Lead Synthesis persona)?
4. Factuality: Does it avoid conversational filler and 'I am ready to help' phrases?
5. Multi-Agent Flow: Does it clearly show evidence of research rather than general knowledge?
"""
