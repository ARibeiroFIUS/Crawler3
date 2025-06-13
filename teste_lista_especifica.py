#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste com Lista Específica de Empresas
=====================================
Testa a extração de palavras-chave com a lista fornecida pelo usuário
"""

import os
import sys
from typing import List
from pydantic import BaseModel

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PalavrasChave(BaseModel):
    """Modelo Pydantic para saídas estruturadas da Maritaca"""
    palavras_significativas: List[str]
    justificativa: str

def testar_extracao_maritaca_nova(api_key, nome_cliente):
    """Testa a extração com o prompt CORRIGIDO"""
    
    if not api_key:
        return None
    
    try:
        import openai
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        
        prompt = f"""
Analise o nome da empresa "{nome_cliente}" e extraia APENAS 1 palavra mais significativa e única que melhor identifica esta empresa.

PRIORIDADE ABSOLUTA (nesta ordem):
1. SIGLAS de 2-4 letras (EMS, QGC, ABC, XYZ) - SEMPRE priorize siglas
2. NOMES ÚNICOS distintivos (Viapol, Petrobras, Ambev)
3. PALAVRAS ESPECÍFICAS não-genéricas

REGRAS RIGOROSAS:
- Ignore completamente: S.A., LTDA, EIRELI, ME, CIA, INC, CORP, DO, DA, DE, E, EM, COM, PARA, POR, BRASIL, INDÚSTRIA, MATERIAIS, PRODUTOS, SERVIÇOS, ENGENHARIA, CONSTRUTORA, TRANSPORTADORA
- Se houver sigla, escolha APENAS a sigla
- Se não houver sigla, escolha o nome mais distintivo
- MÁXIMO 1 palavra (exceto casos muito específicos)
- Evite palavras genéricas

EXEMPLOS CORRETOS:
- "EMS S.A." → ["EMS"]
- "Viapol Ltda" → ["Viapol"]  
- "QGC Engenharia" → ["QGC"]
- "Transportadora XYZ Logística" → ["XYZ"]
- "Construtora ABC Materiais" → ["ABC"]
- "Sun Ace Brasil Indústria" → ["Sun"] (primeira palavra distintiva)
- "Metalúrgica Silva & Cia" → ["Silva"]

Retorne APENAS a palavra mais importante e única para identificar esta empresa.
"""

        completion = client.beta.chat.completions.parse(
            model="sabia-3",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de nomes de empresas. Extraia APENAS a palavra-chave mais significativa."},
                {"role": "user", "content": prompt}
            ],
            response_format=PalavrasChave,
            max_tokens=150,
            temperature=0.1
        )
        
        resultado = completion.choices[0].message.parsed
        
        if resultado and resultado.palavras_significativas:
            return {
                'palavras': resultado.palavras_significativas,
                'justificativa': resultado.justificativa,
                'sucesso': True
            }
        else:
            return {
                'palavras': [],
                'justificativa': 'Resposta vazia da API',
                'sucesso': False
            }
            
    except Exception as e:
        return {
            'palavras': [],
            'justificativa': f'Erro na API: {str(e)}',
            'sucesso': False
        }

def main():
    """Função principal de teste"""
    
    print("=" * 80)
    print("🧪 TESTE COM LISTA ESPECÍFICA DE EMPRESAS")
    print("=" * 80)
    
    # Lista fornecida pelo usuário
    empresas_teste = [
        "Mauad Franqueadora Ltda.",
        "Transportes Ltda.",
        "Máquinas Furtani Ltda.",
        "Galeria Química e Farmacêutica Ltda.",
        "Farmabase Saúde Animal Ltda.",
        "Braswell Papel e Celulose Ltda.",
        "Clean Field Comércio de Produtos Alimentícios Ltda.",
        "José Pupin Agropecuária",
        "LongPing High - Tech Biotecnologia Ltda."
    ]
    
    # Solicitar chave da API
    api_key = input("Digite sua chave da API Maritaca: ").strip()
    
    if not api_key:
        print("❌ Chave da API necessária para este teste")
        return
    
    print(f"\n🔍 Testando {len(empresas_teste)} empresas...")
    print("=" * 80)
    
    resultados_corretos = 0
    total_empresas = len(empresas_teste)
    
    for i, empresa in enumerate(empresas_teste, 1):
        print(f"\n{i:2d}. EMPRESA: {empresa}")
        print("    " + "─" * 70)
        
        # Testar com IA
        resultado = testar_extracao_maritaca_nova(api_key, empresa)
        
        if resultado and resultado['sucesso']:
            palavras = resultado['palavras']
            justificativa = resultado['justificativa']
            
            print(f"    🤖 MARITACA EXTRAIU: {palavras}")
            print(f"    💭 JUSTIFICATIVA: {justificativa[:100]}...")
            
                         # Sugestões CORRETAS baseadas nos exemplos do usuário
             sugestoes = {
                 "Mauad Franqueadora Ltda.": "Mauad",
                 "Transportes Ltda.": "Vipex",  # Assumindo que é "Vipex Transportes"
                 "Máquinas Furtani Ltda.": "Furtan",
                 "Galeria Química e Farmacêutica Ltda.": "Galena",
                 "Farmabase Saúde Animal Ltda.": "Farmabase",
                 "Braswell Papel e Celulose Ltda.": "Braswell",
                 "Clean Field Comércio de Produtos Alimentícios Ltda.": "Clean Field",
                 "José Pupin Agropecuária": "Pupin",
                 "LongPing High - Tech Biotecnologia Ltda.": "LongPing"
             }
            
            sugestao = sugestoes.get(empresa, "?")
            print(f"    💡 SUGESTÃO IDEAL: [{sugestao}]")
            
            # Verificar se está correto
            palavra_extraida = palavras[0].lower() if palavras else ""
            if palavra_extraida == sugestao.lower():
                print(f"    ✅ PERFEITO!")
                resultados_corretos += 1
            else:
                print(f"    ⚠️  DIFERENTE - Você concorda com a IA ou prefere a sugestão?")
                resposta = input("    Digite 1 para IA, 2 para sugestão, Enter para IA: ").strip()
                if resposta == "2":
                    print(f"    📝 ANOTADO: Prefere [{sugestao}]")
                else:
                    print(f"    👍 IA aprovada: [{palavra_extraida}]")
                    resultados_corretos += 1
        else:
            print(f"    ❌ ERRO: {resultado['justificativa'] if resultado else 'Falha na API'}")
        
        print()
    
    print("=" * 80)
    print("📊 RESUMO DOS RESULTADOS")
    print("=" * 80)
    
    taxa_acerto = (resultados_corretos / total_empresas) * 100
    print(f"✅ Resultados corretos: {resultados_corretos}/{total_empresas} ({taxa_acerto:.1f}%)")
    
    if taxa_acerto >= 80:
        print("🎉 EXCELENTE! A IA está funcionando bem")
    elif taxa_acerto >= 60:
        print("⚠️  RAZOÁVEL - Precisa de alguns ajustes")
    else:
        print("❌ PROBLEMÁTICO - Prompt precisa ser reformulado")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    if taxa_acerto < 80:
        print("1. Ajustar o prompt da IA com base nos erros identificados")
        print("2. Adicionar mais exemplos específicos")
        print("3. Refinar as regras de priorização")
    else:
        print("1. Aplicar as correções no sistema principal")
        print("2. Fazer deploy da versão corrigida")
        print("3. Testar com dados reais")

if __name__ == "__main__":
    main() 