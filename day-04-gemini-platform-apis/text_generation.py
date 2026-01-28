import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    ai_client = genai.Client(api_key=api_key)

    generation_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=1000,
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    )

    try:
        model_response = ai_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Who is the president of Pakistan?",
            config=generation_config
        )

        for content_part in model_response.candidates[0].content.parts:
            section_header = (
                "AI REASONING (MODEL'S THOUGHT PROCESS)"
                if content_part.thought
                else "FINAL ANSWER"
            )

            print(f"--- {section_header} ---")
            print(content_part.text.strip())

    except Exception as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
