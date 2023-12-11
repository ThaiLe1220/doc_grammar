# Filename: test.py - Directory: my_flask_app/tests
import re


def custom_tokenize(text):
    pattern = r'\b\w+[\w\'-]*[.,;:!?"]?|\s+|[.,;:!?"]'
    return re.findall(pattern, text)


def longest_common_subsequence(str1, str2):
    """Compute the longest common subsequence of two strings"""
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
    """Calculate the percentage difference based on similar consecutive characters"""
    lcs_length = longest_common_subsequence(str1, str2)
    total_length = len(str1) + len(str2)
    diff_length = total_length - 2 * lcs_length
    percentage_diff = (diff_length / total_length) * 100
    return percentage_diff


def longest_common_subsequence_sentences(tokens1, tokens2):
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
    tokens1 = custom_tokenize(sentence1)
    tokens2 = custom_tokenize(sentence2)

    consecutive_tokens = longest_common_subsequence_sentences(tokens1, tokens2)
    return consecutive_tokens


def reconstruct_formatting(original_sentence, corrected_sentence, original_formatting):
    original_tokens = custom_tokenize(original_sentence)
    corrected_tokens = custom_tokenize(corrected_sentence)
    similar_tokens_pairs = get_similar_tokens_in_sentences(
        original_sentence, corrected_sentence
    )

    # Create a mapping for similar tokens
    similar_tokens_mapping = {ot: ct for ot, ct in similar_tokens_pairs}

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

            # Handle space token formatting immediately after a word token
            if ci + 1 < len(corrected_tokens) and corrected_tokens[ci + 1] == " ":
                corrected_formatting.append(
                    original_formatting[original_token_index + 1].copy()
                )
                skip_next_space = True  # Skip the next space token in the loop
        else:
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

    return corrected_formatting


original_sentence = "Tourismx and suxtainable development: Development challengep in less developeds countries."
corrected_sentence = "Tourism and sustainable development: Development challenges in less developed countries."
original_formatting = [
    {"text": "Tourismx", "bold": True, "font_size": 228600},
    {"text": " "},
    {"text": "and"},
    {"text": " "},
    {"text": "suxtainable"},
    {"text": " "},
    {"text": "development:", "italic": True},
    {"text": " ", "italic": True},
    {"text": "Development", "italic": True},
    {"text": " ", "italic": True},
    {"text": "challengep"},
    {"text": " "},
    {"text": "in"},
    {"text": " "},
    {"text": "less"},
    {"text": " "},
    {"text": "developeds"},
    {"text": " "},
    {"text": "countries."},
]
expected_formatting = [
    {"text": "Tourism", "bold": True, "font_size": 228600},
    {"text": " "},
    {"text": "and"},
    {"text": " "},
    {"text": "sustainable"},
    {"text": " "},
    {"text": "development:", "italic": True},
    {"text": " ", "italic": True},
    {"text": "Development", "italic": True},
    {"text": " ", "italic": True},
    {"text": "challenges"},
    {"text": " "},
    {"text": "in"},
    {"text": " "},
    {"text": "less"},
    {"text": " "},
    {"text": "developed"},
    {"text": " "},
    {"text": "countries."},
]


corrected_formatting = reconstruct_formatting(
    original_sentence, corrected_sentence, original_formatting
)


# Compare the output with expected_formatting
def compare_formatting(output, expected):
    if len(output) != len(expected):
        return False
    for o, e in zip(output, expected):
        if o != e:
            return False
    return True


# Print the result of the comparison
result = compare_formatting(corrected_formatting, expected_formatting)
print(f"\nOriginal Sentence: {original_sentence}")
print(f"Corrected Sentence: {corrected_sentence}")

print(f"\nOriginal Formatting:")
for item in original_formatting:
    print(item)
print(f"\nExpected Formatting:")
for item in expected_formatting:
    print(item)
print(f"\nResult Formatting:")
for item in corrected_formatting:
    print(item)

print("\nThe output matches the expected formatting:", result)
