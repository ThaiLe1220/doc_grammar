""" Filename: exceptions.py - Directory: my_flask_app/utils

This module defines a custom exception class, GrammarCheckError, for handling errors
that may occur during the grammar checking process. This exception is raised when
there is an issue with the grammar checking API call.

"""


class GrammarCheckError(Exception):
    """Custom exception for errors during grammar checking."""

    def __init__(self, message="Error while checking grammar"):
        self.message = message
        super().__init__(self.message)
