import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            paragraphs = []
            for p in tree.iter(ns + 'p'):
                texts = [node.text for node in p.iter(ns + 't') if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error: {e}"

path = r"workspaces\Working_Member\Teacher_林詩閔\projects\3C_assessment.docx"
text = extract_text(path)
with open(r"workspaces\Working_Member\Teacher_林詩閔\projects\3C_assessment.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Extracted!")
