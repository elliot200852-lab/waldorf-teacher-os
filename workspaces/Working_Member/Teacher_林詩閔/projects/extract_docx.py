import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            paragraphs = []
            for p in tree.iter(NAMESPACE + 'p'):
                texts = [node.text for node in p.iter(NAMESPACE + 't') if node.text is not None]
                if texts:
                    paragraphs.append(''.join(texts)) # type: ignore
            return '\n'.join(paragraphs)
    except Exception as e:
        return str(e)

files = [
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\projects\3C_assessment.docx",
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\唸謠.docx",
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\貓頭鳥揣伴.docx",
    r"c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\元宵節來臆燈猜.docx"
]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for f in files:
    print(f"\n=== {f.split('\\')[-1]} ===")
    print(extract_text_from_docx(f))
