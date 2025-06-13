#!/bin/bash

# Script para executar a interface gráfica do Crawler de Clientes em PDF
# Para macOS e Linux

echo "🚀 Iniciando Crawler de Clientes em PDF - Interface Gráfica"
echo "=" * 50

# Verificar se estamos no diretório correto
if [ ! -f "crawler_ui.py" ]; then
    echo "❌ Erro: crawler_ui.py não encontrado"
    echo "💡 Execute este script na pasta do projeto"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado - usando Python do sistema"
fi

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    echo "💡 Instale o Python 3.6 ou superior"
    exit 1
fi

echo "📦 Verificando dependências..."

# Verificar se as dependências estão instaladas
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter não encontrado"
    echo "💡 Instale o tkinter: sudo apt-get install python3-tk (Ubuntu/Debian)"
    exit 1
fi

python3 -c "import pandas, PyPDF2, fuzzywuzzy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Algumas dependências não encontradas"
    echo "📦 Instalando dependências..."
    pip3 install -r requirements.txt
fi

echo "🚀 Iniciando interface gráfica..."
python3 executar_interface.py

echo "✅ Interface encerrada." 