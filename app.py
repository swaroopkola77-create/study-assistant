"""
Study Assistant — a Gemini-powered Gradio app.

Run locally:
    cp .env.example .env      # fill in GEMINI_API_KEY
    pip install -r requirements.txt
    python app.py
"""

import logging
import os
import sys
import time

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --------------------------------------------------------------------------
# Configuration & logging
# --------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("study-assistant")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
MAX_QUESTION_CHARS = int(os.getenv("MAX_QUESTION_CHARS", "4000"))
REQUEST_TIMEOUT_MS = int(os.getenv("REQUEST_TIMEOUT_MS", "30000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))

if not GEMINI_API_KEY:
    logger.error(
        "GEMINI_API_KEY is not set. Create a .env file (see .env.example) "
        "or set the environment variable before starting the app."
    )
    sys.exit(1)

# Fail fast if the client can't even be constructed (bad key format, etc.)
try:
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )
except Exception:
    logger.exception("Failed to initialize the Gemini client.")
    sys.exit(1)

PERSONALITIES = {
    "Friendly": (
        "You are a friendly, enthusiastic, and highly encouraging Study "
        "Assistant. Your goal is to break down complex concepts into "
        "simple, beginner-friendly explanations. Use analogies and "
        "real-world examples that beginners can relate to. Always ask a "
        "follow-up question to check understanding."
    ),
    "Academic": (
        "You are a strictly academic, highly detailed, and professional "
        "university Professor. Use precise, formal terminology and "
        "structure your response clearly (e.g. definitions, key points, "
        "examples). Your goal is still to make complex concepts "
        "understandable, so include analogies and real-world examples "
        "where useful. Always ask a follow-up question to check "
        "understanding."
    ),
}

SAFETY_SETTINGS = [
    types.SafetySetting(category=cat, threshold="BLOCK_MEDIUM_AND_ABOVE")
    for cat in (
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_DANGEROUS_CONTENT",
    )
]


# --------------------------------------------------------------------------
# Core logic
# --------------------------------------------------------------------------

def _call_gemini(question: str, system_prompt: str) -> str:
    """Call the Gemini API with retries on transient failures."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):  # e.g. MAX_RETRIES=2 -> 3 tries
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.4,
                    max_output_tokens=2000,
                    safety_settings=SAFETY_SETTINGS,
                ),
            )

            if not getattr(response, "text", None):
                # Model responded but produced no usable text (e.g. blocked
                # by safety filters, or finished with no content).
                reason = None
                if getattr(response, "candidates", None):
                    reason = getattr(response.candidates[0], "finish_reason", None)
                logger.warning("Empty response from model. finish_reason=%s", reason)
                return (
                    "I couldn't generate a response for that question "
                    "(it may have been blocked by content filters). "
                    "Try rephrasing it."
                )

            return response.text

        except APIError as e:
            last_error = e
            status = getattr(e, "code", None)
            # Retry on rate limiting / transient server errors only.
            if status in (429, 500, 503) and attempt <= MAX_RETRIES:
                wait = 2 ** attempt
                logger.warning(
                    "Gemini API error %s on attempt %d, retrying in %ds",
                    status, attempt, wait,
                )
                time.sleep(wait)
                continue
            logger.error("Gemini API error: %s", e)
            break
        except Exception as e:  # noqa: BLE001 - surface anything unexpected
            last_error = e
            logger.exception("Unexpected error calling Gemini API")
            break

    return (
        "Sorry, something went wrong while contacting the AI service. "
        f"Please try again in a moment. (Details: {last_error})"
    )


def study_assistant(question: str, persona: str) -> str:
    if not question or not question.strip():
        return "Please enter a question first."

    question = question.strip()
    if len(question) > MAX_QUESTION_CHARS:
        return (
            f"Your question is too long ({len(question)} characters). "
            f"Please limit it to {MAX_QUESTION_CHARS} characters."
        )

    if persona not in PERSONALITIES:
        persona = "Friendly"

    logger.info("Question received (persona=%s, len=%d)", persona, len(question))
    return _call_gemini(question, PERSONALITIES[persona])


# --------------------------------------------------------------------------
# Gradio UI
# --------------------------------------------------------------------------

demo = gr.Interface(
    fn=study_assistant,
    inputs=[
        gr.Textbox(
            lines=5,
            placeholder="Enter your question here...",
            label="Question",
            max_lines=15,
        ),
        gr.Radio(
            choices=list(PERSONALITIES.keys()),
            label="Personality",
            value="Friendly",
        ),
    ],
    outputs=gr.Textbox(lines=20, label="Response"),
    title="Study Assistant",
    description="Clarify your doubts using AI.",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.queue(max_size=20).launch(
        server_name=os.getenv("SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("PORT", "7860")),
        root_path=os.getenv("ROOT_PATH", ""),
    )
