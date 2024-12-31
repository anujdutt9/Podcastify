import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict
from pydantic import validate_call
from textwrap import dedent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API Key
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set. Please check your environment configuration.")
    raise ValueError("OPENAI_API_KEY is missing. Add it to your environment variables or .env file.")

# Paths for default files
DEFAULT_GUIDELINES_PATH = Path("prompts/guidelines_prompt.txt")

def read_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    path = Path(file_path)
    if not path.is_file():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    logger.info(f"Reading file: {file_path}")
    return path.read_text().strip()

@validate_call
def validate_inputs(fpath_persona_prompt: str, document_text: Optional[str]) -> None:
    """Validates inputs to ensure required data is provided."""
    if not document_text:
        logger.error("Document text is empty or missing.")
        raise ValueError("Document text must be provided.")
    if not Path(fpath_persona_prompt).is_file():
        logger.error(f"Persona prompt file not found: {fpath_persona_prompt}")
        raise FileNotFoundError(f"Persona prompt file not found: {fpath_persona_prompt}")


@validate_call
def generate_podcast_transcript(
    fpath_persona_prompt: str,
    document_text: str,
    guidelines_path: str = DEFAULT_GUIDELINES_PATH
) -> Dict:
    """
    Generates a podcast transcript based on persona and guidelines.
    """
    validate_inputs(fpath_persona_prompt, document_text if document_text else "dummy_text")

    # Read persona and guidelines
    persona_prompt = read_file(fpath_persona_prompt)
    guidelines_prompt = read_file(guidelines_path)

    # Prepare the system instructions
    system_template = PromptTemplate(
        input_variables=["persona_instructions", "guidelines_instructions"],
        template=dedent("""
            {persona_instructions}

            {guidelines_instructions}
            """)
    )
    system_instructions = system_template.format(
        persona_instructions=persona_prompt.strip(),
        guidelines_instructions=guidelines_prompt.strip()
    )

    # Prepare the human prompt template
    # If the document text is provided, use it as the base for the podcast conversation
    if document_text:
        human_template = PromptTemplate(
            input_variables=["document_text"],
            template=dedent("""
            Below is the document text you should base the podcast conversation on:
        
            "{document_text}"
        
            Please create a podcast-style transcript as described.
            """)
        )
        human_message = HumanMessage(content=human_template.format(document_text=document_text))
    else:
        # Create a new prompt to generate a random story based on the provided persona
        random_story_template = dedent("""
        Using the provided persona description, create a random, engaging story that aligns with the persona's characteristics and style.
        The story should be immersive, creative, and suitable for a podcast-style transcript.
        """)
        human_message = HumanMessage(content=random_story_template)

    # Create the ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_instructions),
        human_message,
    ])

    # Format the prompt
    prompt_instance = prompt.format_messages()

    # Debugging: Print the prompt to verify
    logger.debug(f"Formatted Prompt Instance: {prompt_instance}")

    # Initialize the LLM
    llm = ChatOpenAI(
        model_name=os.getenv("OPENAI_MODEL"),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS")),
        temperature=float(os.getenv("OPENAI_TEMPERATURE")),
    )

    # Bind the response format
    llm = llm.bind(response_format={"type": "json_object"})

    # Generate and parse response
    try:
        logger.info("Generating podcast transcript...")
        parser = JsonOutputParser()
        response = llm.invoke(prompt_instance)
        transcript = parser.parse(response.content)
        logger.info("Transcript generation successful.")
        return transcript
    except Exception as e:
        logger.exception("Failed to generate podcast transcript.")
        raise RuntimeError(f"Error generating podcast transcript: {e}")


# Example usage
if __name__ == "__main__":
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
    except Exception as e:
        logger.error(f"An error occurred: {e}")