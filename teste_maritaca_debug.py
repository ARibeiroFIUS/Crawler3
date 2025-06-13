#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de Diagnóstico - API Maritaca Sabiá-3
==========================================
Verifica se a API está funcionando e diagnostica falsos positivos
"""

import os
import sys
import json
from typing import List
from pydantic import BaseModel

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PalavrasChave(BaseModel):
    """Modelo Pydantic para saídas estruturadas da Maritaca"""
    palavras_significativas: List[str]
    justificativa: str

def testar_api_maritaca():
    """Testa se a API Maritaca está funcionando"""
    
    print("🔍 TESTE 1: Verificando API Maritaca...")
    
    # Solicitar chave da API
    api_key = input("Digite sua chave da API Maritaca (ou Enter para pular): ").strip()
    
    if not api_key:
        print("❌ Sem chave da API - usando método fallback")
        return False
    
    try:
        import openai
        
        # Cliente configurado para Maritaca
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        
        # Teste simples
        prompt = """
Analise o nome da empresa "EMS S.A." e extraia as 1-2 palavras mais significativas.

REGRAS:
- Ignore: S.A., LTDA, EIRELI, ME, CIA
- Se for sigla, mantenha apenas a sigla
- MÁXIMO 2 palavras

Exemplo: "EMS S.A." → ["EMS"]
"""

        completion = client.beta.chat.completions.parse(
            model="sabia-3",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de nomes de empresas."},
                {"role": "user", "content": prompt}
            ],
            response_format=PalavrasChave,
            max_tokens=200,
            temperature=0.1
        )
        
        resultado = completion.choices[0].message.parsed
        
        if resultado and resultado.palavras_significativas:
            print(f"✅ API Maritaca funcionando!")
            print(f"   Teste com 'EMS S.A.': {resultado.palavras_significativas}")
            print(f"   Justificativa: {resultado.justificativa}")
            return True
        else:
            print("❌ API retornou resposta vazia")
            return False
            
    except Exception as e:
        print(f"❌ Erro na API Maritaca: {e}")
        return False

def testar_casos_problematicos():
    """Testa casos que podem gerar falsos positivos"""
    
    print("\n🔍 TESTE 2: Casos Problemáticos...")
    
    casos_teste = [
        {
            'nome': 'EMS S.A.',
            'texto_pdf': 'Este documento não tem relação com EMS não se aplica ao caso.',
            'deveria_encontrar': False,
            'motivo': 'EMS em contexto irrelevante'
        },
        {
            'nome': 'Viapol Ltda',
            'texto_pdf': 'A empresa VIAPOL forneceu os materiais conforme especificado.',
            'deveria_encontrar': True,
            'motivo': 'Viapol em contexto relevante'
        },
        {
            'nome': 'QGC Engenharia',
            'texto_pdf': 'Via de regra, os materiais são fornecidos pela QGC.',
            'deveria_encontrar': True,
            'motivo': 'QGC mencionada corretamente'
        },
        {
            'nome': 'Sun Ace Brasil',
            'texto_pdf': 'Informações sobre EMS não constam neste documento.',
            'deveria_encontrar': False,
            'motivo': 'Sun Ace não mencionada, apenas EMS irrelevante'
        }
    ]
    
    # Importar funções do app principal
    try:
        from app_maritaca_correto import extrair_palavras_chave_simples, buscar_palavras_chave_no_texto_rigoroso
    except ImportError:
        print("❌ Erro ao importar funções do app principal")
        return
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n--- Caso {i}: {caso['nome']} ---")
        
        # Extrair palavras-chave
        palavras_chave = extrair_palavras_chave_simples(caso['nome'])
        print(f"Palavras-chave extraídas: {palavras_chave}")
        
        # Buscar no texto
        resultado = buscar_palavras_chave_no_texto_rigoroso(palavras_chave, caso['texto_pdf'], 90)
        
        print(f"Encontrado: {resultado['found']}")
        print(f"Deveria encontrar: {caso['deveria_encontrar']}")
        print(f"Confiança: {resultado['confidence']}%")
        print(f"Contexto: {resultado['context'][:100]}...")
        
        # Verificar se o resultado está correto
        if resultado['found'] == caso['deveria_encontrar']:
            print("✅ CORRETO")
        else:
            print("❌ INCORRETO - Possível problema!")
            print(f"   Motivo esperado: {caso['motivo']}")

def testar_com_pdf_real():
    """Permite testar com um PDF real"""
    
    print("\n🔍 TESTE 3: PDF Real (Opcional)...")
    
    pdf_path = input("Digite o caminho do PDF para testar (ou Enter para pular): ").strip()
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("❌ PDF não encontrado - pulando teste")
        return
    
    excel_path = input("Digite o caminho do Excel com clientes (ou Enter para pular): ").strip()
    
    if not excel_path or not os.path.exists(excel_path):
        print("❌ Excel não encontrado - pulando teste")
        return
    
    try:
        import pandas as pd
        import PyPDF2
        from app_maritaca_correto import extrair_palavras_chave_simples, buscar_palavras_chave_no_texto_rigoroso
        
        # Ler clientes
        df = pd.read_excel(excel_path)
        clientes = df.iloc[:, 0].dropna().tolist()[:5]  # Apenas 5 primeiros
        
        # Ler PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            texto_pdf = ""
            for page in pdf_reader.pages:
                texto_pdf += page.extract_text() + "\n"
        
        print(f"\nTestando {len(clientes)} clientes...")
        
        for cliente in clientes:
            print(f"\n--- Cliente: {cliente} ---")
            
            palavras_chave = extrair_palavras_chave_simples(cliente)
            print(f"Palavras-chave: {palavras_chave}")
            
            resultado = buscar_palavras_chave_no_texto_rigoroso(palavras_chave, texto_pdf, 90)
            
            print(f"Encontrado: {resultado['found']}")
            print(f"Confiança: {resultado['confidence']}%")
            
            if resultado['found']:
                print(f"Contexto: {resultado['context'][:150]}...")
                
                # Perguntar ao usuário se está correto
                resposta = input("Este resultado está CORRETO? (s/n): ").strip().lower()
                if resposta == 'n':
                    print("❌ FALSO POSITIVO DETECTADO!")
                    print("   Este caso precisa ser corrigido no algoritmo.")
                else:
                    print("✅ Resultado correto")
    
    except Exception as e:
        print(f"❌ Erro no teste com PDF real: {e}")

def main():
    """Função principal de diagnóstico"""
    
    print("=" * 60)
    print("🔬 DIAGNÓSTICO MARITACA SABIÁ-3")
    print("=" * 60)
    
    # Teste 1: API
    api_funcionando = testar_api_maritaca()
    
    # Teste 2: Casos problemáticos
    testar_casos_problematicos()
    
    # Teste 3: PDF real (opcional)
    testar_com_pdf_real()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    if api_funcionando:
        print("✅ API Maritaca: FUNCIONANDO")
    else:
        print("❌ API Maritaca: PROBLEMA ou SEM CHAVE")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("1. Se a API não funciona, o sistema usa método fallback")
    print("2. Verifique se os falsos positivos são detectados corretamente")
    print("3. Ajuste os padrões de detecção se necessário")
    print("4. Use threshold mínimo de 90% para máxima precisão")

if __name__ == "__main__":
    main()