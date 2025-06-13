#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Criar PDF com EMS para Teste
============================
Gera um PDF que contém EMS S.A. para testar o crawler
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def criar_pdf_com_ems():
    """Cria um PDF de teste com EMS S.A."""
    
    filename = "documento_com_ems.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Página 1
    c.drawString(100, height - 100, "DOCUMENTO DE TESTE - CRAWLER PDF")
    c.drawString(100, height - 130, "=" * 50)
    c.drawString(100, height - 160, "Este documento contém informações sobre diversos clientes.")
    c.drawString(100, height - 190, "")
    c.drawString(100, height - 220, "CLIENTES LISTADOS:")
    c.drawString(100, height - 250, "• Cliente A - Empresa de tecnologia")
    c.drawString(100, height - 280, "• Cliente B - Consultoria empresarial")
    c.drawString(100, height - 310, "• EMS S.A. - Empresa farmacêutica")
    c.drawString(100, height - 340, "• Cliente D - Indústria alimentícia")
    c.drawString(100, height - 370, "• Cliente E - Setor automotivo")
    c.drawString(100, height - 400, "")
    c.drawString(100, height - 430, "DETALHES DOS CLIENTES:")
    c.drawString(100, height - 460, "")
    c.drawString(100, height - 490, "EMS S.A. é uma das maiores empresas farmacêuticas do Brasil.")
    c.drawString(100, height - 520, "A EMS possui diversos produtos no mercado nacional.")
    c.drawString(100, height - 550, "Contrato com EMS S.A. foi renovado em 2024.")
    
    # Adicionar mais páginas para simular um documento maior
    for page_num in range(2, 20):
        c.showPage()
        c.drawString(100, height - 100, f"PÁGINA {page_num}")
        c.drawString(100, height - 130, "=" * 20)
        
        if page_num == 19:
            # Página 19 - onde você disse que EMS aparece várias vezes
            c.drawString(100, height - 160, "PÁGINA 19 - INFORMAÇÕES ESPECIAIS SOBRE EMS")
            c.drawString(100, height - 190, "")
            c.drawString(100, height - 220, "EMS S.A. - Relatório Detalhado:")
            c.drawString(100, height - 250, "• EMS S.A. fundada em 1964")
            c.drawString(100, height - 280, "• EMS é líder no mercado farmacêutico")
            c.drawString(100, height - 310, "• Produtos EMS são distribuídos nacionalmente")
            c.drawString(100, height - 340, "• EMS S.A. tem sede em São Paulo")
            c.drawString(100, height - 370, "• Faturamento da EMS cresceu 15% em 2023")
            c.drawString(100, height - 400, "• EMS investe em pesquisa e desenvolvimento")
            c.drawString(100, height - 430, "• Parceria com EMS S.A. é estratégica")
            c.drawString(100, height - 460, "• EMS possui mais de 10.000 funcionários")
            c.drawString(100, height - 490, "• EMS S.A. exporta para 15 países")
            c.drawString(100, height - 520, "• Certificações da EMS incluem ISO 9001")
        else:
            c.drawString(100, height - 160, f"Conteúdo da página {page_num}")
            c.drawString(100, height - 190, "Esta é uma página de exemplo.")
            if page_num % 3 == 0:
                c.drawString(100, height - 220, "Menção ocasional: EMS é uma empresa conhecida.")
    
    c.save()
    print(f"✅ PDF criado: {filename}")
    print("📄 O PDF contém:")
    print("   • 19 páginas")
    print("   • EMS S.A. mencionado várias vezes")
    print("   • Página 19 com múltiplas referências a EMS")

def criar_excel_com_ems():
    """Cria um Excel de teste com EMS S.A."""
    import pandas as pd
    
    clientes = [
        "Cliente A",
        "Cliente B", 
        "EMS S.A.",
        "Cliente D",
        "Cliente E"
    ]
    
    df = pd.DataFrame({"Nome do Cliente": clientes})
    filename = "clientes_com_ems.xlsx"
    df.to_excel(filename, index=False)
    
    print(f"✅ Excel criado: {filename}")
    print("📊 O Excel contém:")
    for i, cliente in enumerate(clientes, 1):
        print(f"   {i}. {cliente}")

if __name__ == "__main__":
    print("🚀 CRIANDO ARQUIVOS DE TESTE COM EMS")
    print("=" * 40)
    
    criar_pdf_com_ems()
    print()
    criar_excel_com_ems()
    
    print("\n🎯 ARQUIVOS CRIADOS PARA TESTE:")
    print("   • documento_com_ems.pdf")
    print("   • clientes_com_ems.xlsx")
    print("\n📝 Use estes arquivos para testar o crawler!") 