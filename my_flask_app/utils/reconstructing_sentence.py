""" Filename: reconstruct_sentence.py - Directory: my_flask_app/utils

This file contains utility functions used for tokenizing sentences, 
finding the longest common subsequence of tokens between two sentences, 
calculating percentage difference between tokens, 
and reconstructing the formatting of a corrected sentence based on its original formatting.

"""
import re


def custom_tokenize(text):
    pattern = r"\(\w+[\w\'-]*\)?|[().,;:!?\"]|\b\w+[\w\'-]*(?:’s)?[().,;:!?\"]?|\s+"
    return re.findall(pattern, text)


def longest_common_subsequence(str1, str2):
    """
    Calculates the length of the longest common subsequence between two strings.

    This function uses dynamic programming to build a matrix (dp) that represents
    the lengths of the longest common subsequences for substrings of str1 and str2.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        int: The length of the longest common subsequence between str1 and str2.
    """
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if str1[i] == str2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[m][n]


def percentage_difference(str1, str2):
    """
    Calculates the percentage difference between two strings based on their longest common subsequence.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        float: The percentage difference between the two strings.
    """
    lcs_length = longest_common_subsequence(str1, str2)
    total_length = len(str1) + len(str2)
    diff_length = total_length - 2 * lcs_length
    percentage_diff = (diff_length / total_length) * 100
    return percentage_diff


def longest_common_subsequence_sentences(tokens1, tokens2):
    """
    Identifies the longest common subsequence of tokens between two lists of tokens.

    This function uses dynamic programming to find the longest subsequence of similar tokens
    between two lists of tokens. It uses a threshold for similarity based on percentage difference.

    Args:
        tokens1 (list): The first list of tokens.
        tokens2 (list): The second list of tokens.

    Returns:
        list: A list of tuples representing similar tokens in the subsequence.
    """
    m, n = len(tokens1), len(tokens2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    longest_subseq_end = (0, 0)  # Track position where longest subsequence ends.

    for i in range(m):
        for j in range(n):
            # Consider tokens similar if their percentage difference is less than 45%
            if percentage_difference(tokens1[i], tokens2[j]) < 1:
                dp[i + 1][j + 1] = dp[i][j] + 1
                if dp[i + 1][j + 1] > dp[longest_subseq_end[0]][longest_subseq_end[1]]:
                    longest_subseq_end = (i + 1, j + 1)
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    # Backtrack to extract the actual tokens in the subsequence
    i, j = longest_subseq_end
    consecutive_tokens = []
    while i > 0 and j > 0:
        # Consider tokens similar if their percentage difference is less than 45%
        if percentage_difference(tokens1[i - 1], tokens2[j - 1]) < 1:
            consecutive_tokens.append((tokens1[i - 1], tokens2[j - 1]))
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return consecutive_tokens[::-1]  # Reverse the list to maintain original order


def get_similar_tokens_in_sentences(sentence1, sentence2):
    """
    Extracts similar tokens from two sentences.


    Args:
        sentence1 (str): The first sentence.
        sentence2 (str): The second sentence.

    Returns:
        list: A list of tuples containing similar tokens from both sentences.
    """
    tokens1 = custom_tokenize(sentence1)
    tokens2 = custom_tokenize(sentence2)

    consecutive_tokens = longest_common_subsequence_sentences(tokens1, tokens2)

    return consecutive_tokens


def reconstruct_formatting(original_sentence, corrected_sentence):
    original_tokens = custom_tokenize(original_sentence)
    corrected_tokens = custom_tokenize(corrected_sentence)
    similar_tokens_pairs = get_similar_tokens_in_sentences(
        original_sentence, corrected_sentence
    )

    # Create a mapping for similar tokens, lists for modified and added tokens
    similar_tokens_mapping = {ot: ct for ot, ct in similar_tokens_pairs}
    modified_tokens = []
    added_tokens = []

    skip_next_space = False
    for ci, c_token in enumerate(corrected_tokens):
        if skip_next_space:
            skip_next_space = False
            continue

        if c_token in similar_tokens_mapping.values():
            original_token_index = original_tokens.index(
                [ot for ot, ct in similar_tokens_pairs if ct == c_token][0]
            )

            # Check if the token was modified and add to the list
            original_token = original_tokens[original_token_index]
            if original_token != c_token:
                modified_tokens.append((original_token, c_token))

            if ci + 1 < len(corrected_tokens) and corrected_tokens[ci + 1] == " ":
                skip_next_space = True  # Skip the next space token in the loop
        else:
            # Add to added tokens list if it's not a space
            if c_token.strip():
                added_tokens.append(c_token)

    return modified_tokens, added_tokens
