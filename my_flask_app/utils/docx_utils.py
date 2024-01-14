""" Filename: docx_utils.py - Directory: my_flask_app/utils
"""
import nltk
from docx import Document
from .grammar_checker import check_grammar
from .reconstructing_sentence import *

# Download necessary Punkt sentence tokenizer if not already downloaded
nltk.download("punkt", quiet=True)


def correct_text_grammar(file_path):
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip() or paragraph.style.name == "EndNote Bibliography":
            continue

        corrected_para = ""

        para_word_count = len(paragraph.text.split())
        # print(f"\n--Paragraph--: [{para_word_count}] {paragraph.text}")
        if para_word_count <= 64:
            corrected_para = check_grammar(paragraph.text)

        else:
            sentences = nltk.tokenize.sent_tokenize(paragraph.text)
            for i, original_sentence in enumerate(sentences):
                corrected_sentence = check_grammar(original_sentence) + " "
                corrected_para += corrected_sentence

        # print(f"[Before Correction] paragraph.text: {paragraph.text}")
        # print(f"----------Corrected Para----------: {corrected_para}")

        correct_paragraph(corrected_para, paragraph)
        # print(f"[After Correction] paragraph.text: {paragraph.text}")

    doc.save(file_path)

    return []


def correct_paragraph(corrected_para, paragraph):
    modifications = find_modified_text(paragraph.text, corrected_para)
    paragraph_tokens = custom_tokenize(paragraph.text)
    # print("\nParagraph Tokens:", paragraph_tokens)

    modifications_dict = {item[2]: (item[0], item[1]) for item in modifications}
    # print("\nModifications Dictionary:", modifications_dict)

    current_token_index = 0
    current_pos = 0

    for run_index, run in enumerate(paragraph.runs):
        # print(f"\nProcessing run {run_index} (Text: '{run.text}')")
        new_run_text = ""
        run_start_pos = current_pos
        run_end_pos = current_pos + len(run.text)

        while current_token_index < len(paragraph_tokens) and current_pos < run_end_pos:
            token = paragraph_tokens[current_token_index]
            token_end_pos = current_pos + len(token)
            # print(
            #     f"  Current token: '{token}' (Index: {current_token_index}, Positions: {current_pos}-{token_end_pos})"
            # )

            if current_token_index in modifications_dict:
                original, modified = modifications_dict[current_token_index]
                # print(f"    Modification found: '{original}' -> '{modified}'")

                if token_end_pos <= run_end_pos:
                    # print(f"    Applying full modification to run {run_index}")
                    new_run_text += modified
                    current_token_index += 1
                    current_pos = token_end_pos
                elif run_start_pos < token_end_pos and current_pos < run_end_pos:
                    partial_mod_length = run_end_pos - current_pos
                    # print(
                    #     f"    Applying partial modification to run {run_index}: '{modified[:partial_mod_length]}'"
                    # )
                    new_run_text += modified[:partial_mod_length]

                    if len(original) > partial_mod_length:
                        modifications_dict[current_token_index] = (
                            original[partial_mod_length:],
                            modified[partial_mod_length:],
                        )
                    else:
                        # print("    Skipping token, not in current run")
                        current_token_index += 1

                    current_pos = run_end_pos
                else:
                    break
            else:
                if run_start_pos <= current_pos < run_end_pos:
                    # print(f"    Adding unmodified token: '{token}'")
                    new_run_text += token
                    current_token_index += 1
                    current_pos = token_end_pos
                else:
                    # print("    Token not in current run, moving to next run")
                    break

        run.text = new_run_text
        current_pos = run_end_pos
        # print(f"  Updated run {run_index} text: '{run.text}'")


def find_modified_text(original_text, corrected_text):
    mod = []
    ori_tokens = custom_tokenize(original_text)
    cor_tokens = custom_tokenize(corrected_text)

    ori_matrix = [[token, index] for index, token in enumerate(ori_tokens)]
    cor_matrix = [[token, index] for index, token in enumerate(cor_tokens)]

    temp_mod = find_modified_tokens(ori_matrix, cor_matrix)

    # TODO: replace ori_tokens with mod and then rerun the find_modified_tokens again to improve correctness....
    for item in temp_mod:
        index = item[2]
        ori_tokens[index] = item[1]

    updated_ori_matrix = [[token, index] for index, token in enumerate(ori_tokens)]

    mod = find_modified_tokens(updated_ori_matrix, cor_matrix)
    combined_list = temp_mod + mod

    final_mod = sorted(list(set(combined_list)), key=lambda x: x[2])
    final_mod = [item for item in final_mod if item[0] != item[1]]

    return final_mod


def find_modified_tokens(ori, cor):
    """
    Identifies modifications between original and corrected texts.

    Args:
        ori (list): Original text represented as a list of [token, position] pairs.
        cor (list): Corrected text represented as a list of [token, position] pairs.

    Returns:
        list: A list of tuples of modifications (original_token, modified_token, position).
    """
    ori_index = cor_index = 0
    mod = []

    while ori_index < len(ori) and cor_index < len(cor):
        # print(f"Current Iteration: {ori_index}, {cor_index}")
        ori_token, ori_pos = ori[ori_index]
        cor_token, _ = cor[cor_index]

        if ori_token == cor_token:
            # Tokens are identical, move to the next pair
            ori_index += 1
            cor_index += 1
        else:
            if ori_index + 4 < len(ori) and cor_index + 4 < len(cor):
                if ori[ori_index + 4][0] == cor[cor_index + 2][0]:
                    mod.append((ori_token, "", ori_pos))
                    mod.append((" ", "", ori_pos + 1))
                    mod.append((ori[ori_index + 2][0], cor_token, ori_pos + 2))

                    ori_index += 3
                    cor_index += 1
                    continue
                elif ori[ori_index + 2][0] == cor[cor_index + 2][0]:
                    mod.append((ori_token, cor_token, ori_pos))
                    ori_index += 1
                    cor_index += 1
                    continue
                elif ori[ori_index + 2][0] == cor[cor_index + 4][0]:
                    mod.append(
                        (ori_token, cor_token + " " + cor[cor_index + 2][0], ori_pos)
                    )
                    ori_index += 1
                    cor_index += 3
                    continue
                elif (
                    ori[ori_index + 2][0] != cor[cor_index + 2][0]
                    and ori[ori_index + 4][0] == cor[cor_index + 4][0]
                ):
                    mod.append((ori_token, cor_token, ori_pos))
                    mod.append(
                        (ori[ori_index + 2][0], cor[cor_index + 2][0], ori_pos + 2)
                    )
                    ori_index += 3
                    cor_index += 3

                else:
                    ori_index += 1
                    cor_index += 1
            else:
                # Handle end-of-text cases
                if len(ori) - ori_index == len(cor) - cor_index:
                    mod.append((ori_token, cor_token, ori_pos))
                    ori_index += 1
                    cor_index += 1
                elif len(ori) - ori_index > len(cor) - cor_index:
                    mod.append((ori_token, "", ori_pos))
                    mod.append((" ", "", ori_pos + 1))
                    mod.append((ori[ori_index + 2][0], cor_token, ori_pos + 2))
                    ori_index += 3
                    cor_index += 1
                else:
                    mod.append(
                        (
                            ori_token,
                            cor_token + " " + cor[cor_index + 2][0],
                            ori_pos,
                        )
                    )
                    ori_index += 1
                    cor_index += 3

    return mod
