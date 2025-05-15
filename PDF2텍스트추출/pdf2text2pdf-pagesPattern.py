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
def extract_text_from_pdf_excluding_ranges_and_keywords(pdf_path, txt_output_path, exclude_ranges, exclude_keywords):
    text = ""
    excluded_pages = set()
    for start, end in exclude_ranges:
        excluded_pages.update(range(start, end + 1))

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i + 1 in excluded_pages:
                continue

            page_text = page.extract_text()
            if any(keyword in page_text for keyword in exclude_keywords):
                continue

            text += page_text + "\n"

    with open(txt_output_path, "w", encoding="utf-8") as file:
        file.write(text)

    return text

# 텍스트를 PDF로 저장 함수
def save_text_to_pdf(text, pdf_output_path):
    # 한글 폰트 등록
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))

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

# 제외할 페이지 범위 설정 (예: 2-3 페이지와 5-6 페이지 제외)
#exclude_ranges = [(2, 3), (5, 6)]
exclude_ranges = [(52,53)]

# 제외할 키워드 설정 (예: "붙임", "양식")
exclude_keywords = ["붙임", "서식", "별지", "별첨"]

# 텍스트 추출 및 파일 저장 실행
extracted_text = extract_text_from_pdf_excluding_ranges_and_keywords(pdf_path, txt_output_path, exclude_ranges, exclude_keywords)
print(f"텍스트가 {txt_output_path}에 저장되었습니다.")

# 텍스트를 PDF로 저장 실행
save_text_to_pdf(extracted_text, pdf_output_path)
print(f"텍스트가 {pdf_output_path}에 PDF 형식으로 저장되었습니다.")
