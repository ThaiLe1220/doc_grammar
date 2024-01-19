import re


def custom_tokenize(text):
    """
    Tokenizes a string into words, spaces, punctuation marks, and special patterns like '*email'.

    :param text: The string to be tokenized.
    :return: A list of tokens extracted from the string.
    """
    # Adding a regex pattern to capture '*email' addresses
    # email_pattern = r"\*\w+[\w.-]*@\w+\.\w+(\.\w+)?"
    email_pattern = r"w"
    # Original pattern to tokenize the rest of the text
    original_pattern = (
        r'\w+[\w\'-]*\)?|[.,;:!?{}<>()@"]|\b\w+[\w\'-]*[.,;:!?{}<>()"]?|\s+'
    )
    # Combine the patterns, giving precedence to the email pattern
    combined_pattern = f"({email_pattern})|({original_pattern})"

    return re.findall(combined_pattern, text)


# Example usage
text = "Here is an email: *anna.felipe@rmit.edu.vn and some other text. Le hong Thai. lehongthai2000@gmail.com"
tokens = custom_tokenize(text)
# Flatten the list of tuples and filter out empty strings
tokens = [item for sublist in tokens for item in sublist if item]
print(tokens)
