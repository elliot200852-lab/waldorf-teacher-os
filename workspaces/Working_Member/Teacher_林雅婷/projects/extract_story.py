import os
import zipfile
import xml.etree.ElementTree as ET

def find_file(root_dir, filename_part):
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if filename_part in f:
                return os.path.join(root, f)
    return None

def extract_text(docx_path):
    with zipfile.ZipFile(docx_path) as docx:
        tree = ET.XML(docx.read('word/document.xml'))
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text = [node.text for node in tree.findall('.//w:t', namespaces) if node.text]
        return ''.join(text)

docx_path = find_file('g:\\', '西亞的千年生存戰')
if docx_path:
    print(f"Found: {docx_path}")
    text = extract_text(docx_path)
    with open('story.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Done")
else:
    print("Not found")
