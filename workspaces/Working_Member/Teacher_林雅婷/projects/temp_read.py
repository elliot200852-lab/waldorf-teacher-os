import zipfile
import xml.etree.ElementTree as ET

docx_path = r'g:\我的雲端硬碟\AI\歐亞非地理備課\塵土、黑金與綠洲--西亞的千年生存戰.docx'
out_path = r'c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\temp_output.txt'

try:
    with zipfile.ZipFile(docx_path) as docx:
        tree = ET.XML(docx.read('word/document.xml'))
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text = [node.text for node in tree.iterfind('.//w:t', namespaces) if node.text]
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text))
    print("Success")
except Exception as e:
    print(f"Error: {e}")
