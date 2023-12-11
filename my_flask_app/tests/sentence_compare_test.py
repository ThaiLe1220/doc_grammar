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


def compare_sentences(sentence1, sentence2):
    tokens1 = custom_tokenize(sentence1)
    tokens2 = custom_tokenize(sentence2)

    # print(f"\nToken of original sentence: ")
    # for item in tokens1:
    #     print(f"'{item}'")

    # print(f"\nToken of corrected sentence: ")
    # for item in tokens2:
    #     print(f"'{item}'")
    Unchanged = []
    Changed = []

    for t1 in tokens1:
        for t2 in tokens2:
            if t1 != " ":
                if t1 == t2:
                    Unchanged.append(t1)

    for t1 in tokens1:
        for t2 in tokens2:
            if t1 != " ":
                if (
                    t1 not in Unchanged
                    and t2 not in Unchanged
                    and t1 != t2
                    and percentage_difference(t1, t2) < 45
                ):
                    Changed.append((t1, t2))

    print(Unchanged)
    print(Changed)


# Example usage
sentence1 = "ThaiLeee is went to the wrong sessession qws."
sentence2 = "ThaiLe is in the wrong session qws."
compare_sentences(sentence1, sentence2)
