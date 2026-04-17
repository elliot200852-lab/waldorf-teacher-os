import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def read_docx(path):
    z = zipfile.ZipFile(path)
    xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    texts = []
    for node in tree.iter():
        if node.tag == f"{{{ns['w']}}}t" and node.text:
            texts.append(node.text)
        elif node.tag == f"{{{ns['w']}}}p":
            texts.append('\n')
    return ''.join(texts).replace("\n\n\n", "\n")

def read_pdf(path):
    try:
        import fitz
        doc = fitz.open(path)
        return "\n".join([page.get_text() for page in doc])
    except ImportError:
        try:
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([page.extract_text() for page in reader.pages])
        except ImportError:
            return "No fitz or PyPDF2 installed"

print("=== DOCX Content ===")
try:
    print(read_docx("雅婷七年級課程大綱 copy.docx")[:2000])
except Exception as e:
    print("DOCX Err:", e)

print("\n=== PDF Content ===")
try:
    print(read_pdf("亞洲地理6B妍霏.pdf")[:2000])
except Exception as e:
    print("PDF Err:", e)
