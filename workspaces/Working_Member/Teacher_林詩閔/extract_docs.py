import zipfile
import xml.etree.ElementTree as ET
import codecs
import time

files = [
    r'C:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\113三年級台語課\113三年級(3C)秋季台語教學紀錄(林詩閔).docx',
    r'C:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\113三年級台語課\113三年級(3C)冬季台語教學紀錄(林詩閔).docx',
    r'C:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\113三年級台語課\113三年級(3C)春季台語教學紀錄(林詩閔).docx',
    r'C:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\113三年級台語課\113三年級(3C)夏季台語教學紀錄(林詩閔).docx'
]

with codecs.open('3c_records.txt', 'w', encoding='utf-8') as f:
    for docx_path in files:
        f.write('\n\n=== ' + docx_path.split('\\')[-1] + ' ===\n')
        try:
            with zipfile.ZipFile(docx_path) as docx:
                xml_content = docx.read('word/document.xml')
                tree = ET.XML(xml_content)
                NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
                for p in tree.iter(NAMESPACE + 't'):
                    if p.text and p.text.strip():
                        f.write(p.text.strip() + '\n')
        except Exception as e:
            f.write('Error: ' + str(e) + '\n')
