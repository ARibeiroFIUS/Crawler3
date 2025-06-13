#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script Final para Criar Executável do Crawler
=============================================

Este script cria um executável funcional do crawler.
"""

import subprocess
import os
import shutil
import sys
from pathlib import Path

def main():
    print("🚀 CRIANDO EXECUTÁVEL FINAL DO CRAWLER PDF")
    print("=" * 60)
    
    # Limpar builds anteriores
    folders_to_clean = ["build", "dist", "__pycache__"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Removido: {folder}")
    
    # Remover arquivos .spec
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🗑️ Removido: {spec_file}")
    
    print("\n📦 Criando executável...")
    
    # Comando para criar executável
    comando = [
        "pyinstaller",
        "--onefile",                           # Arquivo único
        "--windowed",                          # Sem console (para interface gráfica)
        "--name", "CrawlerPDF_Final",         # Nome do executável
        "--hidden-import", "pandas",           # Dependências
        "--hidden-import", "openpyxl",
        "--hidden-import", "PyPDF2",
        "--hidden-import", "fuzzywuzzy",
        "--hidden-import", "Levenshtein",
        "--hidden-import", "tkinter",
        "--add-data", "clientes.xlsx:.",       # Incluir arquivo exemplo
        "--add-data", "documento.pdf:.",       # Incluir arquivo exemplo
        "crawler_executavel.py"                # Arquivo principal
    ]
    
    print(f"Comando: {' '.join(comando)}")
    print("⏳ Aguarde, isso pode levar alguns minutos...")
    
    try:
        # Executar PyInstaller
        result = subprocess.run(comando, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ EXECUTÁVEL CRIADO COM SUCESSO!")
            
            # Verificar se foi criado
            exe_path = "dist/CrawlerPDF_Final"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 Tamanho: {size_mb:.1f} MB")
                print(f"📁 Localização: {os.path.abspath(exe_path)}")
                
                # Criar pasta final organizada
                final_folder = "CrawlerPDF_Executavel"
                if os.path.exists(final_folder):
                    shutil.rmtree(final_folder)
                os.makedirs(final_folder)
                
                # Copiar executável
                shutil.copy2(exe_path, final_folder)
                print(f"✅ Executável copiado para: {final_folder}/")
                
                # Criar arquivos exemplo
                example_files = ["clientes.xlsx", "documento.pdf"]
                for file in example_files:
                    if os.path.exists(file):
                        shutil.copy2(file, final_folder)
                        print(f"📄 Arquivo exemplo copiado: {file}")
                
                # Criar instruções
                instructions = """🚀 CRAWLER DE CLIENTES EM PDF
================================

📋 COMO USAR:

1️⃣ INTERFACE GRÁFICA (Recomendado):
   • Execute: CrawlerPDF_Final (clique duplo)
   • Uma janela será aberta
   • Selecione arquivo Excel e PDF
   • Configure tolerância (80% recomendado)
   • Clique "PROCESSAR ARQUIVOS"

2️⃣ LINHA DE COMANDO:
   • Terminal/CMD: ./CrawlerPDF_Final arquivo.xlsx documento.pdf
   • Exemplo: ./CrawlerPDF_Final clientes.xlsx documento.pdf

📁 ARQUIVOS INCLUÍDOS:
   • CrawlerPDF_Final - Executável principal
   • clientes.xlsx - Arquivo exemplo
   • documento.pdf - Documento exemplo

💡 CARACTERÍSTICAS:
   ✅ Não precisa de Python instalado
   ✅ Interface gráfica amigável
   ✅ Suporte a linha de comando
   ✅ Busca fuzzy com 80% tolerância
   ✅ Resultados salvos em Excel
   ✅ Funciona offline

🔧 PRIMEIRO USO:
   • Primeira execução pode ser lenta (normal)
   • Mac: Pode pedir permissão em Preferências > Segurança
   • Windows: Pode ser bloqueado pelo antivírus

📞 SUPORTE:
   • Interface intuitiva com logs detalhados
   • Mensagens de erro claras
   • Progresso visual do processamento

🎯 RESULTADO:
   • Arquivo Excel com lista de clientes
   • Coluna "encontrado": Sim/Não
   • Coluna "similaridade": Percentual
   • Salvo automaticamente com timestamp

Desenvolvido com ❤️ para sua produtividade!"""
                
                instructions_file = Path(final_folder) / "COMO_USAR.txt"
                instructions_file.write_text(instructions, encoding='utf-8')
                print(f"📋 Instruções criadas: COMO_USAR.txt")
                
                print(f"\n🎉 EXECUTÁVEL PRONTO!")
                print(f"📁 Pasta final: {os.path.abspath(final_folder)}")
                print(f"🚀 Para usar: entre na pasta e execute 'CrawlerPDF_Final'")
                
                # Listar conteúdo da pasta final
                print(f"\n📋 Conteúdo da pasta:")
                for item in os.listdir(final_folder):
                    item_path = os.path.join(final_folder, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path) / (1024 * 1024)
                        print(f"   📄 {item} ({size:.1f} MB)")
                
            else:
                print("❌ Executável não foi encontrado após criação")
                
        else:
            print("❌ ERRO ao criar executável:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
    
    # Limpeza final
    print(f"\n🧹 Limpeza final...")
    cleanup_folders = ["build", "__pycache__"]
    for folder in cleanup_folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Removido: {folder}")
    
    # Manter apenas pasta dist original e a final
    print(f"\n🏁 PROCESSO CONCLUÍDO!")
    print(f"💡 O executável está pronto para ser usado em qualquer computador!")

if __name__ == "__main__":
    main() 