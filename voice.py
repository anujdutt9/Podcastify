import os
import logging
from typing import Dict
from dotenv import load_dotenv
from pydantic import validate_call
from utils.voice_utils import ELEVENLABS_VOICE_MAPPING
from elevenlabs import ElevenLabs, VoiceSettings
from pydub import AudioSegment
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    logger.error("ELEVENLABS_API_KEY is not set. Please check your environment configuration.")
    raise ValueError("ELEVENLABS_API_KEY is missing. Add it to your environment variables or .env file.")


@validate_call
def get_voice_for_persona(persona: str, speaker: str) -> str:
    """
    Get the corresponding voice for the speaker based on the persona.
    If the persona or speaker is not found, default to 'Brian'.
    """
    persona_voices = ELEVENLABS_VOICE_MAPPING.get(persona, {})
    return persona_voices.get(speaker.strip("<>"), "aFqHDefrsNkoISstIlMU")


@validate_call
def generate_podcast_audio(podcast_transcript: Dict, persona: str):
    """
    Generates a podcast audio file from the JSON transcript for the given persona.
    """
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    combined_audio = AudioSegment.silent(duration=0)
    timestamps = []
    current_time = 0

    # Create the output directory if it does not exist
    if not os.path.exists("output"):
        os.makedirs("output", exist_ok=True)

    # Load intro music and add it to the combined audio
    intro_music = AudioSegment.from_file("assets/podcast_intro.mp3", format="mp3")
    combined_audio += intro_music

    # Add a pause after the intro music
    pause_duration = 1  # Pause duration in seconds
    pause_audio = AudioSegment.silent(duration=pause_duration * 1000)  # Convert seconds to milliseconds
    combined_audio += pause_audio
    current_time += (len(intro_music) + len(pause_audio)) / 1000  # Update the current time

    # Iterate over each line in the podcast transcript
    for entry in podcast_transcript.get("podcast", []):
        speaker = entry.get("speaker")
        spoken_text = entry.get("dialogue")

        if not speaker or not spoken_text:
            continue

        # Get the corresponding voice for the persona and speaker
        selected_voice = get_voice_for_persona(persona, speaker)

        # Perform the text-to-speech conversion
        audio_stream = client.text_to_speech.convert(
            voice_id=selected_voice,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=spoken_text,
            model_id="eleven_flash_v2_5",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        # Combine the audio segments
        audio_bytes = b"".join(audio_stream)
        audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        combined_audio += audio_segment

        # Add timestamp
        timestamps.append({
            "start_time": current_time,
            "end_time": current_time + len(audio_segment) / 1000,
            "speaker": speaker,
            "dialogue": spoken_text
        })

        current_time += len(audio_segment) / 1000

    # Export the combined audio to a BytesIO object
    audio_buffer = BytesIO()
    combined_audio.export(audio_buffer, format="mp3")
    audio_buffer.seek(0)

    # Export the combined audio
    persona_name = persona.replace(" ", "")
    audio_file_path = f"output/{persona_name}_podcast_audio.mp3"
    combined_audio.export(audio_file_path, format="mp3")

    return audio_file_path, timestamps

# Example usage
if __name__ == "__main__":
    from transcript import generate_podcast_transcript
    try:
        # Example file paths (replace with actual paths)
        persona_file = "prompts/magicalStoryteller_prompt.txt"
        document_text = ("The dominant sequence transduction models are based on complex recurrent or "
                         "convolutional neural networks that include an encoder and a decoder. The best"
                         "performing models also connect the encoder and decoder through an attention"
                         "mechanism. We propose a new simple network architecture, the Transformer,"
                         "based solely on attention mechanisms, dispensing with recurrence and convolutions"
                         "entirely. Experiments on two machine translation tasks show these models to"
                         "be superior in quality while being more parallelizable and requiring significantly"
                         "less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-"
                         "to-German translation task, improving over the existing best results, including"
                         "ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task,"
                         "our model establishes a new single-model state-of-the-art BLEU score of 41.8 after"
                         "training for 3.5 days on eight GPUs, a small fraction of the training costs of the"
                         "best models from the literature. We show that the Transformer generalizes well to"
                         "other tasks by applying it successfully to English constituency parsing both with"
                         "large and limited training data.")

        document_text = ""
        transcript = generate_podcast_transcript(persona_file, document_text)
        print("Generated Transcript:\n", transcript)
        audio = generate_podcast_audio(transcript, "MagicalStoryteller")
        print(f"Generated audio file: {audio}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")