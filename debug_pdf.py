#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Debug para PDF
========================
Testa a extração de texto do PDF e busca por EMS
"""

import PyPDF2
import pandas as pd
from fuzzywuzzy import fuzz
import re

def debug_pdf_extraction(pdf_path):
    """Debug da extração de texto do PDF."""
    print("🔍 DEBUG: Iniciando extração de texto do PDF...")
    
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"🔍 DEBUG: PDF tem {len(reader.pages)} páginas")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                print(f"🔍 DEBUG: Página {i+1} - {len(page_text)} caracteres extraídos")
                
                # Mostrar primeiros 200 caracteres de cada página
                preview = page_text[:200].replace('\n', '\\n')
                print(f"🔍 DEBUG: Página {i+1} preview: {preview}...")
                
                # Buscar EMS especificamente nesta página
                if 'ems' in page_text.lower():
                    print(f"🔍 DEBUG: *** EMS ENCONTRADO NA PÁGINA {i+1}! ***")
                    # Mostrar contexto onde EMS aparece
                    lines = page_text.split('\n')
                    for j, line in enumerate(lines):
                        if 'ems' in line.lower():
                            print(f"🔍 DEBUG: Linha {j+1}: {line.strip()}")
                
                text += page_text + "\n"
        
        print(f"🔍 DEBUG: Total de texto extraído: {len(text)} caracteres")
        
        # Buscar EMS no texto completo
        text_lower = text.lower()
        if 'ems' in text_lower:
            print("🔍 DEBUG: *** EMS ENCONTRADO NO TEXTO COMPLETO! ***")
            
            # Encontrar todas as ocorrências
            import re
            matches = list(re.finditer(r'ems[^a-z]*', text_lower))
            print(f"🔍 DEBUG: {len(matches)} ocorrências de EMS encontradas:")
            
            for i, match in enumerate(matches):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')
                print(f"🔍 DEBUG: Ocorrência {i+1}: ...{context}...")
        else:
            print("🔍 DEBUG: *** EMS NÃO ENCONTRADO NO TEXTO! ***")
            
        return text
        
    except Exception as e:
        print(f"🔍 DEBUG: ERRO ao extrair PDF: {e}")
        import traceback
        traceback.print_exc()
        return ""

def debug_excel_clients(excel_path):
    """Debug da leitura do Excel."""
    print("🔍 DEBUG: Lendo arquivo Excel...")
    
    try:
        df = pd.read_excel(excel_path)
        print(f"🔍 DEBUG: Excel tem {len(df)} linhas e {len(df.columns)} colunas")
        print(f"🔍 DEBUG: Colunas: {list(df.columns)}")
        print(f"🔍 DEBUG: Primeiras 10 linhas da primeira coluna:")
        
        clients = df.iloc[:, 0].dropna().astype(str).tolist()
        for i, client in enumerate(clients[:10]):
            print(f"🔍 DEBUG: Cliente {i+1}: '{client}'")
            if 'ems' in client.lower():
                print(f"🔍 DEBUG: *** EMS ENCONTRADO NO EXCEL: '{client}' ***")
        
        return clients
        
    except Exception as e:
        print(f"🔍 DEBUG: ERRO ao ler Excel: {e}")
        return []

def debug_search_algorithms(client, pdf_text):
    """Debug dos algoritmos de busca."""
    print(f"\n🔍 DEBUG: Testando algoritmos para cliente: '{client}'")
    
    client_lower = str(client).lower().strip()
    pdf_lower = pdf_text.lower()
    
    print(f"🔍 DEBUG: Cliente normalizado: '{client_lower}'")
    
    # 1. Busca exata
    exact_match = client_lower in pdf_lower
    print(f"🔍 DEBUG: Busca exata: {exact_match}")
    
    # 2. Busca sem pontuação
    client_clean = re.sub(r'[^\w\s]', '', client_lower)
    pdf_clean = re.sub(r'[^\w\s]', '', pdf_lower)
    clean_match = client_clean in pdf_clean
    print(f"🔍 DEBUG: Cliente limpo: '{client_clean}'")
    print(f"🔍 DEBUG: Busca sem pontuação: {clean_match}")
    
    # 3. Busca por palavras
    client_words = client_clean.split()
    word_matches = []
    for word in client_words:
        if len(word) >= 3:
            if word in pdf_clean:
                word_matches.append(word)
                print(f"🔍 DEBUG: Palavra '{word}' ENCONTRADA!")
            else:
                print(f"🔍 DEBUG: Palavra '{word}' NÃO encontrada")
    
    print(f"🔍 DEBUG: Palavras encontradas: {word_matches}")
    
    # 4. Busca fuzzy
    similarity_partial = fuzz.partial_ratio(client_lower, pdf_lower)
    similarity_token = fuzz.token_sort_ratio(client_lower, pdf_lower)
    similarity_set = fuzz.token_set_ratio(client_lower, pdf_lower)
    
    print(f"🔍 DEBUG: Similaridade partial: {similarity_partial}%")
    print(f"🔍 DEBUG: Similaridade token_sort: {similarity_token}%")
    print(f"🔍 DEBUG: Similaridade token_set: {similarity_set}%")
    
    best_similarity = max(similarity_partial, similarity_token, similarity_set)
    print(f"🔍 DEBUG: Melhor similaridade: {best_similarity}%")

def main():
    """Função principal de debug."""
    print("🚀 INICIANDO DEBUG DO CRAWLER PDF")
    print("=" * 50)
    
    # Caminhos dos arquivos
    excel_path = "clientes.xlsx"
    pdf_path = "documento.pdf"
    
    # 1. Debug do Excel
    print("\n📊 DEBUGANDO EXCEL:")
    clients = debug_excel_clients(excel_path)
    
    # 2. Debug do PDF
    print("\n📄 DEBUGANDO PDF:")
    pdf_text = debug_pdf_extraction(pdf_path)
    
    # 3. Debug específico para EMS
    print("\n🔍 DEBUGANDO BUSCA POR EMS:")
    ems_clients = [c for c in clients if 'ems' in c.lower()]
    
    if ems_clients:
        for ems_client in ems_clients:
            debug_search_algorithms(ems_client, pdf_text)
    else:
        print("🔍 DEBUG: Nenhum cliente EMS encontrado no Excel")
        
        # Testar com EMS S.A. manualmente
        print("🔍 DEBUG: Testando 'EMS S.A.' manualmente:")
        debug_search_algorithms("EMS S.A.", pdf_text)

if __name__ == "__main__":
    main() 