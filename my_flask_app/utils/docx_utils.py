""" Filename: docx_utils.py - Directory: my_flask_app/utils
"""
import re
import nltk
from docx import Document
from .grammar_checker import check_grammar
from .reconstructing_sentence import reconstruct_formatting

# Download necessary Punkt sentence tokenizer if not already downloaded
nltk.download("punkt", quiet=True)


def correct_text_grammar(file_path):
    """
    Corrects grammar in a DOCX file and applies original formatting to the corrected text.

    :param file_path: The path to the DOCX file to be processed.
    """
    doc = Document(file_path)
    corrections = []  # List to hold correction details

    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():  # Skip empty paragraphs
            continue

        # Get aggregated formatting for each sentence in the paragraph
        sentence_formatting_list = get_aggregated_formatting(paragraph)

        # Tokenize the paragraph's text into sentences
        sentences = nltk.tokenize.sent_tokenize(paragraph.text)
        # Clear the paragraph for reconstruction
        paragraph.clear()

        # Correct the sentences and apply formatting
        for i, sentence in enumerate(sentences):
            # print(f"\n{i}\n")
            corrected_sentence = check_grammar(sentence)

            # print(f"\n----Original Sentence----: {sentence}")
            # print(f"----Corrected Sentence---: {corrected_sentence}")
            # print(f"---Original Formatting---: {sentence_formatting_list[i]}")

            # Split the corrected sentence into runs based on original formatting
            (
                corrected_runs,
                modified_tokens,
                added_tokens,
            ) = reconstruct_formatting(
                sentence, corrected_sentence, sentence_formatting_list[i]
            )
            # Collect the correction details
            correction_details = {
                "original_sentence": sentence,
                "corrected_sentence": corrected_sentence,
                "modified_tokens": modified_tokens,
                "added_tokens": added_tokens,
            }
            corrections.append(correction_details)

            # print(f"------Corrected Runs-----: {corrected_runs}")
            # print(f"-----Modified Tokens-----: {modified_tokens}")
            # print(f"-------Added Tokens------: {added_tokens}")

            # Reconstruct the paragraph with corrected runs and their formatting
            for ci, corrected_run in enumerate(corrected_runs):
                if i != 0 and ci == 0:
                    corrected_run["text"] = " " + corrected_run["text"]
                new_run = paragraph.add_run(corrected_run["text"])
                apply_run_formatting(new_run, corrected_run)

    # Save the corrected document
    doc.save(file_path)

    # Return all corrections details
    return corrections


def get_aggregated_formatting(paragraph):
    """
    Aggregates formatting for each sentence in a paragraph.

    :param paragraph: A paragraph object from a DOCX document.
    :return: A list of formatting dictionaries for each sentence in the paragraph.
    """
    formatting_list = []
    sentence_formatting = []
    previous_formatting = {}
    combined_text = ""
    end_of_sentence = False

    for run in paragraph.runs:
        current_formatting = extract_formatting_from_run(run)
        for token in custom_tokenize(run.text):
            if token == " ":
                sentence_formatting.append(
                    {"text": combined_text, **previous_formatting}
                )
                sentence_formatting.append({"text": " ", **current_formatting})
                combined_text = ""
            else:
                previous_formatting = current_formatting
                combined_text += token

            if end_of_sentence:
                formatting_list.append(sentence_formatting)
                sentence_formatting = []

            end_of_sentence = True if "." in token else False

    if combined_text != "":
        sentence_formatting.append({"text": combined_text, **previous_formatting})
        formatting_list.append(sentence_formatting)

    return formatting_list


def extract_formatting_from_run(run):
    """
    Extracts formatting details from a run in a DOCX document.

    :param run: A run object from a DOCX paragraph.
    :return: A dictionary containing the formatting details of the run.
    """
    formatting = {}
    if run.bold:
        formatting["bold"] = True
    if run.italic:
        formatting["italic"] = True
    if run.underline:
        formatting["underline"] = True
    if run.font.size:
        formatting["font_size"] = run.font.size

    return formatting


def custom_tokenize(text):
    """
    Tokenizes a string into words, spaces, and punctuation marks.

    :param text: The string to be tokenized.
    :return: A list of tokens extracted from the string.
    """
    pattern = r'\b\w+[\w\'-]*[.,;:!?"]?|\s+|[.,;:!?"]'
    return re.findall(pattern, text)


def apply_run_formatting(run, formatting):
    """
    Applies formatting to a run in a DOCX document.

    :param run: A run object from a DOCX paragraph.
    :param formatting: A dictionary containing formatting details to apply to the run.
    """
    run.bold = formatting.get("bold")
    run.italic = formatting.get("italic")
    run.underline = formatting.get("underline")
    # Only set font size if it's explicitly provided
    if "font_size" in formatting and formatting["font_size"] is not None:
        run.font.size = formatting["font_size"]
