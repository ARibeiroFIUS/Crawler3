#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar a Interface Web do Crawler
==================================================

Execute este arquivo para abrir a interface web do crawler.
"""

import sys
import os
import webbrowser
import time
import threading

def open_browser():
    """Abre o navegador após 2 segundos."""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == "__main__":
    print("🚀 Iniciando Interface Web do Crawler de Clientes em PDF...")
    print("=" * 60)
    print("📱 A interface web será aberta em: http://localhost:5000")
    print("🌐 Compatível com qualquer navegador web")
    print("🛑 Para parar o servidor: Ctrl+C")
    print("=" * 60)
    
    # Abrir navegador automaticamente
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Importar e executar a aplicação web
        from app_web import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Certifique-se de que todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Erro ao executar a interface: {e}")
        print("💡 Verifique se o Python e Flask estão instalados corretamente.") 