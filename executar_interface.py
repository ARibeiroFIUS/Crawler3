#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar a interface gráfica do Crawler
==================================================

Execute este arquivo para abrir a interface gráfica do crawler.
"""

import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from crawler_ui import main
    
    if __name__ == "__main__":
        print("🚀 Iniciando interface gráfica do Crawler de Clientes em PDF...")
        print("📋 Aguarde a janela abrir...")
        main()
        
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Certifique-se de que todas as dependências estão instaladas:")
    print("   pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Erro ao executar a interface: {e}")
    print("💡 Verifique se o Python e tkinter estão instalados corretamente.") 