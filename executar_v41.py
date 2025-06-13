#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Executar Crawler PDF V4.1 - Ultra-Precisão
==========================================
Script simples para iniciar a interface web
"""

import os
import sys
import subprocess

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import pandas
        import PyPDF2
        import unidecode
        import rapidfuzz
        import flask
        import requests
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    
    dependencias = [
        "pandas",
        "PyPDF2", 
        "unidecode",
        "rapidfuzz",
        "flask",
        "requests",
        "openpyxl"
    ]
    
    for dep in dependencias:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")
            return False
    
    return True

def main():
    print("🎯 CRAWLER PDF V4.1 - ULTRA-PRECISÃO")
    print("="*50)
    print()
    
    # Verificar dependências
    if not verificar_dependencias():
        resposta = input("Deseja instalar as dependências automaticamente? (s/n): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            if not instalar_dependencias():
                print("❌ Erro na instalação. Execute manualmente:")
                print("pip install pandas PyPDF2 unidecode rapidfuzz flask requests openpyxl")
                return
        else:
            print("❌ Dependências necessárias não instaladas.")
            return
    
    print()
    print("🚀 Iniciando Crawler PDF V4.1...")
    print("📍 Acesse: http://localhost:5001")
    print()
    print("✨ CARACTERÍSTICAS DA V4.1:")
    print("• Elimina falsos positivos como 'EMS' em contextos irrelevantes")
    print("• Usa IA Maritaca (opcional) para extrair palavras-chave")
    print("• Algoritmo ultra-rigoroso com análise de contexto")
    print("• Threshold mínimo de 90% para máxima precisão")
    print()
    print("⚠️  Para parar o servidor: Ctrl+C")
    print("="*50)
    
    try:
        # Importar e executar
        from app_maritaca_v2 import app
        app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar: {e}")
        print("\nTente executar diretamente:")
        print("python3 app_maritaca_v2.py")

if __name__ == "__main__":
    main() 