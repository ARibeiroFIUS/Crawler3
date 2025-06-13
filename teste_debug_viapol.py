#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug específico para o problema da Viapol
"""

import pandas as pd
from app import match_client_in_text

def teste_direto():
    # Simular texto do PDF que contém apenas Viapol
    texto_pdf = """
    EMPRESA: Viapol Ltda.
    Esta empresa é a Viapol.
    Contrato com Viapol para fornecimento de materiais.
    Viapol é responsável pelo projeto.
    """
    
    # Lista de clientes do Excel (simulando o que o usuário tem)
    clientes_excel = ['Viapol']  # Apenas Viapol deveria ser encontrado
    
    print("=== TESTE DEBUG VIAPOL ===")
    print(f"Texto do PDF: {texto_pdf.strip()}")
    print(f"Clientes no Excel: {clientes_excel}")
    print()
    
    # Testar cada cliente
    for cliente in clientes_excel:
        resultado = match_client_in_text(cliente, texto_pdf, 80)
        print(f"Cliente: {cliente}")
        print(f"  Encontrado: {resultado['found']}")
        print(f"  Confiança: {resultado['confidence']}%")
        print(f"  Alias usado: {resultado['alias']}")
        print(f"  Contexto: {resultado['context']}")
        print()

def teste_com_outros_nomes():
    """Testar se outros nomes estão sendo encontrados incorretamente"""
    
    texto_pdf = """
    EMPRESA: Viapol Ltda.
    Esta empresa é a Viapol.
    Contrato com Viapol para fornecimento de materiais.  
    """
    
    # Nomes que NÃO deveriam ser encontrados
    nomes_teste = [
        'Via Pol',      # Separado
        'Via',          # Parcial
        'Pol',          # Parcial  
        'Vial',         # Parecido
        'Vapol',        # Typo
        'Cliente A',    # Completamente diferente
        'Empresa X'     # Completamente diferente
    ]
    
    print("=== TESTE FALSOS POSITIVOS ===")
    print(f"Texto: {texto_pdf.strip()}")
    print()
    
    for nome in nomes_teste:
        resultado = match_client_in_text(nome, texto_pdf, 80)
        if resultado['found']:
            print(f"⚠️  PROBLEMA: '{nome}' foi encontrado incorretamente!")
            print(f"   Confiança: {resultado['confidence']}%")
            print(f"   Alias: {resultado['alias']}")
            print(f"   Contexto: {resultado['context']}")
            print()
        else:
            print(f"✅ '{nome}' corretamente NÃO encontrado (confiança: {resultado['confidence']}%)")

if __name__ == "__main__":
    teste_direto()
    print("\n" + "="*50 + "\n")
    teste_com_outros_nomes() 