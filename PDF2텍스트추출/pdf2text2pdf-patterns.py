import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter

# PDF 파일 경로
pdf_path = r"C:\\data\\rfp_pdf\\법률구조서비스 플랫폼 구축사업 감리.pdf"
txt_output_path = r"C:\\data\\rfp_txt\\법률구조서비스 플랫폼 구축사업 감리.txt"
pdf_output_path = r"C:\\data\\rfp_pdf\\법률구조서비스 플랫폼 구축사업 감리-output.pdf"

# 폰트 경로
#font_path = r"C:\\path\\to\\NanumGothic.ttf"  # 폰트 파일 경로 설정
font_path = r"C:\fonts\nanum-all\나눔 글꼴\나눔고딕\NanumFontSetup_TTF_GOTHIC\NanumGothic.ttf"

# 텍스트 추출 및 저장 함수
def extract_text_from_pdf_excluding_keywords(pdf_path, txt_output_path, exclude_keywords):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            # 키워드가 포함된 페이지는 제외
            if any(keyword in page_text for keyword in exclude_keywords):
                continue

            text += page_text + "\n"

    with open(txt_output_path, "w", encoding="utf-8") as file:
        file.write(text)

    return text

# 텍스트를 PDF로 저장 함수
def save_text_to_pdf_from_file(txt_input_path, pdf_output_path):
    # 한글 폰트 등록
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))

    with open(txt_input_path, "r", encoding="utf-8") as file:
        text = file.read()

    c = canvas.Canvas(pdf_output_path, pagesize=letter)
    c.setFont("NanumGothic", 10)  # 등록한 폰트를 사용
    width, height = letter

    lines = text.split("\n")

    x_margin = 50
    y_position = height - 50
    line_height = 12

    for line in lines:
        if y_position < 50:  # 페이지 하단에 도달하면 새로운 페이지
            c.showPage()
            c.setFont("NanumGothic", 10)  # 새로운 페이지에서도 폰트 설정
            y_position = height - 50
        c.drawString(x_margin, y_position, line)
        y_position -= line_height

    c.save()

# 제외할 키워드 설정 (예: "별지", "서식", "붙임", "별첨")
exclude_keywords = ["별지", "서식", "붙임", "별첨", "별 첨"]

# 텍스트 추출 및 파일 저장 실행
extracted_text = extract_text_from_pdf_excluding_keywords(pdf_path, txt_output_path, exclude_keywords)
print(f"텍스트가 {txt_output_path}에 저장되었습니다.")

# 저장된 텍스트 파일을 읽어서 PDF로 저장 실행
save_text_to_pdf_from_file(txt_output_path, pdf_output_path)
print(f"텍스트가 {pdf_output_path}에 PDF 형식으로 저장되었습니다.")
