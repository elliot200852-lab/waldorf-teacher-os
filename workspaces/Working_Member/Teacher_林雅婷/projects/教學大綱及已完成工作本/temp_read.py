import zipfile
import xml.etree.ElementTree as ET
import sys
import io

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
    return ''.join(texts)

content = read_docx("雅婷七年級課程大綱 copy.docx")
with io.open("output.txt", "w", encoding="utf-8") as f:
    f.write(content)
