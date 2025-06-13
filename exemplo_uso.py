#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de Uso do Crawler de Clientes em PDF
===========================================

Este script demonstra como usar a versão avançada do crawler
para seus próprios arquivos Excel e PDF.
"""

from crawler_advanced import PDFClientCrawler

def exemplo_basico():
    """Exemplo básico de uso do crawler."""
    print("🔍 Executando exemplo básico...")
    
    # Criar instância do crawler
    crawler = PDFClientCrawler(threshold=80, verbose=True)
    
    # Processar arquivos (substitua pelos seus arquivos)
    stats = crawler.process_files(
        excel_path="clientes.xlsx",      # Seu arquivo Excel
        pdf_path="documento.pdf",        # Seu arquivo PDF
        output_path="output/meus_resultados.xlsx"  # Arquivo de saída
    )
    
    if stats:
        print(f"\n✅ Processamento concluído com sucesso!")
        print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
    else:
        print("\n❌ Erro no processamento.")

def exemplo_personalizado():
    """Exemplo com configurações personalizadas."""
    print("\n🔧 Executando exemplo personalizado...")
    
    # Crawler com tolerância maior e modo silencioso
    crawler = PDFClientCrawler(threshold=90, verbose=False)
    
    # Especificar coluna e aba diferentes do Excel
    stats = crawler.process_files(
        excel_path="clientes.xlsx",
        pdf_path="documento.pdf",
        output_path="output/resultados_personalizados.xlsx",
        excel_column=0,  # Primeira coluna (0-indexado)
        excel_sheet=0    # Primeira aba (0-indexado)
    )
    
    if stats:
        print(f"✅ Processamento personalizado concluído!")
        print(f"Clientes encontrados: {stats['found_clients']}/{stats['total_clients']}")

def exemplo_multiplos_algoritmos():
    """Exemplo mostrando como os algoritmos de similaridade funcionam."""
    print("\n🧠 Demonstrando algoritmos de similaridade...")
    
    from fuzzywuzzy import fuzz
    
    # Exemplos de nomes com variações
    cliente_original = "João da Silva"
    variações = [
        "João Silva",          # Nome parcial
        "JOÃO DA SILVA",       # Maiúsculas
        "Joao da Silva",       # Sem acento
        "J. da Silva",         # Abreviado
        "João da Silva Jr.",   # Com sufixo
        "Silva, João da"       # Ordem invertida
    ]
    
    print(f"Cliente original: '{cliente_original}'")
    print("\nComparações de similaridade:")
    
    for variacao in variações:
        ratio = fuzz.ratio(cliente_original.lower(), variacao.lower())
        partial = fuzz.partial_ratio(cliente_original.lower(), variacao.lower())
        token = fuzz.token_sort_ratio(cliente_original.lower(), variacao.lower())
        
        print(f"  '{variacao}':")
        print(f"    Ratio: {ratio}% | Partial: {partial}% | Token: {token}%")
        print(f"    Seria encontrado com tolerância 80%: {'Sim' if max(ratio, partial, token) >= 80 else 'Não'}")

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 EXEMPLOS DE USO DO CRAWLER DE CLIENTES EM PDF")
    print("=" * 60)
    
    # Executar exemplos
    exemplo_basico()
    exemplo_personalizado()
    exemplo_multiplos_algoritmos()
    
    print("\n" + "=" * 60)
    print("📚 DICAS DE USO:")
    print("=" * 60)
    print("1. Coloque seu arquivo Excel e PDF na pasta do projeto")
    print("2. Use tolerância 70-90% dependendo da qualidade dos dados")
    print("3. Verifique se a coluna correta está sendo lida do Excel")
    print("4. Os resultados são salvos com metadados detalhados")
    print("5. Use 'python crawler_advanced.py --help' para ver todas as opções")
    print("=" * 60) 