import re


def custom_tokenize(text):
    """Tokenize a sentence into words, spaces, and punctuation"""
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
        if percentage_difference(tokens1[i - 1], tokens2[j - 1]) < 45:
            consecutive_tokens.append((tokens1[i - 1], tokens2[j - 1]))
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return consecutive_tokens[::-1]  # Reverse the list to maintain original order


def compare_sentences(sentence1, sentence2):
    tokens1 = custom_tokenize(sentence1)
    tokens2 = custom_tokenize(sentence2)

    consecutive_tokens = longest_common_subsequence_sentences(tokens1, tokens2)
    similarity_percentage = (
        len(consecutive_tokens) / max(len(tokens1), len(tokens2)) * 100
    )
    return similarity_percentage, consecutive_tokens


# Example sentences
sentence1 = "ThaiLeee is went to the wrong sessession qws."

sentence2 = "ThaiLeee is went to the wrong sessession qws."
sentence3 = "ThaiLeee is to the next sessession qws."
sentence4 = "ThaiLe is in the wrong session qws."

# Compare the sentences
similarity_percentage1, similar_sequences1 = compare_sentences(sentence1, sentence2)
similarity_percentage2, similar_sequences2 = compare_sentences(sentence1, sentence3)
similarity_percentage3, similar_sequences3 = compare_sentences(sentence1, sentence4)

print(f"Similarity Percentage: {similarity_percentage1}%")
# print("Consecutive Similar Tokens:", ["".join(seq) for seq in similar_sequences1])
print(similar_sequences1)

print(f"Similarity Percentage: {similarity_percentage2}%")
# print("Consecutive Similar Tokens:", ["".join(seq) for seq in similar_sequences2])
print(similar_sequences2)

print(f"Similarity Percentage: {similarity_percentage3}%")
# print("Consecutive Similar Tokens:", ["".join(seq) for seq in similar_sequences3])
print(similar_sequences3)

# Consecutive Similar Tokens: ['ThaiLeee', ' ', 'is', ' ', 'went', ' ', 'to', ' ', 'the', ' ', 'wrong', ' ', 'sessession', ' ', 'qws.']
# Similarity Percentage: 86.66666666666667%
# Consecutive Similar Tokens: ['ThaiLeee', ' ', 'is', ' ', 'to', ' ', 'the', ' ', 'wrong', ' ', 'sessession', ' ', 'qws.']
# Similarity Percentage: 80.0%
# Consecutive Similar Tokens: ['ThaiLeee', ' ', 'is', ' ', ' ', 'the', ' ', 'wrong', ' ', 'sessession', ' ', 'qws.']
