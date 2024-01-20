""" Filename: grammar_checker.py - Directory: my_flask_app/utils

This module provides functions for checking and correcting the grammar of a given text
using an external API. It includes functions for cleaning and formatting the API response
and handling potential errors during the grammar check.

"""
import re
import requests
import aiohttp
from .exceptions import GrammarCheckError

API_URL = "https://polite-horribly-cub.ngrok-free.app/generate_code"


def clean_api_response(api_response_text: str, original_text: str) -> str:
    # Patterns that might be introduced by the API and not part of the original text
    patterns_to_remove = [
        r"Correct.*",
        r"Incorrect.*",
        r"\d+\.\d+.*",  # Match any numerical value followed by any text
        r"Identify and.*",
        r"Please explain the.*",
        r"Please note that the.*",
        r"Can you explain why the.*",
        r"Here's the corrected text.*",
        r"Correct english of this text.*",
        r"Please correct the following.*",
        r"Correct English in the following text.*",
        r"Please let me know if you need anything.*",
        r"Please explain the corection you made and why.*",
        r"Please note that the text has been modified to improve readability and clarity.*",
        r"Please note that the above text is just an example and the actual text you want to corect may contain diferent erors.*",
    ]

    for pattern in patterns_to_remove:
        # Use a conditional regex to ensure the pattern is not part of the original text
        pattern_regex = f"(?<!{re.escape(original_text)}){pattern}"
        api_response_text = re.sub(
            pattern_regex, "", api_response_text, flags=re.IGNORECASE | re.DOTALL
        )

    # Remove excessive newlines and trim whitespace
    cleaned_text = re.sub(r"[\n\s]+", " ", api_response_text).strip()

    # Check if original text starts/ends with quotation marks and remove them if not
    if not (original_text.startswith('"') and original_text.endswith('"')):
        cleaned_text = re.sub(r'^["\']+|["\']+$', "", cleaned_text)

    # Check if original text starts with numbering like '1. ' and remove it if not
    if not re.match(r"^\d+\.\s+", original_text):
        cleaned_text = re.sub(r"^\d+\.\s+", "", cleaned_text)

    # Define known punctuation marks
    known_punctuation_marks = [".", "!", "?", ":", ";"]

    # End with the same punctuation mark as the original text, if it has one
    ending_punctuation = None
    for punctuation_mark in known_punctuation_marks:
        if original_text.endswith(punctuation_mark):
            ending_punctuation = punctuation_mark
            break

    # Remove existing end punctuation from cleaned text
    cleaned_text = re.sub(r"[.!?]+$", "", cleaned_text)

    # Add appropriate punctuation mark or default to a period
    if ending_punctuation:
        # Ensure only one instance of the punctuation mark
        cleaned_text = cleaned_text.rstrip(ending_punctuation) + ending_punctuation
    else:
        # Default to a period if no known punctuation mark is found
        cleaned_text += "."

    return cleaned_text


def extract_and_preserve(text: str):
    # Pattern to match all content within parentheses
    reference_pattern = r"\(([^)]+)\)"
    # Pattern for special patterns
    special_pattern = r"\(([^)]+)\)"
    # special_pattern = r"(?:\d+|[a-zA-Z])[/;).>\-\+\\]"

    # Find all matches of the patterns
    references = re.findall(reference_pattern, text)
    specials = re.findall(special_pattern, text)

    # Replace each found reference and special pattern with placeholders
    for ref in references:
        text = text.replace(f"({ref})", "(REFERENCE)", 1)

    for special in specials:
        text = text.replace(special, "(SPECIAL)", 1)

    return text, references, specials


def insert_back(text: str, references: list, specials: list):
    # Placeholder pattern for references
    ref_placeholder_pattern = re.compile(
        r"\([^\)]*REFEREN[CS]ES?[^\)]*\)", re.IGNORECASE
    )
    # Placeholder for special patterns
    special_placeholder = "(SPECIAL)"

    for ref in references:
        text = ref_placeholder_pattern.sub("(" + ref + ")", text, 1)

    for special in specials:
        text = text.replace(special_placeholder, special, 1)

    return text


async def check_grammar(original_text: str, session) -> str:
    try:
        # print("\n[Original Text]\n", original_text)
        # Existing logic for extracting references and placeholders
        text_for_api, references, specials = extract_and_preserve(original_text)

        prompt = f"Correct english of this text: {text_for_api}"
        # print("[Request Sent]\n", prompt)

        async with session.get(
            API_URL, params={"prompts": prompt, "max_length": 64}, timeout=20
        ) as response:
            if response.status != 200:
                error_body = await response.text()
                print(f"API Error Response: {error_body}")
                raise GrammarCheckError(
                    f"API responded with error code: {response.status}"
                )
            api_response = await response.json()
            # print("[API Response]\n", api_response)

            corrected_text = api_response[0] if api_response else original_text

            # Logic for inserting references back and cleaning the response
            corrected_text_with_refs = insert_back(corrected_text, references, specials)
            final_corrected_text = clean_api_response(
                corrected_text_with_refs, original_text
            )

            # print("[Corrected Text]\n", final_corrected_text)
            return final_corrected_text
    except Exception as error:
        print("Error calling grammar check API:", error)
        return original_text
