import docx
import sys

def extract_text(doc_path, output_path):
    doc = docx.Document(doc_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                f.write(text + '\n')

if __name__ == '__main__':
    extract_text(sys.argv[1], sys.argv[2])
