import PyPDF2
import re
import pandas as pd

def extract_and_clean_table_data(pdf_path):
    """
    PDF 파일에서 표 데이터를 추출하고 정리합니다.

    Args:
        pdf_path (str): PDF 파일 경로.

    Returns:
        list: 정리된 표 데이터를 담은 리스트.
    """

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    # 테이블 시작과 끝을 나타내는 패턴 정의
    table_start_pattern = r"월\s+전월말예탁자산.*?배당금액"
    table_end_pattern = r"\d{4}-\d{2}\s+[\d,]+\s+[\d,]+"  # 테이블 끝나는 패턴 (날짜와 숫자)
    table_content = re.search(table_start_pattern + r"(.*?)" + table_end_pattern, text, re.DOTALL)

    if not table_content:
        print("Table not found in PDF.")
        return []

    raw_table_text = table_content.group(1).strip()
    rows = raw_table_text.strip().split('\n')

    cleaned_data = []
    header_row = []
    if rows:
        # 헤더 처리 (두 줄로 분리된 헤더 합치기)
        header_parts = rows[0].split(' ')
        header_row = [header_parts[i] + " " + header_parts[i+1] if i < len(header_parts) - 1 else header_parts[i] for i in range(0, len(header_parts), 2)]

        for i in range(1, len(rows) - 1, 2):  # 2줄씩 처리
            row1 = rows[i].split(' ')
            row2 = rows[i+1].split(' ')

            # 첫 번째 열과 마지막 열은 row1 값만 사용, 나머지는 row1 + row2
            cleaned_row = [row1[0], *[row1[j] + row2[j] for j in range(1, len(row1) - 1)], row1[-1]]
            cleaned_data.append(dict(zip(header_row, cleaned_row)))
    return cleaned_data

# PDF 파일 경로
pdf_file_path =r"C:\Users\User\Documents\개인자료\미국세금신고\증빙서류\아내자료\이0영_27_주식 월별수익현황(스캔)pdf.pdf"

# 표 데이터 추출 및 정리
cleaned_data = extract_and_clean_table_data(pdf_file_path)

# DataFrame 생성 및 엑셀 파일로 저장
if cleaned_data:
    df = pd.DataFrame(cleaned_data)
    excel_file_path = r"C:\Users\User\Documents\개인자료\미국세금신고\증빙서류\아내자료\이0영_27_주식 월별수익현황(스캔)pdf.xlsx"
    df.to_excel(excel_file_path, index=False)
    print(f"Cleaned data saved to '{excel_file_path}'")
else:
    print("No data to save.")