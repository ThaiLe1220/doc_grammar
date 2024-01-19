import re


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


def custom_tokenize(text):
    pattern = r"\(\w+[\w\'-]*\)?|[().,;:!?\"]|\b\w+[\w\'-]*(?:’s)?[().,;:!?\"]?|\s+"
    return re.findall(pattern, text)


def find_modified_text(original_text, corrected_text):
    print(f"[Original Text] {original_text}")
    print(f"[Corrected Text] {corrected_text}")
    diff = percentage_difference(original_text, corrected_text)
    print(diff)

    # Check if the text difference is more than 45%
    if diff > 45:
        return []

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

            elif ori_index + 2 < len(ori) and cor_index + 2 < len(cor):
                if ori[ori_index + 2][0] == cor[cor_index][0]:
                    mod.append((ori_token, "", ori_pos))
                    mod.append((" ", "", ori_pos + 1))
                    mod.append((ori[ori_index + 2][0], cor_token, ori_pos + 2))

                    ori_index += 3
                    cor_index += 1
                    continue
                elif ori[ori_index][0] == cor[cor_index + 2][0]:
                    mod.append(
                        (ori_token, cor_token + " " + cor[cor_index + 2][0], ori_pos)
                    )
                    ori_index += 1
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
                    if ori_index + 2 < len(ori):
                        mod.append((ori[ori_index + 2][0], cor_token, ori_pos + 2))
                    ori_index += 3
                    cor_index += 1
                else:
                    if cor_index + 2 < len(cor):
                        mod.append(
                            (
                                ori_token,
                                cor_token + " " + cor[cor_index + 2][0],
                                ori_pos,
                            )
                        )
                        cor_index += 3
                    else:
                        mod.append((ori_token, cor_token, ori_pos))
                        cor_index += 1
                    ori_index += 1

    return mod


original_text = "Given that Sony PSN has been under DDoS attack by Anonymous before this event happened. Therefore, it is possible that:"
corrected_text = "Given that Sony PSN has ben under DoS atack by Anonymous before this event hapened d., Therefore, it is posible that:"


print(custom_tokenize(original_text))
print(custom_tokenize(corrected_text))

print(len(custom_tokenize(original_text)))
print(len(custom_tokenize(corrected_text)))


result = find_modified_text(original_text, corrected_text)
for item in result:
    print(f"Original: '{item[0]}', Modified: '{item[1]}', Position: {item[2]}")
