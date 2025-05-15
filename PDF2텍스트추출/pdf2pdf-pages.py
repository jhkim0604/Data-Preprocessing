import os
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from tkinter import Tk, filedialog

# 폰트 경로
font_path = r"C:\fonts\nanum-all\나눔 글꼴\나눔고딕\NanumFontSetup_TTF_GOTHIC\NanumGothic.ttf"

def extract_text_from_pdf(input_file, exclude_pages, exclude_ranges):
    try:

        excluded_pages = set(exclude_pages)
        for start, end in exclude_ranges:
            excluded_pages.update(range(start, end + 1))

        # 입력 PDF에서 텍스트 추출
        with pdfplumber.open(input_file) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages):
                if i + 1 in excluded_pages:
                    continue

                text += page.extract_text() + "\n"

        # 한글 폰트 등록
        pdfmetrics.registerFont(TTFont("NanumGothic", font_path))

        # 출력 파일 경로 생성
        input_dir, input_filename = os.path.split(input_file)
        input_name, input_ext = os.path.splitext(input_filename)
        output_file = os.path.join(input_dir, f"{input_name}-small.pdf")

        # 텍스트를 출력 PDF에 작성
        c = canvas.Canvas(output_file, pagesize=letter)
        c.setFont("NanumGothic", 10)  # 등록한 폰트를 사용")

        c.drawString(100, 800, "Extracted Text from PDF:")
        y = 780

        for line in text.splitlines():
            c.drawString(100, y, line)
            y -= 12
            if y < 40:  # 페이지가 꽉 차면 새 페이지
                c.showPage()
                c.setFont("NanumGothic", 10)  # 등록한 폰트를 사용
                y = 800

        c.save()
        print(f"텍스트가 성공적으로 {output_file}에 기록되었습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

def main():
    # 파일 선택 창
    root = Tk()
    root.withdraw()  # GUI 창 숨기기

    # 제외할 페이지와 범위 설정 예시
    #exclude_pages = [2, 4]  # 특정 페이지 제외 (예: 2번, 4번 페이지)
    #exclude_ranges = [(7, 9), (12, 14)]  # 특정 페이지 범위 제외 (예: 7-9, 12-14 페이지)  
    # SR 사업 SI RFP 삭제할 페이지와 페이지 범위
    exclude_pages = []   # SR 사업 SI RFP 삭제할 페이지
    exclude_ranges = [(48,335),(350,360)]     # SR 사업 SI RFP 삭제할 페이지 범위

    print("PDF 파일을 선택하세요.")
    input_file = filedialog.askopenfilename(
        title="PDF 파일 선택",
        filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
    )

    if not input_file:
        print("파일이 선택되지 않았습니다.")
        return

    extract_text_from_pdf(input_file, exclude_pages, exclude_ranges)

if __name__ == "__main__":
    main()
