def longest_common_subsequence(str1, str2):
    """Compute the longest common subsequence of two strings"""
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    print(dp)

    for i in range(m):
        for j in range(n):
            if str1[i] == str2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    print(dp)
    return dp[m][n]


def percentage_difference(str1, str2):
    """Calculate the percentage difference based on similar consecutive characters"""
    lcs_length = longest_common_subsequence(str1, str2)
    total_length = len(str1) + len(str2)
    diff_length = total_length - 2 * lcs_length
    percentage_diff = (diff_length / total_length) * 100
    return percentage_diff


# Test examples
print(percentage_difference("lh", "hello"))  # Example 1
print(percentage_difference("el", "hello"))  # Example 1
print(percentage_difference("le", "hello"))  # Example 1
# print(percentage_difference("sessession", "session"))  # Example 1
# print(percentage_difference("xsession", "session"))  # Example 2
# print(percentage_difference("sessionxx", "session"))  # Example 3
# print(percentage_difference("ThaiLeee", "ThaiLe e"))  # Example 3
