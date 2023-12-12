""" Filename: reconstruct_sentence.py - Directory: my_flask_app/utils
"""
import re


def custom_tokenize(text):
    """
    Tokenizes a string into words, spaces, and punctuation marks.

    :param text: The string to be tokenized.
    :return: A list of tokens extracted from the string.
    """
    pattern = r'\b\w+[\w\'-]*[.,;:!?"]?|\s+|[.,;:!?"]'
    return re.findall(pattern, text)


def longest_common_subsequence(str1, str2):
    """
    Compute the longest common subsequence (LCS) of two strings.

    :param str1: First string.
    :param str2: Second string.
    :return: Length of the LCS.
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
    Calculate the percentage difference based on LCS.

    :param str1: First string.
    :param str2: Second string.
    :return: Percentage difference between the two strings.
    """
    lcs_length = longest_common_subsequence(str1, str2)
    total_length = len(str1) + len(str2)
    diff_length = total_length - 2 * lcs_length
    percentage_diff = (diff_length / total_length) * 100
    return percentage_diff


def longest_common_subsequence_sentences(tokens1, tokens2):
    """
    Find the longest subsequence of similar tokens between two lists of tokens.

    :param tokens1: List of tokens from the first sentence.
    :param tokens2: List of tokens from the second sentence.
    :return: List of consecutive tokens forming the longest common subsequence.
    """
    m, n = len(tokens1), len(tokens2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    longest_subseq_end = (
        0,
        0,
    )  # Keep track of the position where the longest subsequence of similar tokens ends.

    for i in range(m):
        for j in range(n):
            # Consider 2 tokens are similar if their percentage_difference < 45%
            if percentage_difference(tokens1[i], tokens2[j]) < 45:
                dp[i + 1][j + 1] = dp[i][j] + 1
                if dp[i + 1][j + 1] > dp[longest_subseq_end[0]][longest_subseq_end[1]]:
                    longest_subseq_end = (i + 1, j + 1)
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    # Backtrack to find the actual tokens in the subsequence
    i, j = longest_subseq_end
    consecutive_tokens = []
    while i > 0 and j > 0:
        # Consider 2 tokens are similar if their percentage_difference < 45%
        if percentage_difference(tokens1[i - 1], tokens2[j - 1]) < 45:
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
    Identify similar tokens in two sentences.

    :param sentence1: First sentence.
    :param sentence2: Second sentence.
    :return: List of pairs of similar tokens between the two sentences.
    """
    tokens1 = custom_tokenize(sentence1)
    tokens2 = custom_tokenize(sentence2)

    consecutive_tokens = longest_common_subsequence_sentences(tokens1, tokens2)
    return consecutive_tokens


def reconstruct_formatting(original_sentence, corrected_sentence, original_formatting):
    """
    Apply formatting from an original sentence to a corrected sentence.

    :param original_sentence: The original sentence with formatting.
    :param corrected_sentence: The corrected sentence to apply formatting to.
    :param original_formatting: List of formatting dictionaries for each token in the original sentence.
    :return: Tuple of (List of formatting dictionaries for each token in the corrected sentence, List of modified token pairs, List of added tokens).
    """
    original_tokens = custom_tokenize(original_sentence)
    corrected_tokens = custom_tokenize(corrected_sentence)
    similar_tokens_pairs = get_similar_tokens_in_sentences(
        original_sentence, corrected_sentence
    )

    # Create a mapping for similar tokens, lists for modified and added tokens
    similar_tokens_mapping = {ot: ct for ot, ct in similar_tokens_pairs}
    modified_tokens = []
    added_tokens = []

    corrected_formatting = []
    skip_next_space = False
    for ci, c_token in enumerate(corrected_tokens):
        if skip_next_space:
            skip_next_space = False
            continue

        if c_token in similar_tokens_mapping.values():
            original_token_index = original_tokens.index(
                [ot for ot, ct in similar_tokens_pairs if ct == c_token][0]
            )
            format_to_apply = original_formatting[original_token_index].copy()
            format_to_apply["text"] = c_token
            corrected_formatting.append(format_to_apply)

            # Check if the token was modified and add to the list
            original_token = original_tokens[original_token_index]
            if original_token != c_token:
                modified_tokens.append((original_token, c_token))

            # Handle space token formatting immediately after a word token
            if ci + 1 < len(corrected_tokens) and corrected_tokens[ci + 1] == " ":
                corrected_formatting.append(
                    original_formatting[original_token_index + 1].copy()
                )
                skip_next_space = True  # Skip the next space token in the loop
        else:
            # Add to added tokens list if it's not a space
            if c_token.strip():
                added_tokens.append(c_token)

            # Apply formatting of the nearest similar token for new/dissimilar tokens
            closest_ci = min(
                [corrected_tokens.index(ct) for _, ct in similar_tokens_pairs],
                key=lambda x: abs(x - ci),
            )
            closest_oi = original_tokens.index(
                [
                    ot
                    for ot, ct in similar_tokens_pairs
                    if ct == corrected_tokens[closest_ci]
                ][0]
            )
            format_to_apply = original_formatting[closest_oi].copy()
            format_to_apply["text"] = c_token
            corrected_formatting.append(format_to_apply)

    return corrected_formatting, modified_tokens, added_tokens
