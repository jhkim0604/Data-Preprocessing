import pandas as pd
import re
import csv
import os
import PyPDF2
import openpyxl
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_from_pdf(pdf_path, start_page=1):
    """
    PDF 파일에서 텍스트를 추출합니다.
    
    Args:
        pdf_path (str): PDF 파일 경로
        start_page (int): 추출을 시작할 페이지 번호 (0-based index)
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        extracted_text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            # 지정된 페이지부터 끝까지 텍스트 추출
            for page_num in range(start_page - 1, num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                logger.info(f"페이지 {page_num + 1} 텍스트 추출 완료: {len(page_text)} 자")
                extracted_text += page_text + "\n"
                
        return extracted_text
    except Exception as e:
        logger.error(f"PDF 파일 처리 중 오류 발생: {e}")
        return None

def convert_stock_transactions(input_source, output_file, is_pdf=False, pdf_start_page=2, skip_first_table=True):
    """
    두 줄로 구성된 주식 거래내역을 한 줄로 통합하여 변환합니다.
    
    Args:
        input_source (str): 입력 텍스트, 파일 경로 또는 PDF 파일 경로
        output_file (str): 출력 파일 경로 (xlsx)
        is_pdf (bool): 입력이 PDF 파일인지 여부
        pdf_start_page (int): PDF에서 시작할 페이지 번호
        skip_first_table (bool): 두 번째 페이지의 첫 번째 표를 건너뛸지 여부
    """
    # 데이터를 저장할 리스트
    consolidated_data = []
    
    # 헤더 정의
    headers = [
        '거래일자', '종목명', '수량', '거래금액', '수수료', '변제/연체합', '예수금',
        '통화', '거래구분', '단가', '거래금액(외)', '거래세및농특세', '소득/주민세', '예수금(외)'
    ]
    
    try:
        # 입력 소스 처리
        if is_pdf:
            # PDF에서 텍스트 추출
            text_content = extract_from_pdf(input_source, pdf_start_page)
            if text_content is None:
                return None
                
            # 디버깅을 위해 추출된 텍스트 일부를 출력
            logger.info("PDF에서 추출된 텍스트 샘플 (처음 300자):")
            logger.info(text_content[:300])
            
            lines = text_content.split('\n')
        elif os.path.exists(input_source):
            # 파일에서 읽기
            with open(input_source, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        else:
            # 직접 텍스트가 입력된 경우
            lines = input_source.strip().split('\n')
        
        # PDF에서 추출된 텍스트에서 표 제목 및 불필요한 줄 제거
        cleaned_lines = []
        title_found = False
        first_table_found = False
        first_table_ending = False
        second_table_started = False
        
        # 표 사이를 구분하는 패턴 정의 (예: 긴 구분선 또는 특정 텍스트)
        table_separator_pattern = r'^[-=]{10,}$'  # 10개 이상의 '-' 또는 '=' 문자
        
        # 추출된 텍스트 처음 부분 저장 (디버깅용)
        sample_lines = "\n".join(lines[:50])  # 처음 50줄
        with open("pdf_extracted_sample.txt", "w", encoding="utf-8") as f:
            f.write(sample_lines)
        logger.info(f"추출된 텍스트 샘플을 pdf_extracted_sample.txt에 저장했습니다.")
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 디버깅을 위해 모든 라인 출력
            logger.debug(f"처리 중인 라인: {line}")
            
            # 첫 번째 표를 건너뛰기 위한 로직
            if skip_first_table and not second_table_started:
                # 날짜 형식으로 시작하는지 확인 (YYYY/MM/DD 형식)
                date_pattern = r'^(\d{4}/\d{2}/\d{2})'
                if re.match(date_pattern, line):
                    # 이미 첫 번째 표를 지났다고 판단하고 두 번째 표의 데이터 시작
                    logger.info(f"날짜 형식 발견, 두 번째 표 시작으로 간주: {line}")
                    second_table_started = True
                    cleaned_lines.append(line)
                    continue
                
                # 표 제목 패턴 (예: "거래일자    종목명    수량    거래금액" 등)
                title_pattern = r'(거래일자|통화)\s+(종목명|거래구분)\s+(수량|단가)'
                
                # 첫 번째 표 제목 찾기
                if re.search(title_pattern, line) and not first_table_found:
                    logger.info("첫 번째 표 제목 발견: " + line)
                    first_table_found = True
                    continue
                
                # 첫 번째 표의 끝을 찾기 위한 로직
                if first_table_found and not first_table_ending:
                    # 표 구분자 또는 다음 표의 시작 패턴 확인
                    if re.match(table_separator_pattern, line) or "합계" in line or "Total" in line:
                        logger.info("첫 번째 표 끝 부분 발견: " + line)
                        first_table_ending = True
                    continue
                
                # 두 번째 표 제목 찾기
                if first_table_ending:
                    title_pattern = r'(거래일자|통화)\s+(종목명|거래구분)\s+(수량|단가)'
                    if re.search(title_pattern, line):
                        logger.info("두 번째 표 제목 발견: " + line)
                        title_found = True
                        continue
            
            # 두 번째 표부터 데이터 처리
            if not skip_first_table or second_table_started:
                # 표 제목 패턴 확인
                title_pattern = r'(거래일자|통화)\s+(종목명|거래구분)\s+(수량|단가)'
                if re.search(title_pattern, line):
                    if not title_found:
                        # 첫 번째 발견된 표 제목은 무시 (헤더로 대체)
                        title_found = True
                        logger.info("표 제목 발견: " + line)
                    continue
                
                # 날짜 형식 확인 - PDF 변환 과정에서 형식이 변경될 수 있음
                date_patterns = [
                    r'^(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD
                    r'^(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                    r'^(\d{4}\.\d{2}\.\d{2})'  # YYYY.MM.DD
                ]
                
                is_date_line = any(re.match(pattern, line) for pattern in date_patterns)
                
                if is_date_line or line.startswith('KRW'):
                    cleaned_lines.append(line)
                    logger.debug(f"유효한 데이터 라인 발견: {line}")
                
        logger.info(f"정제된 라인 수: {len(cleaned_lines)}")
        # 정제된 라인 모두 저장 (디버깅용)
        with open("cleaned_lines.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_lines))
        logger.info(f"정제된 라인을 cleaned_lines.txt에 저장했습니다.")
            
        # 데이터 처리
        i = 0
        while i < len(cleaned_lines):
            # 첫 번째 줄 처리
            if i < len(cleaned_lines):
                first_line = cleaned_lines[i].strip()
                # 날짜 형식으로 시작하는지 확인 (여러 가능한 형식)
                date_patterns = [
                    r'^(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD
                    r'^(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                    r'^(\d{4}\.\d{2}\.\d{2})'  # YYYY.MM.DD
                ]
                
                is_date_line = any(re.match(pattern, first_line) for pattern in date_patterns)
                
                if is_date_line:
                    first_data = first_line.split()
                    logger.debug(f"첫 번째 줄 데이터: {first_data}")
                    
                    # 두 번째 줄이 있는지 확인
                    if i + 1 < len(cleaned_lines):
                        second_line = cleaned_lines[i+1].strip()
                        # 통화 코드(KRW)로 시작하는지 확인
                        if second_line.startswith('KRW'):
                            second_data = second_line.split()
                            logger.debug(f"두 번째 줄 데이터: {second_data}")
                            
                            # 두 줄 데이터 합치기
                            try:
                                # 종목명에 공백이 있을 수 있으므로 조정
                                if len(first_data) > 7:  # 종목명에 공백이 있는 경우
                                    종목명_시작 = 1
                                    종목명_끝 = len(first_data) - 5  # 마지막 5개 항목 제외
                                    종목명 = ' '.join(first_data[종목명_시작:종목명_끝])
                                    수량 = first_data[종목명_끝]
                                    거래금액 = first_data[종목명_끝 + 1]
                                    수수료 = first_data[종목명_끝 + 2]
                                    변제연체합 = first_data[종목명_끝 + 3]
                                    예수금 = first_data[종목명_끝 + 4]
                                    
                                    combined_row = [
                                        first_data[0],  # 거래일자
                                        종목명,          # 종목명
                                        수량,           # 수량
                                        거래금액,        # 거래금액
                                        수수료,         # 수수료
                                        변제연체합,      # 변제/연체합
                                        예수금          # 예수금
                                    ]
                                else:  # 종목명에 공백이 없는 경우 (필드 수가 적을 경우 대비)
                                    # 필드가 7개 미만인 경우도 처리
                                    if len(first_data) < 7:
                                        # 필요한 만큼 빈 값 추가
                                        first_data = first_data + [''] * (7 - len(first_data))
                                        logger.warning(f"첫 번째 줄 데이터 필드 부족: {len(first_data)}/7 필드로 보완")
                                    
                                    combined_row = [
                                        first_data[0],  # 거래일자
                                        first_data[1],  # 종목명
                                        first_data[2],  # 수량
                                        first_data[3],  # 거래금액
                                        first_data[4],  # 수수료
                                        first_data[5],  # 변제/연체합
                                        first_data[6]   # 예수금
                                    ]
                                
                                # 두 번째 줄 데이터 추가
                                # 인덱스 오류 방지를 위해 길이 확인
                                if len(second_data) >= 7:
                                    combined_row.extend([
                                        second_data[0],  # 통화
                                        second_data[1],  # 거래구분
                                        second_data[2],  # 단가
                                        second_data[3],  # 거래금액(외)
                                        second_data[4],  # 거래세및농특세
                                        second_data[5],  # 소득/주민세
                                        second_data[6]   # 예수금(외)
                                    ])
                                else:
                                    # 데이터가 부족한 경우, 가능한 만큼 추가하고 나머지는 빈 값으로 채움
                                    for idx in range(min(len(second_data), 7)):
                                        combined_row.append(second_data[idx])
                                        
                                    # 부족한 필드 빈 값으로 채움
                                    combined_row.extend([''] * (14 - len(combined_row)))
                                    logger.warning(f"두 번째 줄 데이터 필드 부족: {len(second_data)}/7 필드 있음")
                                
                                # 최종 확인: combined_row가 정확히 14개 필드를 가지는지
                                if len(combined_row) != 14:
                                    # 부족하면 채우고, 초과하면 자름
                                    if len(combined_row) < 14:
                                        combined_row.extend([''] * (14 - len(combined_row)))
                                    else:
                                        combined_row = combined_row[:14]
                                        
                                consolidated_data.append(combined_row)
                                logger.debug(f"통합된 행 추가: {combined_row}")
                                
                            except Exception as e:
                                logger.error(f"데이터 처리 중 오류 발생: {e}, 라인: {first_line}, {second_line}")
                                logger.error(f"첫 번째 데이터: {first_data}")
                                logger.error(f"두 번째 데이터: {second_data}")
                                import traceback
                                logger.error(traceback.format_exc())
                                
                            i += 2  # 다음 두 줄로 이동
                            continue
                        else:
                            # 두 번째 줄이 KRW로 시작하지 않으면 첫 번째 줄만 처리
                            logger.warning(f"두 번째 줄이 KRW로 시작하지 않음: {second_line}")
                            # 첫 번째 줄 데이터만으로 행 추가 (빈 값으로 나머지 채움)
                            try:
                                combined_row = []
                                # 첫 번째 줄에서 가능한 만큼 데이터 추출
                                for idx in range(min(len(first_data), 7)):
                                    combined_row.append(first_data[idx])
                                    
                                # 부족한 필드 빈 값으로 채움
                                combined_row.extend([''] * (14 - len(combined_row)))
                                consolidated_data.append(combined_row)
                                logger.debug(f"첫 번째 줄만으로 행 추가: {combined_row}")
                            except Exception as e:
                                logger.error(f"첫 번째 줄 처리 중 오류: {e}, 라인: {first_line}")
                            
                            i += 1  # 다음 줄로 이동
                            continue
            i += 1  # 다음 줄로 이동
        
        logger.info(f"변환된 데이터 행 수: {len(consolidated_data)}")
        
        # 엑셀 파일로 저장
        if output_file.endswith('.csv'):
            # CSV로 저장
            with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for row in consolidated_data:
                    writer.writerow(row)
        else:
            # 기본값으로 엑셀(xlsx) 파일 생성
            if not output_file.endswith('.xlsx'):
                output_file += '.xlsx'
                
            # 판다스 데이터프레임 생성
            df = pd.DataFrame(consolidated_data, columns=headers)
            
            # 엑셀 파일로 저장
            df.to_excel(output_file, index=False, sheet_name='주식거래내역')
            
            # 엑셀 파일 서식 지정
            wb = openpyxl.load_workbook(output_file)
            ws = wb.active
            
            # 헤더 스타일 지정
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col)
                cell.font = openpyxl.styles.Font(bold=True)
                cell.alignment = openpyxl.styles.Alignment(horizontal='center')
                
            # 열 너비 자동 조정
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column].width = adjusted_width
                
            wb.save(output_file)
        
        logger.info(f"변환 완료: {output_file}에 저장되었습니다.")
        return consolidated_data  # 변환된 데이터 반환
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# 사용 예시
if __name__ == "__main__":
    # PDF 파일에서 추출하여 엑셀로 변환
    try:
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler("stock_converter.log", encoding='utf-8'),
                                logging.StreamHandler()
                            ])
        
        pdf_path = r"C:\Users\User\Documents\개인자료\미국세금신고\증권거래내역\아내자료\키움증권 거래내역 2024년.pdf"  # 입력 PDF 파일 경로
        excel_path = r"C:\Users\User\Documents\개인자료\미국세금신고\증권거래내역\아내자료\키움증권 거래내역 2024년.xlsx"  # 출력 엑셀 파일 경로
        
        logger.info(f"변환 시작: {pdf_path} -> {excel_path}")
        
        result = convert_stock_transactions(
            pdf_path,
            excel_path,
            is_pdf=True,
            pdf_start_page=2,
            skip_first_table=True  # 두 번째 페이지의 첫 번째 표 건너뛰기
        )
        
        if result:
            logger.info(f"성공적으로 변환 완료. 총 {len(result)}개 거래내역 추출.")
        else:
            logger.error("변환 실패. 로그 파일을 확인하세요.")
            
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())

