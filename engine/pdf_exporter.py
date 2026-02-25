from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime


def generate_pdf_report(
    filename="legal_report.pdf",
    mapping_data=None,
    analysis_text=None,
    ocr_text=None,
    risk_data=None,
):
    os.makedirs("reports", exist_ok=True)

    path = os.path.join("reports", filename)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    y = height - 40

    def draw_line(text):
        nonlocal y
        if y < 50:
            c.showPage()
            y = height - 40
        c.drawString(40, y, text)
        y -= 18

    # Header
    draw_line("LexTransition AI — Legal Report")
    draw_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    draw_line("")
    draw_line("-------------------------------------------")
    draw_line("")

    # Mapping
    if mapping_data:
        draw_line("=== Mapping Result ===")
        for k, v in mapping_data.items():
            draw_line(f"{k}: {v}")
        draw_line(" ")

    # AI Analysis
    if analysis_text:
        draw_line("AI Analysis:")
        for line in analysis_text.split("\n"):
            draw_line(line)
        draw_line(" ")

    # OCR
    if ocr_text:
        draw_line("OCR Extracted Text:")
        for line in ocr_text.split("\n"):
            draw_line(line)
        draw_line(" ")

    # Risk
    if risk_data:
        draw_line("Risk Assessment:")
        for k, v in risk_data.items():
            draw_line(f"{k}: {v}")
        draw_line(" ")

    c.save()

    return path