#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para Criar Executável Desktop do Crawler
===============================================

Cria um executável que funciona como aplicação desktop,
abrindo automaticamente no navegador.
"""

import subprocess
import os
import shutil
import sys
from pathlib import Path

def main():
    print("🚀 CRIANDO EXECUTÁVEL DESKTOP DO CRAWLER PDF")
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
    
    print("\n📦 Criando executável desktop...")
    
    # Comando para criar executável
    comando = [
        "pyinstaller",
        "--onefile",                           # Arquivo único
        "--name", "CrawlerPDF_Desktop",       # Nome do executável
        "--hidden-import", "pandas",           # Dependências
        "--hidden-import", "openpyxl",
        "--hidden-import", "PyPDF2",
        "--hidden-import", "fuzzywuzzy",
        "--hidden-import", "Levenshtein",
        "--hidden-import", "flask",
        "--hidden-import", "werkzeug",
        "--hidden-import", "jinja2",
        "--add-data", "clientes.xlsx:.",       # Incluir arquivo exemplo
        "--add-data", "documento.pdf:.",       # Incluir arquivo exemplo
        "crawler_app_desktop.py"              # Arquivo principal
    ]
    
    print(f"Comando: {' '.join(comando)}")
    print("⏳ Aguarde, isso pode levar alguns minutos...")
    
    try:
        # Executar PyInstaller
        result = subprocess.run(comando, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ EXECUTÁVEL CRIADO COM SUCESSO!")
            
            # Verificar se foi criado
            exe_path = "dist/CrawlerPDF_Desktop"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 Tamanho: {size_mb:.1f} MB")
                print(f"📁 Localização: {os.path.abspath(exe_path)}")
                
                # Criar pasta final organizada
                final_folder = "CrawlerPDF_Desktop_App"
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
                instructions = """🚀 CRAWLER PDF - APLICAÇÃO DESKTOP
=====================================

📱 COMO USAR:

1️⃣ EXECUTAR A APLICAÇÃO:
   • Clique duas vezes em: CrawlerPDF_Desktop
   • A aplicação abrirá automaticamente no seu navegador
   • Uma janela moderna será exibida

2️⃣ USAR A INTERFACE:
   • 📊 Selecione o arquivo Excel com a lista de clientes
   • 📄 Selecione o arquivo PDF para buscar
   • 🎯 Ajuste a tolerância (80% recomendado)
   • 🚀 Clique em "PROCESSAR ARQUIVOS"

3️⃣ ACOMPANHAR O PROGRESSO:
   • Barra de progresso visual
   • Status em tempo real
   • Estatísticas detalhadas

4️⃣ BAIXAR RESULTADOS:
   • Arquivo Excel gerado automaticamente
   • Botão de download na interface
   • Resultados salvos com timestamp

💡 CARACTERÍSTICAS:

✅ Interface moderna e intuitiva
✅ Funciona como aplicação desktop
✅ Não precisa de Python instalado
✅ Abre automaticamente no navegador
✅ Progresso visual em tempo real
✅ Busca fuzzy com tolerância ajustável
✅ Resultados em Excel profissional
✅ Funciona offline (sem internet)

🔧 PRIMEIRO USO:

• Mac: Pode pedir permissão em "Preferências do Sistema > Segurança"
• Windows: Pode ser bloqueado pelo antivírus inicialmente
• Primeira execução pode ser mais lenta (normal)
• O navegador abrirá automaticamente em http://localhost:5000

📁 ARQUIVOS INCLUÍDOS:

• CrawlerPDF_Desktop - Aplicação principal
• clientes.xlsx - Arquivo exemplo para teste
• documento.pdf - Documento exemplo para teste
• COMO_USAR.txt - Este arquivo de instruções

🎯 RESULTADO:

A aplicação gera um arquivo Excel com:
• Lista completa de clientes
• Status: "Sim" ou "Não" para cada cliente
• Percentual de similaridade
• Tipo de correspondência (Exata/Fuzzy)

🆘 SUPORTE:

• Interface com mensagens claras
• Logs detalhados durante processamento
• Validação automática de arquivos
• Tratamento de erros amigável

🏆 VANTAGENS:

• Não precisa abrir terminal
• Interface gráfica profissional
• Funciona em Mac, Windows e Linux
• Processamento rápido e eficiente
• Resultados organizados e claros

Desenvolvido com ❤️ para maximizar sua produtividade!

Para fechar a aplicação, simplesmente feche a janela do navegador
e pressione Ctrl+C no terminal (se aparecer).
"""
                
                instructions_file = Path(final_folder) / "COMO_USAR.txt"
                instructions_file.write_text(instructions, encoding='utf-8')
                print(f"📋 Instruções criadas: COMO_USAR.txt")
                
                # Criar script de execução para Mac
                mac_script = f"""#!/bin/bash
echo "🚀 Iniciando Crawler PDF Desktop..."
echo "📱 Abrindo aplicação no navegador..."
cd "$(dirname "$0")"
./CrawlerPDF_Desktop
"""
                mac_script_file = Path(final_folder) / "Executar_CrawlerPDF.sh"
                mac_script_file.write_text(mac_script, encoding='utf-8')
                os.chmod(mac_script_file, 0o755)
                print(f"🍎 Script Mac criado: Executar_CrawlerPDF.sh")
                
                print(f"\n🎉 APLICAÇÃO DESKTOP PRONTA!")
                print(f"📁 Pasta final: {os.path.abspath(final_folder)}")
                print(f"🚀 Para usar: entre na pasta e execute 'CrawlerPDF_Desktop'")
                print(f"🍎 No Mac: também pode usar 'Executar_CrawlerPDF.sh'")
                
                # Listar conteúdo da pasta final
                print(f"\n📋 Conteúdo da pasta:")
                for item in os.listdir(final_folder):
                    item_path = os.path.join(final_folder, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path) / (1024 * 1024)
                        print(f"   📄 {item} ({size:.1f} MB)")
                
                print(f"\n💡 DICA: A aplicação abrirá automaticamente no navegador!")
                print(f"🌐 Endereço: http://localhost:5000")
                
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
    
    print(f"\n🏁 PROCESSO CONCLUÍDO!")
    print(f"💡 A aplicação desktop está pronta para ser usada!")
    print(f"🎯 Execute o arquivo e a interface abrirá automaticamente!")

if __name__ == "__main__":
    main() 