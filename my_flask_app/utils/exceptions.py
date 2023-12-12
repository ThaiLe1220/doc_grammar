""" Filename: exceptions.py - Directory: my_flask_app/utils
"""


class GrammarCheckError(Exception):
    """Custom exception for errors during grammar checking."""

    def __init__(self, message="Error while checking grammar"):
        self.message = message
        super().__init__(self.message)
