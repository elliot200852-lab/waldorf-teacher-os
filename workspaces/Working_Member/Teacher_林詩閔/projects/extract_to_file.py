import zipfile
import xml.etree.ElementTree as ET
import glob

def extract_docx(file_path):
    try:
        with zipfile.ZipFile(file_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            paragraphs = []
            for p in tree.iter(NAMESPACE + 'p'):
                texts = [node.text for node in p.iter(NAMESPACE + 't') if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error: {e}"

files = [
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\唸謠.docx",
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\貓頭鳥揣伴.docx",
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\元宵節來臆燈猜.docx"
]

with open(r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\extracted_texts.txt", "w", encoding="utf-8") as f:
    for file in files:
        f.write(f"\n\n{'='*20}\n{file}\n{'='*20}\n")
        f.write(extract_docx(file))
        f.write("\n")
