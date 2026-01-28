import os
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    ai_client = genai.Client(api_key=gemini_api_key)

    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )

    input_text = "Hi Zahra, Welcome to the world of AI! You are making great progress. Good Luck for your Gen AI journey ahead."
    
    try:
        model_response = ai_client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=input_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config
            )
        )

        raw_audio_data = model_response.candidates[0].content.parts[0].inline_data.data
        output_file = "output_audio.wav"
        
        with wave.open(output_file, "wb") as wav_container:
            wav_container.setnchannels(1)   
            wav_container.setsampwidth(2)     
            wav_container.setframerate(24000) 
            wav_container.writeframes(raw_audio_data)

        print(f"Success! {output_file} is ready to play.")

    except Exception as api_error:
        print(f"An error occurred during speech synthesis: {api_error}")


if __name__ == "__main__":
    main()
