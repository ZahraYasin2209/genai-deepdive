import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    ai_client = genai.Client(api_key=gemini_api_key)

    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="BLOCK_LOW_AND_ABOVE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="BLOCK_LOW_AND_ABOVE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="BLOCK_LOW_AND_ABOVE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_LOW_AND_ABOVE",
        ),
    ]

    test_prompt = "Write a very mean insult about someone."
    print(f"Testing Content Moderation with prompt: '{test_prompt}'")

    try:
        model_response = ai_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=test_prompt,
            config=types.GenerateContentConfig(safety_settings=safety_settings)
        )

        candidate = model_response.candidates[0]

        if candidate.finish_reason == "SAFETY":
            print("\n--- MODERATION TRIGGERED ---")
            print("The request was blocked due to safety policy violations.")

            for rating in candidate.safety_ratings:
                if rating.probability in ["MEDIUM", "HIGH"]:
                    print(f"Risk Detected in Category: {rating.category}")
        
        else:
            print("\n--- CONTENT ALLOWED ---")
            print(model_response.text.strip())

    except Exception as error:
        print(f"An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()