# Filename: reconstruct_formatting_test.py - Directory: my_flask_app/tests
import unittest
from test import reconstruct_formatting, custom_tokenize


class TestDocxUtils(unittest.TestCase):
    def test_1(self):
        original_sentence = "ThaiLeee is went to the wrong sessession qws."
        corrected_sentence = "ThaiLe is in the wrong session qws."
        original_formatting = [
            {"text": "ThaiLeee", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "is", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "went", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "to", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "the", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "wrong", "bold": True, "italic": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "sessession", "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "qws.", "italic": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
        ]

        expected_formatting = [
            {"text": "ThaiLe", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "is", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "in", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "the", "bold": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "wrong", "bold": True, "italic": True, "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "session", "font_size": 228600},
            {"text": " ", "bold": True, "font_size": 228600},
            {"text": "qws.", "italic": True, "font_size": 228600},
        ]

        result = reconstruct_formatting(
            original_sentence, corrected_sentence, original_formatting
        )
        self.assertEqual(result, expected_formatting)

    def test_2(self):
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

        result = reconstruct_formatting(
            original_sentence, corrected_sentence, original_formatting
        )
        self.assertEqual(result, expected_formatting)

    # Additional test cases can be added here to cover more scenarios


if __name__ == "__main__":
    unittest.main()
