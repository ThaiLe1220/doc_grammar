""" File: tests/analyze_endnote_xml.py
"""
import os
import zipfile
import xml.etree.ElementTree as ET


def analyze_docx_xml(docx_path):
    # Open the .docx file as a zip archive
    with zipfile.ZipFile(docx_path) as docx_zip:
        # Extract the XML file for the document body
        with docx_zip.open("word/document.xml") as document_xml:
            # Parse the XML
            tree = ET.parse(document_xml)
            root = tree.getroot()
            output_item = os.path.join(os.path.dirname(__file__), "root.txt")
            with open(output_item, "a", encoding="utf-8") as file_part:
                file_part.write("\n-------- ROOT -------- \n")
                for attribute_name in dir(root):
                    attribute_value = getattr(root, attribute_name)
                    file_part.write(f"{attribute_name}: {attribute_value}\n")

            # Define the namespaces
            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            # Look for elements related to EndNote references
            endnote_refs = root.findall(".//w:endnoteReference", namespaces)
            fld_simples = root.findall(".//w:fldSimple", namespaces)
            instr_texts = root.findall(".//w:instrText", namespaces)

            # Print out the XML structure of found elements
            for endnote_ref in endnote_refs:
                print(ET.tostring(endnote_ref, encoding="unicode"))

            for fld_simple in fld_simples:
                print(ET.tostring(fld_simple, encoding="unicode"))

            for instr_text in instr_texts:
                print(ET.tostring(instr_text, encoding="unicode"))

            # Return a list of identified elements (for further processing if needed)
            return endnote_refs, fld_simples, instr_texts


# Assuming 'ICCE2023_gpt_format_test.docx' contains the EndNote references
# Adjust the path if necessary based on where the script is run from
docx_path = "../file_uploads/ICCE2023_gpt_format_test.docx"
analyze_docx_xml(docx_path)
