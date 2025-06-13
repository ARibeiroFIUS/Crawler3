#!/bin/bash

echo "🚀 ENVIANDO CÓDIGO PARA GITHUB..."
echo "================================="

# Remover conexão anterior se existir
git remote remove origin 2>/dev/null

# Conectar ao GitHub
echo "📡 Conectando ao GitHub..."
git remote add origin https://github.com/ARibeiroFIUS/crawler-pdf-online.git

# Enviar código
echo "📤 Enviando arquivos..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCESSO! Código enviado para GitHub!"
    echo ""
    echo "🌐 PRÓXIMO PASSO - RENDER.COM:"
    echo "1. Acesse: https://render.com"
    echo "2. Login com GitHub (ARibeiroFIUS)"
    echo "3. New + → Web Service"
    echo "4. Conecte: crawler-pdf-online"
    echo "5. Configurações:"
    echo "   Name: crawler-pdf-andre"
    echo "   Build Command: pip install -r requirements.txt"
    echo "   Start Command: gunicorn app:app --host=0.0.0.0 --port=\$PORT"
    echo "6. Create Web Service"
    echo ""
    echo "🎯 SEU LINK: https://crawler-pdf-andre.onrender.com"
    echo ""
    echo "⏱️ Deploy leva ~3-5 minutos"
else
    echo ""
    echo "❌ ERRO! Verifique se criou o repositório no GitHub:"
    echo "🔗 https://github.com/new"
    echo "📝 Nome: crawler-pdf-online"
    echo "✅ Public"
fi 