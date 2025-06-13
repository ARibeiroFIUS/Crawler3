#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script Simples para Criar Executável
===================================

Cria um executável da interface web do crawler.
"""

import subprocess
import sys
import os

def main():
    print("🚀 Criando executável do Crawler PDF...")
    print("=" * 50)
    
    # Comando simples para criar executável da interface web
    comando = [
        "pyinstaller",
        "--onefile",                      # Um arquivo único
        "--name", "CrawlerPDF",          # Nome do executável
        "--hidden-import", "pandas",      # Importações necessárias
        "--hidden-import", "openpyxl",
        "--hidden-import", "PyPDF2", 
        "--hidden-import", "fuzzywuzzy",
        "--hidden-import", "Levenshtein",
        "--hidden-import", "flask",
        "--hidden-import", "werkzeug",
        "--hidden-import", "jinja2",
        "executar_interface_web.py"       # Arquivo principal
    ]
    
    print(f"📦 Executando: {' '.join(comando)}")
    print("⏳ Isso pode levar alguns minutos...")
    
    try:
        # Executar o comando
        result = subprocess.run(comando, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executável criado com sucesso!")
            print("📁 Localização: dist/CrawlerPDF")
            
            # Verificar se o arquivo foi criado
            if os.path.exists("dist/CrawlerPDF"):
                size = os.path.getsize("dist/CrawlerPDF") / (1024 * 1024)
                print(f"📊 Tamanho: {size:.1f} MB")
                print("\n🎉 PRONTO! Seu executável está pronto para uso.")
                print("💡 Para usar: execute o arquivo 'CrawlerPDF' na pasta 'dist'")
                print("🌐 Ele abrirá a interface web em http://localhost:5000")
            else:
                print("⚠️ Executável criado mas não encontrado no local esperado")
                
        else:
            print("❌ Erro ao criar executável:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 