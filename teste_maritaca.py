#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da Nova Versão V4.0 com IA Maritaca
==========================================
Demonstra como a IA extrai palavras-chave significativas
"""

import pandas as pd
from app_maritaca import extrair_palavras_chave_simples, buscar_palavras_chave_no_texto

def teste_extracao_palavras_chave():
    """Testa a extração de palavras-chave de diferentes tipos de nomes"""
    
    print("🧠 TESTE: Extração de Palavras-Chave")
    print("="*50)
    
    # Casos de teste
    casos_teste = [
        "EMS S.A.",
        "Viapol Ltda",
        "Produtos Alimentícios Café Ltda",
        "Aços Equipamentos e Serviços de Informática Ltda",
        "Sun Ace Brasil Indústria e Comércio Ltda",
        "QGC Engenharia",
        "Via Pol Materiais",  # Caso problemático
        "Empresa ABC ME"
    ]
    
    for nome in casos_teste:
        palavras = extrair_palavras_chave_simples(nome)
        print(f"'{nome}' → {palavras}")
    
    print()

def teste_busca_otimizada():
    """Testa a busca otimizada com palavras-chave"""
    
    print("🔍 TESTE: Busca Otimizada com Palavras-Chave")
    print("="*50)
    
    # Texto do PDF simulado
    texto_pdf = """
    CONTRATO DE FORNECIMENTO
    
    Empresa contratada: Viapol Ltda
    CNPJ: 12.345.678/0001-90
    
    A empresa Viapol é responsável pelo fornecimento de materiais
    de construção para o projeto XYZ.
    
    Outras informações sobre EMS não se aplicam aqui.
    Via de regra, todos os contratos devem ser assinados.
    """
    
    # Casos de teste
    casos_teste = [
        ("Viapol", ["viapol"]),           # Deveria encontrar
        ("EMS S.A.", ["ems"]),            # NÃO deveria encontrar (EMS aparece em contexto diferente)
        ("Via Pol", ["via", "pol"]),      # NÃO deveria encontrar (palavras separadas)
        ("QGC", ["qgc"]),                 # NÃO deveria encontrar
        ("Materiais", ["materiais"])      # Poderia encontrar (palavra genérica no texto)
    ]
    
    for nome_cliente, palavras_chave in casos_teste:
        resultado = buscar_palavras_chave_no_texto(palavras_chave, texto_pdf, 85)
        
        status = "✅ ENCONTRADO" if resultado['found'] else "❌ NÃO ENCONTRADO"
        print(f"{nome_cliente} (palavras: {palavras_chave})")
        print(f"  {status} - Confiança: {resultado['confidence']}%")
        print(f"  Palavras encontradas: {resultado['palavras_encontradas']}")
        print(f"  Contexto: {resultado['context'][:80]}...")
        print()

def teste_comparacao_versoes():
    """Compara a versão antiga com a nova"""
    
    print("⚖️  TESTE: Comparação V3 vs V4")
    print("="*50)
    
    # Importar função da versão antiga
    from app import match_client_in_text
    
    texto_pdf = """
    Empresa: Viapol Ltda
    Fornecimento de materiais para construção.
    EMS não tem relação com este contrato.
    """
    
    casos_problema = [
        "EMS S.A.",
        "Via Pol", 
        "Viapol"
    ]
    
    print("VERSÃO 3.0 (Antiga):")
    for cliente in casos_problema:
        resultado_v3 = match_client_in_text(cliente, texto_pdf, 80)
        status = "✅" if resultado_v3['found'] else "❌"
        print(f"  {status} {cliente}: {resultado_v3['confidence']}%")
    
    print("\nVERSÃO 4.0 (Nova com Palavras-Chave):")
    for cliente in casos_problema:
        palavras = extrair_palavras_chave_simples(cliente)
        resultado_v4 = buscar_palavras_chave_no_texto(palavras, texto_pdf, 85)
        status = "✅" if resultado_v4['found'] else "❌"
        print(f"  {status} {cliente} (palavras: {palavras}): {resultado_v4['confidence']}%")

def criar_exemplo_excel():
    """Cria um Excel de exemplo para teste"""
    
    clientes_exemplo = [
        "EMS S.A.",
        "Viapol Ltda", 
        "QGC Engenharia",
        "Sun Ace Brasil Indústria e Comércio Ltda",
        "Via Pol Materiais",  # Caso problemático
        "Produtos Alimentícios Café Ltda"
    ]
    
    df = pd.DataFrame({'Nome do Cliente': clientes_exemplo})
    df.to_excel('teste_clientes_v4.xlsx', index=False)
    print("📊 Arquivo criado: teste_clientes_v4.xlsx")

if __name__ == "__main__":
    print("🤖 TESTE CRAWLER PDF V4.0 - IA MARITACA")
    print("="*60)
    print()
    
    teste_extracao_palavras_chave()
    print()
    teste_busca_otimizada()
    print()
    teste_comparacao_versoes()
    print()
    criar_exemplo_excel()
    
    print("\n" + "="*60)
    print("✨ RESUMO DOS BENEFÍCIOS DA V4.0:")
    print("• Extrai apenas palavras-chave significativas")
    print("• Evita falsos positivos como 'EMS' em textos aleatórios")
    print("• Busca mais precisa e eficiente")
    print("• Suporte opcional à IA Maritaca para análise avançada")
    print("• Cache inteligente para evitar chamadas desnecessárias à API")
    print("\n🚀 Para usar: python3 app_maritaca.py") 