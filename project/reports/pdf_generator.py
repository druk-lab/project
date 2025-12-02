from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def simple_pdf(path: str, title: str, lines: list[str]):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30
    c.setFont("Helvetica", 10)
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 14
    c.showPage()
    c.save()
