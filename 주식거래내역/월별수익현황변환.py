import pandas as pd
import re
import os
from PyPDF2 import PdfReader
from openpyxl import Workbook

def extract_text_from_pdf(pdf_path):
    """PDF 파일에서 텍스트 추출"""
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_table_data(text):
    """PDF에서 추출한 텍스트에서 표 데이터 파싱"""
    # 텍스트를 줄 단위로 분리
    lines = text.split('\n')
    
    # 필요없는 라인 제거 (빈 줄, 페이지 번호 등)
    filtered_lines = [line.strip() for line in lines if line.strip() and 'CamScanner' not in line]
    
    # 데이터 행을 두 줄씩 묶어서 처리
    row_pairs = []
    i = 0
    
    # 헤더 라인 찾기 (표의 첫 부분)
    header_index = None
    for idx, line in enumerate(filtered_lines):
        if re.search(r'2024-\d{2}', line) and '번호' in filtered_lines[idx-1]:
            header_index = idx - 1
            break
    
    if header_index is None:
        print("표 헤더를 찾을 수 없습니다.")
        return None
    
    # 헤더 행 추출
    header_row1 = filtered_lines[header_index].split()
    header_row2 = filtered_lines[header_index + 1].split()
    
    # 통합된 헤더 생성
    # 열 병합을 고려한 헤더 통합
    headers = []
    if '번호' in header_row1:
        headers.append('번호')
    
    # 나머지 헤더 추가
    for i in range(len(header_row1)):
        if i < len(header_row1) and header_row1[i] not in ['번호']:
            if i < len(header_row2):
                header = f"{header_row1[i]}_{header_row2[i]}"
            else:
                header = header_row1[i]
            headers.append(header)
    
    # 날짜 형식을 가진 헤더를 찾아서 추가
    date_headers = []
    for line in filtered_lines[header_index:header_index+2]:
        date_matches = re.findall(r'2024-\d{2}', line)
        for date in date_matches:
            if date not in date_headers:
                date_headers.append(date)
    
    # 헤더에 날짜 추가
    for date in date_headers:
        headers.append(date)
    
    # 데이터 행 처리 (헤더 이후)
    data_rows = []
    i = header_index + 2  # 헤더 다음부터 시작
    
    while i < len(filtered_lines) - 1:
        row1 = filtered_lines[i].split()
        row2 = filtered_lines[i + 1].split() if i + 1 < len(filtered_lines) else []
        
        # 날짜 행인지 확인
        if any(re.match(r'\d{2}\.\d{2}\.\d{3}', cell) for cell in row1) or \
           any(re.match(r'\d{2}\.\d{2}\.\d{3}', cell) for cell in row2):
            i += 2  # 날짜 행은 건너뛰기
            continue
        
        # 두 줄 데이터 병합
        combined_row = {}
        
        # 각 열에 데이터 할당
        col_idx = 0
        for idx, header in enumerate(headers):
            if '번호' in header:
                if row1 and col_idx < len(row1):
                    combined_row[header] = row1[col_idx]
                    col_idx += 1
            elif '2024-' in header:
                # 날짜 열은 해당 위치에서 데이터 추출
                date_idx = date_headers.index(header)
                if date_idx < len(row1) - 2:  # 날짜 열 인덱스 조정
                    combined_row[header] = row1[date_idx + 2]  # 인덱스 조정 필요할 수 있음
            else:
                # 두 번째 행의 데이터 추가
                if col_idx < len(row2):
                    combined_row[header] = row2[col_idx]
                    col_idx += 1
                else:
                    combined_row[header] = ""
        
        data_rows.append(combined_row)
        i += 2  # 다음 두 줄로 이동
    
    return headers, data_rows

def convert_to_excel(headers, data_rows, output_path):
    """데이터를 엑셀 파일로 변환"""
    df = pd.DataFrame(data_rows)
    df.to_excel(output_path, index=False)
    print(f"엑셀 파일이 생성되었습니다: {output_path}")

def main(pdf_path, output_path):
    """메인 함수"""
    print(f"PDF 파일 처리 중: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    # 디버깅을 위해 추출된 텍스트 저장
    with open('extracted_text.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("추출된 텍스트를 'extracted_text.txt'에 저장했습니다.")
    
    result = parse_table_data(text)
    if result:
        headers, data_rows = result
        convert_to_excel(headers, data_rows, output_path)
    else:
        print("표 데이터를 추출할 수 없습니다.")

if __name__ == "__main__":
    pdf_path = r"C:\Users\User\Documents\개인자료\미국세금신고\증빙서류\아내자료\이0영_27_주식 월별수익현황(스캔)pdf.pdf"  # 입력 PDF 파일 경로
    output_path = r"C:\Users\User\Documents\개인자료\미국세금신고\증빙서류\아내자료\이0영_27_주식 월별수익현황(스캔)pdf.xlsx"  # 출력 엑셀 파일 경로
    main(pdf_path, output_path)