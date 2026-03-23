import zipfile
import xml.etree.ElementTree as ET
import codecs

def extract(docx_path):
    with codecs.open("output.txt", "w", encoding="utf-8") as f:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            for p in tree.iter(NAMESPACE + 't'):
                if p.text and p.text.strip():
                    f.write(p.text.strip() + "\n")

extract(r'c:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\reference\113三年級台語課\秋季\3C心田班姓名台語.docx')
