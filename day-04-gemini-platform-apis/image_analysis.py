import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    ai_client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=3,
                initial_delay=2.0,
                max_delay=10.0
            )
        )
    )

    image_path = "test_image.png"

    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist in the current directory.")
        return

    with open(image_path, "rb") as file:
        image_bytes = file.read()

    print(f"Analyzing {image_path}...")

    prompt = (
        "Describe the provided image in detail. If there is text present, transcribe it in simple words. "
        "If there are individuals present, describe their actions in detail."
    )

    try:
        model_response = ai_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            ]
        )

        print("\n--- VISION ANALYSIS RESULTS ---")
        print(model_response.text.strip())

    except Exception as error:
        print(f"Vision analysis failed: {error}")


if __name__ == "__main__":
    main()
