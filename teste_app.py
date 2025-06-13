#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da Aplicação Desktop
==========================

Script para testar se a aplicação está funcionando corretamente.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar e testar a aplicação
try:
    from crawler_app_desktop import main
    print("✅ Módulo importado com sucesso!")
    
    print("🚀 Iniciando teste da aplicação...")
    main()
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro na aplicação: {e}")
    import traceback
    traceback.print_exc() 