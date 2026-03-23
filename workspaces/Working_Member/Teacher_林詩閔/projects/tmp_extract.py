import zipfile, xml.etree.ElementTree as ET
import os

docx_path = r'c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\唸謠.docx'
out_path = r'c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\projects\nian-yio-text.txt'

d=zipfile.ZipFile(docx_path)
x=d.read('word/document.xml')
t=ET.XML(x)
ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
paragraphs = []
for p in t.iter(ns+'p'):
    texts = [n.text for n in p.iter(ns+'t') if n.text]
    if texts:
        paragraphs.append(''.join(texts))
text='\n'.join(paragraphs)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
