import re


def extract_and_preserve_references(text: str):
    # Pattern to match all content within parentheses
    reference_pattern = r"\(([^)]+)\)"

    # Find all matches of the pattern
    references = re.findall(reference_pattern, text)

    # Replace each found reference section with a placeholder
    for ref in references:
        text = text.replace(f"({ref})", " REF_PLACEHOLDER ", 1)

    return text, references


# Sample text
sample_text = "In recent years (2023), the field of education has witnessed a significant shift toward the integration of technology, particularly in the assessment design (Almond et al., 2002; Gorin, 2006; Ineke Van den Berg et al., 2006; Verónica Villarroel et al., 2018)."

# Running the function
modified_text, refs = extract_and_preserve_references(sample_text)

# Output results
print("Modified Text:", modified_text)
print("Extracted References:", refs)
