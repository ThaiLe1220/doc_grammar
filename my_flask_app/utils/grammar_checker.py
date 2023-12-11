# Filename: grammar_checker.py - Directory: my_flask_app/utils
import re
import requests

API_URL = "https://3c92-103-253-89-37.ngrok-free.app/generate_code"


def clean_api_response(api_response_text: str, original_text: str) -> str:
    # Remove excessive newlines and trim whitespace
    cleaned_text = re.sub(r"[\n\s]+", " ", api_response_text).strip()

    # Check if original text starts/ends with quotation marks and remove them if not
    if not (original_text.startswith('"') and original_text.endswith('"')):
        cleaned_text = re.sub(r'^["\']+|["\']+$', "", cleaned_text)

    # Check if original text starts with numbering like '1. ' and remove it if not
    if not re.match(r"^\d+\.\s+", original_text):
        cleaned_text = re.sub(r"^\d+\.\s+", "", cleaned_text)

    # Trim the corrected text if it's significantly longer than the original
    original_word_count = len(original_text.split())
    corrected_words = cleaned_text.split()
    if len(corrected_words) > original_word_count * 1.5:
        cleaned_text = " ".join(corrected_words[:original_word_count])

    # Count periods at the end of the original text
    period_count = (
        len(re.findall(r"\.+$", original_text)[0])
        if re.findall(r"\.+$", original_text)
        else 1
    )

    # Ensure the corrected sentence ends with the same number of periods as the original
    cleaned_text = re.sub(r"\.+$", "", cleaned_text) + "." * period_count

    return cleaned_text


def check_grammar(original_text: str) -> str:
    try:
        prompt = f"Correct english of this sentence: {original_text}. Here is the corrected version."
        # print("\n[Request Sent]:", prompt)

        response = requests.get(
            API_URL,
            params={
                "prompts": prompt,
                "max_length": 64,
            },
        )
        api_response = response.json()
        # print("[API Response]:", api_response)

        corrected_text = api_response[0] if api_response else "Correction unavailable"

        # Clean the API response to extract the corrected sentence
        corrected_text = clean_api_response(corrected_text, original_text)

        # print("[Corrected Text]:", corrected_text)
        return corrected_text
    except Exception as error:
        print("Error calling grammar check API:", error)
        raise
