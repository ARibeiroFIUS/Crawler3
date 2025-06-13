#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da Versão V4.1 Ultra-Precisa
==================================
Demonstra como eliminar falsos positivos
"""

from app_maritaca_v2 import (
    extrair_palavras_chave_simples, 
    buscar_palavras_chave_no_texto_rigoroso,
    eh_falso_positivo
)

def teste_ultra_precisao():
    """Testa a versão ultra-precisa"""
    
    print("🎯 TESTE: Versão V4.1 Ultra-Precisa")
    print("="*60)
    
    # Texto problemático que causava falsos positivos
    texto_pdf = """
    CONTRATO DE FORNECIMENTO
    
    Empresa contratada: Viapol Ltda
    CNPJ: 12.345.678/0001-90
    
    A empresa Viapol é responsável pelo fornecimento de materiais
    de construção para o projeto XYZ.
    
    Outras informações sobre EMS não se aplicam aqui.
    Via de regra, todos os contratos devem ser assinados.
    Pol não tem relação com este contrato.
    """
    
    # Casos de teste
    casos_teste = [
        ("Viapol Ltda", "Deveria ENCONTRAR"),
        ("EMS S.A.", "NÃO deveria encontrar (contexto irrelevante)"),
        ("Via Pol Materiais", "NÃO deveria encontrar (palavras separadas)"),
        ("QGC Engenharia", "NÃO deveria encontrar (não existe no texto)"),
        ("Materiais Ltda", "Poderia encontrar (palavra genérica presente)")
    ]
    
    print("RESULTADOS:")
    print("-" * 60)
    
    for nome_cliente, expectativa in casos_teste:
        # Extrair palavras-chave
        palavras_chave = extrair_palavras_chave_simples(nome_cliente)
        
        # Buscar no texto
        resultado = buscar_palavras_chave_no_texto_rigoroso(palavras_chave, texto_pdf, 95)
        
        # Status
        status = "✅ ENCONTRADO" if resultado['found'] else "❌ NÃO ENCONTRADO"
        
        print(f"\n{nome_cliente}")
        print(f"  Palavras-chave: {palavras_chave}")
        print(f"  {status} - Confiança: {resultado['confidence']}%")
        print(f"  Expectativa: {expectativa}")
        
        if resultado['found']:
            print(f"  Palavras encontradas: {resultado['palavras_encontradas']}")
            print(f"  Contexto: {resultado['context'][:80]}...")
        
        # Verificar se atendeu a expectativa
        deveria_encontrar = "Deveria ENCONTRAR" in expectativa
        encontrou = resultado['found']
        
        if deveria_encontrar == encontrou:
            print(f"  ✅ CORRETO!")
        else:
            print(f"  ❌ PROBLEMA: Expectativa não atendida!")

def teste_deteccao_falsos_positivos():
    """Testa a detecção específica de falsos positivos"""
    
    print("\n\n🛡️ TESTE: Detecção de Falsos Positivos")
    print("="*60)
    
    casos_contexto = [
        ("ems", "Outras informações sobre EMS não se aplicam aqui", True),
        ("ems", "A empresa EMS Ltda é responsável pelo projeto", False),
        ("via", "Via de regra, todos os contratos devem ser assinados", True),
        ("via", "Empresa Via Expressa Ltda", False),
        ("pol", "Pol não tem relação com este contrato", True),
        ("pol", "Empresa Pol Materiais Ltda", False)
    ]
    
    for palavra, contexto, deveria_ser_falso_positivo in casos_contexto:
        eh_falso = eh_falso_positivo(palavra, contexto.lower(), contexto.lower().find(palavra))
        
        status = "🛡️ FALSO POSITIVO DETECTADO" if eh_falso else "✅ LEGÍTIMO"
        expectativa = "Deveria detectar falso positivo" if deveria_ser_falso_positivo else "Deveria ser legítimo"
        
        print(f"\nPalavra: '{palavra}'")
        print(f"Contexto: '{contexto}'")
        print(f"{status}")
        print(f"Expectativa: {expectativa}")
        
        if eh_falso == deveria_ser_falso_positivo:
            print("✅ CORRETO!")
        else:
            print("❌ PROBLEMA!")

def comparacao_versoes():
    """Compara todas as versões"""
    
    print("\n\n⚖️ COMPARAÇÃO: V3.0 vs V4.0 vs V4.1")
    print("="*60)
    
    texto_teste = """
    Empresa: Viapol Ltda
    Outras informações sobre EMS não se aplicam.
    Via de regra, contratos são importantes.
    """
    
    casos = ["Viapol", "EMS S.A.", "Via Pol"]
    
    print("Cliente        | V3.0  | V4.0  | V4.1  | Ideal")
    print("-" * 50)
    
    for cliente in casos:
        # V3.0 (importar da versão antiga)
        try:
            from app import match_client_in_text
            resultado_v3 = match_client_in_text(cliente, texto_teste, 80)
            v3_status = "✅" if resultado_v3['found'] else "❌"
        except:
            v3_status = "?"
        
        # V4.0 (versão com palavras-chave básica)
        try:
            from app_maritaca import buscar_palavras_chave_no_texto, extrair_palavras_chave_simples as extract_v4
            palavras_v4 = extract_v4(cliente)
            resultado_v4 = buscar_palavras_chave_no_texto(palavras_v4, texto_teste, 85)
            v4_status = "✅" if resultado_v4['found'] else "❌"
        except:
            v4_status = "?"
        
        # V4.1 (versão ultra-precisa)
        palavras_v41 = extrair_palavras_chave_simples(cliente)
        resultado_v41 = buscar_palavras_chave_no_texto_rigoroso(palavras_v41, texto_teste, 95)
        v41_status = "✅" if resultado_v41['found'] else "❌"
        
        # Ideal (o que deveria acontecer)
        ideal = "✅" if cliente == "Viapol" else "❌"
        
        print(f"{cliente:<14} | {v3_status:<4} | {v4_status:<4} | {v41_status:<4} | {ideal}")

if __name__ == "__main__":
    print("🎯 TESTE COMPLETO - CRAWLER PDF V4.1 ULTRA-PRECISO")
    print("="*70)
    
    teste_ultra_precisao()
    teste_deteccao_falsos_positivos()
    comparacao_versoes()
    
    print("\n" + "="*70)
    print("📊 RESUMO:")
    print("• V4.1 elimina falsos positivos através de análise de contexto")
    print("• Usa regex com delimitadores de palavra (\\b)")
    print("• Detecta padrões específicos de falsos positivos")
    print("• Threshold mínimo de 90% para máxima precisão")
    print("• Ideal para casos onde precisão é mais importante que recall")
    print("\n🚀 Para usar a interface: python3 app_maritaca_v2.py") 