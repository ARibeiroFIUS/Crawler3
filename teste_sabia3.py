#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da API Maritaca CORRETA com Sabiá-3
=========================================
Demonstra o uso correto da API oficial
"""

import os
from typing import List
from pydantic import BaseModel

# Modelo para saídas estruturadas
class PalavrasChave(BaseModel):
    palavras_significativas: List[str]
    justificativa: str

def teste_api_maritaca_oficial():
    """Testa a API oficial da Maritaca com sabiá-3"""
    
    print("🤖 TESTE: API Maritaca Oficial com Sabiá-3")
    print("="*60)
    
    # Verificar se openai está instalado
    try:
        import openai
        print("✅ Biblioteca openai encontrada")
    except ImportError:
        print("❌ Instale: pip install openai")
        return
    
    # Solicitar chave da API
    api_key = input("🔑 Cole sua chave da API Maritaca (ou Enter para pular): ").strip()
    
    if not api_key:
        print("⚠️  Pulando teste da API (sem chave)")
        return
    
    # Configurar cliente CORRETAMENTE
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://chat.maritaca.ai/api",
    )
    
    # Casos de teste
    casos_teste = [
        "EMS S.A.",
        "Viapol Ltda",
        "Produtos Alimentícios Café Ltda",
        "Sun Ace Brasil Indústria e Comércio Ltda",
        "QGC Engenharia",
        "Via Pol Materiais"
    ]
    
    print("\n🧠 TESTANDO EXTRAÇÃO DE PALAVRAS-CHAVE:")
    print("-" * 60)
    
    for nome_cliente in casos_teste:
        try:
            prompt = f"""
Analise o nome da empresa "{nome_cliente}" e extraia as 1-2 palavras mais significativas e únicas que melhor identificam esta empresa.

REGRAS RIGOROSAS:
- Ignore completamente: S.A., LTDA, EIRELI, ME, CIA, INC, CORP, DO, DA, DE, E, EM, COM
- Se for sigla (ex: EMS, QGC), mantenha APENAS a sigla
- Se for nome composto, escolha APENAS as palavras mais distintivas
- MÁXIMO 2 palavras
- Prefira palavras longas e específicas

EXEMPLOS:
- "EMS S.A." → ["EMS"]
- "Viapol Ltda" → ["Viapol"]  
- "Produtos Alimentícios Café Ltda" → ["Alimentícios", "Café"]

Retorne apenas as palavras mais importantes para identificar unicamente esta empresa.
"""

            # Usar saídas estruturadas com Pydantic
            completion = client.beta.chat.completions.parse(
                model="sabia-3",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de nomes de empresas. Extraia as palavras-chave mais significativas."},
                    {"role": "user", "content": prompt}
                ],
                response_format=PalavrasChave,
                max_tokens=200,
                temperature=0.1
            )
            
            resultado = completion.choices[0].message.parsed
            
            print(f"\n📊 {nome_cliente}")
            print(f"   Palavras: {resultado.palavras_significativas}")
            print(f"   Justificativa: {resultado.justificativa}")
            
        except Exception as e:
            print(f"\n❌ Erro com '{nome_cliente}': {e}")

def teste_api_simples():
    """Teste simples da API sem saídas estruturadas"""
    
    print("\n\n🔧 TESTE SIMPLES DA API:")
    print("="*60)
    
    api_key = input("🔑 Cole sua chave da API Maritaca: ").strip()
    
    if not api_key:
        print("⚠️  Teste cancelado (sem chave)")
        return
    
    try:
        import openai
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        
        response = client.chat.completions.create(
            model="sabia-3",
            messages=[
                {"role": "user", "content": "Quanto é 25 + 27?"},
            ],
            max_tokens=100
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Resposta do Sabiá-3: {answer}")
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    
    print("🔍 VERIFICANDO DEPENDÊNCIAS:")
    print("="*40)
    
    dependencias = {
        'openai': 'Biblioteca oficial OpenAI (compatível com Maritaca)',
        'pydantic': 'Para saídas estruturadas',
        'pandas': 'Para manipular Excel',
        'PyPDF2': 'Para ler PDFs',
        'rapidfuzz': 'Para busca fuzzy',
        'flask': 'Para interface web'
    }
    
    for dep, desc in dependencias.items():
        try:
            __import__(dep)
            print(f"✅ {dep}: {desc}")
        except ImportError:
            print(f"❌ {dep}: {desc} - INSTALAR: pip install {dep}")

if __name__ == "__main__":
    print("🤖 TESTE COMPLETO - API MARITACA OFICIAL")
    print("="*70)
    
    verificar_dependencias()
    
    print("\n" + "="*70)
    
    escolha = input("""
Escolha o teste:
1 - Teste completo com saídas estruturadas
2 - Teste simples da API
3 - Apenas verificar dependências

Digite 1, 2 ou 3: """).strip()
    
    if escolha == "1":
        teste_api_maritaca_oficial()
    elif escolha == "2":
        teste_api_simples()
    elif escolha == "3":
        print("✅ Verificação de dependências concluída")
    else:
        print("❌ Opção inválida")
    
    print("\n" + "="*70)
    print("📚 DOCUMENTAÇÃO OFICIAL:")
    print("• API: https://chat.maritaca.ai/api")
    print("• Docs: https://docs.maritaca.ai/")
    print("• Chave: https://chat.maritaca.ai/ (seção API)")
    print("\n🚀 Para usar o crawler: python3 app_maritaca_correto.py") 