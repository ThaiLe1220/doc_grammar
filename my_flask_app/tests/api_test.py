import re
import requests

API_URL = "https://polite-horribly-cub.ngrok-free.app/generate_code"


def clean_api_response(api_response_text: str, original_text: str) -> str:
    """
    Cleans and formats the API response text based on the original text's structure.

    Args:
        api_response_text (str): The raw text response from the grammar checking API.
        original_text (str): The original text that was submitted for grammar checking.

    Returns:
        str: Cleaned and formatted text that reflects the corrections from the API,
             while maintaining the original text's structural and punctuation patterns.
    """
    # Remove excessive newlines and trim whitespace
    cleaned_text = api_response_text

    return cleaned_text


def check_grammar(original_text: str) -> str:
    """
    Checks and corrects the grammar of a given text using an external API.

    Args:
        original_text (str): The text to be checked and corrected for grammar.

    Raises:
        GrammarCheckError: An error raised if there is an issue with the grammar checking API call.

    Returns:
        str: The corrected version of the original text with improved grammar.
    """
    try:
        prompt = f"Correct english: {original_text}"
        print("\n[Request Sent]:", prompt)

        response = requests.get(
            API_URL,
            params={
                "prompts": prompt,
                "max_length": 128,
            },
            timeout=10,  # Timeout in 10 seconds
        )
        api_response = response.json()
        print("[API Response]:", api_response)

        corrected_text = api_response[0] if api_response else "Correction unavailable"

        # Clean the API response to extract the corrected sentence
        corrected_text = clean_api_response(corrected_text, original_text)

        print("[Corrected Text]:", corrected_text)
        return corrected_text
    except Exception as error:
        print("Error calling grammar check API:", error)


original = (
    # "1. Hello This is Eugene, and today is a very good day kkkk dont you think so ."
    "School of Science, Engineering & Technology, RMIT University, Vietnam"
)


corrected = check_grammar(original)
