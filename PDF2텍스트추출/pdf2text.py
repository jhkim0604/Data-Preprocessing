import pdfplumber

# PDF 파일 경로와 출력 텍스트 파일 경로
#pdf_path = r"C:\data\pdfFolder2Text\주간보고(김진호) 10-24.pdf"
pdf_path = r"C:\data\rfp_pdf\SR-MaaS 통합정보시스템-감리.pdf"
#output_path = r"C:\data\pdfFolder2Text-output\주간보고(김진호) 10-24.txt"
output_path = r"C:\data\rfp_txt\SR-MaaS 통합정보시스템-감리.txt"

# 텍스트 추출 및 파일 저장 함수
def extract_text_from_pdf(pdf_path, output_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
    # 텍스트 파일에 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"텍스트가 '{output_path}'에 저장되었습니다.")

# 텍스트 추출 및 저장 실행
extract_text_from_pdf(pdf_path, output_path)
