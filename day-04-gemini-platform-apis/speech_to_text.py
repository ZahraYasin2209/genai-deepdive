import os
import time

from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    ai_client = genai.Client(api_key=gemini_api_key)

    print(f"Uploading audio file...")
    
    uploaded_audio_file = ai_client.files.upload(file="output_audio.wav")

    print("Processing audio", end="")
    while uploaded_audio_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        uploaded_audio_file = ai_client.files.get(name=uploaded_audio_file.name)

    if uploaded_audio_file.state.name == "FAILED":
        raise ValueError("Audio file processing failed on the server.")

    print("\nTranscribing...")
    model_response = ai_client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            "Please provide a high-quality, verbatim transcription of this audio.",
            uploaded_audio_file
        ]
    )

    print("--- TRANSCRIPTION RESULTS ---")
    print(model_response.text.strip())


if __name__ == "__main__":
    main()
