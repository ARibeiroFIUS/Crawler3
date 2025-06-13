#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para Criar Executáveis do Crawler
=======================================

Este script usa PyInstaller para criar executáveis stand-alone
do crawler que podem ser executados sem Python instalado.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_section(title):
    """Imprime uma seção formatada."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def run_command(command, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n📦 {description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Sucesso!")
            return True
        else:
            print("❌ Erro:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def create_web_executable():
    """Cria executável para a interface web."""
    print_section("CRIANDO EXECUTÁVEL - INTERFACE WEB")
    
    # Comando para criar executável da interface web
    command = """
    pyinstaller --onefile --windowed --name CrawlerPDF_Web \
    --add-data "templates:templates" \
    --hidden-import flask \
    --hidden-import werkzeug \
    --hidden-import jinja2 \
    --hidden-import pandas \
    --hidden-import openpyxl \
    --hidden-import PyPDF2 \
    --hidden-import fuzzywuzzy \
    --hidden-import Levenshtein \
    executar_interface_web.py
    """
    
    return run_command(command.replace('\n', ' ').strip(), "Criando executável da Interface Web")

def create_desktop_executable():
    """Cria executável para a interface desktop."""
    print_section("CRIANDO EXECUTÁVEL - INTERFACE DESKTOP")
    
    # Comando para criar executável da interface desktop
    command = """
    pyinstaller --onefile --windowed --name CrawlerPDF_Desktop \
    --hidden-import tkinter \
    --hidden-import pandas \
    --hidden-import openpyxl \
    --hidden-import PyPDF2 \
    --hidden-import fuzzywuzzy \
    --hidden-import Levenshtein \
    executar_interface.py
    """
    
    return run_command(command.replace('\n', ' ').strip(), "Criando executável da Interface Desktop")

def create_console_executable():
    """Cria executável para linha de comando."""
    print_section("CRIANDO EXECUTÁVEL - LINHA DE COMANDO")
    
    # Comando para criar executável de linha de comando
    command = """
    pyinstaller --onefile --name CrawlerPDF_Console \
    --hidden-import pandas \
    --hidden-import openpyxl \
    --hidden-import PyPDF2 \
    --hidden-import fuzzywuzzy \
    --hidden-import Levenshtein \
    crawler_advanced.py
    """
    
    return run_command(command.replace('\n', ' ').strip(), "Criando executável de Linha de Comando")

def organize_executables():
    """Organiza os executáveis criados."""
    print_section("ORGANIZANDO EXECUTÁVEIS")
    
    # Criar pasta de distribuição
    dist_folder = Path("dist_executaveis")
    if dist_folder.exists():
        shutil.rmtree(dist_folder)
    dist_folder.mkdir()
    
    # Mover executáveis
    dist_path = Path("dist")
    if dist_path.exists():
        for exe_file in dist_path.glob("*"):
            if exe_file.is_file():
                destination = dist_folder / exe_file.name
                shutil.move(str(exe_file), str(destination))
                print(f"✅ Movido: {exe_file.name} -> {destination}")
    
    # Criar README para os executáveis
    readme_content = """
# 🚀 EXECUTÁVEIS DO CRAWLER DE CLIENTES EM PDF

## 📁 Arquivos Incluídos:

### 🌐 CrawlerPDF_Web
- **Descrição:** Interface web moderna
- **Como usar:** Execute o arquivo e acesse http://localhost:5000
- **Vantagens:** Funciona em qualquer sistema, interface intuitiva

### 🖥️ CrawlerPDF_Desktop
- **Descrição:** Interface gráfica nativa
- **Como usar:** Execute o arquivo diretamente
- **Vantagens:** Aplicação desktop nativa, não precisa de navegador

### ⌨️ CrawlerPDF_Console
- **Descrição:** Versão linha de comando
- **Como usar:** Execute via terminal com argumentos
- **Exemplo:** `./CrawlerPDF_Console arquivo.xlsx documento.pdf -t 80`
- **Vantagens:** Ideal para automação e scripts

## 💡 DICAS DE USO:

1. **Primeira execução pode ser lenta** (sistema extraindo arquivos)
2. **Windows:** Pode ser necessário permitir execução no antivírus
3. **Mac:** Pode ser necessário permitir em "Preferências > Segurança"
4. **Linux:** Tornar executável com `chmod +x nome_do_arquivo`

## 📊 REQUISITOS:
- Nenhum! Os executáveis incluem tudo que é necessário
- Tamanho: ~100-200MB cada (incluem Python e dependências)

## 🆘 PROBLEMAS COMUNS:
- **Antivírus bloqueia:** Adicionar à lista de exceções
- **Execução lenta:** Normal na primeira execução
- **Erro de permissão:** Executar como administrador

Desenvolvido com ❤️ para maximizar sua produtividade!
"""
    
    readme_file = dist_folder / "LEIA-ME.txt"
    readme_file.write_text(readme_content, encoding='utf-8')
    print(f"✅ README criado: {readme_file}")
    
    return dist_folder

def cleanup():
    """Remove arquivos temporários."""
    print_section("LIMPEZA")
    
    folders_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Removido: {folder}")
    
    # Remover arquivos .spec
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🗑️ Removido: {spec_file}")

def main():
    """Função principal."""
    print_section("GERADOR DE EXECUTÁVEIS - CRAWLER PDF")
    print("Este script criará executáveis standalone do crawler.")
    print("Os executáveis podem ser executados sem Python instalado!")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        if not run_command("pip install pyinstaller", "Instalando PyInstaller"):
            print("❌ Falha ao instalar PyInstaller")
            return
    
    success_count = 0
    total_count = 3
    
    # Criar executáveis
    if create_web_executable():
        success_count += 1
    
    if create_desktop_executable():
        success_count += 1
    
    if create_console_executable():
        success_count += 1
    
    # Organizar resultados
    if success_count > 0:
        dist_folder = organize_executables()
        
        print_section("RESULTADO FINAL")
        print(f"✅ {success_count}/{total_count} executáveis criados com sucesso!")
        print(f"📁 Executáveis salvos em: {dist_folder.absolute()}")
        
        # Listar arquivos criados
        print("\n📋 Arquivos criados:")
        for file in dist_folder.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   📄 {file.name} ({size_mb:.1f} MB)")
        
        print(f"\n🎉 PRONTO! Você agora tem executáveis standalone do crawler!")
        print(f"💡 Estes arquivos podem ser executados em qualquer computador")
        print(f"   sem precisar instalar Python ou dependências.")
        
    else:
        print("❌ Nenhum executável foi criado com sucesso.")
    
    # Limpeza
    cleanup()
    
    print(f"\n{'='*60}")
    print("🏁 PROCESSO CONCLUÍDO")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 