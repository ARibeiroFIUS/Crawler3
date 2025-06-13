from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename, content):
    c = canvas.Canvas(filename, pagesize=letter)
    textobject = c.beginText()
    textobject.setTextOrigin(50, 750)
    textobject.setFont("Helvetica", 12)
    for line in content.split("\n"):
        textobject.textLine(line)
    c.drawText(textobject)
    c.save()


pdf_content = """
Este é um documento de exemplo para testar o crawler.

Contém informações sobre vários clientes.

Cliente A é um cliente muito importante.
Cliente B tem um contrato recente.
O Cliente C está em negociação.
Cliente F não está na lista.
"""

create_pdf("documento.pdf", pdf_content)


