import zipfile
import xml.etree.ElementTree as ET

doc_path = r'C:\Users\user\Desktop\27.3.26Methods of teaching for transformative learning.docx'
doc = zipfile.ZipFile(doc_path)
xml_content = doc.read('word/document.xml')
tree = ET.XML(xml_content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paras = []
for p in tree.findall('.//w:p', ns):
    texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
    if texts:
        paras.append(''.join(texts))

with open('extracted_doc.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(paras))
