import docx
import sys

def extract_tables(doc_path, output_path):
    doc = docx.Document(doc_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, table in enumerate(doc.tables):
            f.write(f'## Table {i+1}\n\n')
            for row in table.rows:
                row_data = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
                f.write('| ' + ' | '.join(row_data) + ' |\n')
            f.write('\n')

if __name__ == '__main__':
    extract_tables(sys.argv[1], sys.argv[2])
