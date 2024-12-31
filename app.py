import gradio as gr
from gradio_pdf import PDF
from pathlib import Path
from pypdf import PdfReader
from utils.prompt_utils import PERSONA_TO_PROMPT_MAPPING, PERSONA_CHOICES
from transcript import generate_podcast_transcript
from voice import generate_podcast_audio

dir_ = Path(__file__).parent


def format_transcript_readable(transcript_json):
    """
    Converts the JSON transcript into a human-readable text format.
    """
    readable_text = ""
    for entry in transcript_json.get("podcast", []):
        speaker = entry.get("speaker", "").strip("<>")
        dialogue = entry.get("dialogue", "")
        readable_text += f"{speaker}: {dialogue}\n\n"
    return readable_text.strip()


# Function to process the user's request
def process_request(document: str, persona: str):
    if document:
        # Read the uploaded PDF
        pdf_reader = PdfReader(document)
        document_text = ""
        for page in pdf_reader.pages:
            document_text += page.extract_text()
    else:
        document_text = ""

    # Generate podcast transcript and audio
    fpath_persona_prompt = PERSONA_TO_PROMPT_MAPPING.get(persona, "prompts/podcastHost_prompt.txt")
    podcast_transcript = generate_podcast_transcript(fpath_persona_prompt, document_text)

    # Format transcript for readable display
    readable_transcript = format_transcript_readable(podcast_transcript)

    # Generate Podcast Audio
    podcast_audio, _ = generate_podcast_audio(podcast_transcript, persona)

    return readable_transcript, podcast_audio


# Define the interface
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("## 🎙️ Document and Story Podcast Creator")
    # Instruction section
    instructions = gr.Markdown(
        "Upload a document to generate a podcast based on its content, or leave it empty to generate a random story podcast based on the selected persona."
    )
    with gr.Row():
        # Left panel for document upload and viewing
        with gr.Column(scale=5):
            pdf_view = PDF(label="Upload and View Document (Optional)", height=1000)

        # Right panel for podcast transcript and audio
        with gr.Column(scale=5):
            selected_persona = gr.Radio(
                choices=PERSONA_CHOICES,
                label="Select a Persona",
                value=PERSONA_CHOICES[0],
            )
            transcript_output = gr.Textbox(
                label="Generated Podcast Transcript",
                interactive=False,
                lines=20,
            )
            audio_output = gr.Audio(label="Generated Podcast Audio", interactive=False)
            submit_btn = gr.Button("Generate Podcast")


    # Dynamic instruction text based on document upload
    def update_instructions(pdf_file, persona):
        if pdf_file:
            return (
                f"📄 A document is uploaded. The podcast will be based on your document content "
                f"and narrated in the style of a {persona}."
            )
        else:
            return (
                f"📝 No document uploaded. A random story will be generated and narrated in the style of a {persona}."
            )

    # Update the button label dynamically
    def update_button_label(pdf_file):
        return "Generate Podcast from Document" if pdf_file else "Generate Random Podcast"

    # Event handling
    submit_btn.click(
        fn=process_request,
        inputs=[pdf_view, selected_persona],
        outputs=[transcript_output, audio_output],
    )

    # Update instructions and button dynamically
    pdf_view.change(fn=update_instructions, inputs=[pdf_view, selected_persona], outputs=[instructions])
    pdf_view.change(fn=update_button_label, inputs=[pdf_view], outputs=[submit_btn])


# Launch the app
if __name__ == "__main__":
    demo.launch()