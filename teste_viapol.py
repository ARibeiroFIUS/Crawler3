#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste específico para problema com Viapol
"""

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Criar Excel apenas com Viapol
def criar_excel_viapol():
    data = {'Nome do Cliente': ['Viapol']}
    df = pd.DataFrame(data)
    df.to_excel('teste_viapol_clientes.xlsx', index=False)
    print("Excel criado: teste_viapol_clientes.xlsx")

# Criar PDF apenas com Viapol
def criar_pdf_viapol():
    c = canvas.Canvas("teste_viapol_documento.pdf", pagesize=letter)
    width, height = letter
    
    # Apenas Viapol no PDF
    c.drawString(100, height-100, "EMPRESA: Viapol")
    c.drawString(100, height-150, "Esta empresa é a Viapol Ltda.")
    c.drawString(100, height-200, "Contrato com Viapol para fornecimento.")
    
    c.save()
    print("PDF criado: teste_viapol_documento.pdf")

# Testar com o sistema atual
def testar_sistema():
    from app import CrawlerPDFV3
    
    crawler = CrawlerPDFV3()
    
    # Processar
    results = crawler.process_files(
        'teste_viapol_clientes.xlsx',
        'teste_viapol_documento.pdf', 
        80
    )
    
    print("\n=== RESULTADOS DO TESTE ===")
    print(f"Total de clientes no Excel: 1 (Viapol)")
    print(f"Total de resultados encontrados: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\nResultado {i}:")
        print(f"  Cliente: {result['cliente']}")
        print(f"  Encontrado: {result['encontrado']}")
        print(f"  Similaridade: {result['similaridade']}%")
        print(f"  Contexto: {result['contexto'][:100]}...")

if __name__ == "__main__":
    print("Criando arquivos de teste...")
    criar_excel_viapol()
    criar_pdf_viapol()
    
    print("\nTestando sistema...")
    testar_sistema() 