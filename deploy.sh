#!/bin/bash

echo "🚀 DEPLOY CRAWLER PDF ONLINE"
echo "=========================="

# Verificar se git está inicializado
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Crawler PDF - Deploy inicial"
fi

echo ""
echo "🌐 ESCOLHA UMA OPÇÃO DE DEPLOY:"
echo ""
echo "1. 🔵 Railway (Recomendado - Mais fácil)"
echo "2. 🟢 Heroku (Clássico)"
echo "3. 🟠 Render (Gratuito)"
echo "4. 🟡 Vercel (Rápido)"
echo "5. 📋 Apenas preparar arquivos"
echo ""

read -p "Digite sua escolha (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔵 RAILWAY DEPLOY:"
        echo "1. Acesse: https://railway.app"
        echo "2. Conecte sua conta GitHub"
        echo "3. Clique 'Deploy from GitHub repo'"
        echo "4. Selecione este repositório"
        echo "5. ✅ Deploy automático!"
        echo ""
        echo "📋 Quer fazer push para GitHub primeiro? (y/n)"
        read -p "> " github
        if [ "$github" = "y" ]; then
            read -p "📝 URL do seu repositório GitHub: " repo_url
            git remote add origin $repo_url
            git branch -M main
            git push -u origin main
            echo "✅ Push para GitHub concluído!"
            echo "🔗 Agora acesse Railway: https://railway.app"
        fi
        ;;
    2)
        echo ""
        echo "🟢 HEROKU DEPLOY:"
        if command -v heroku &> /dev/null; then
            read -p "📝 Nome da sua app (ex: crawler-pdf-joao): " app_name
            heroku create $app_name
            git push heroku main
            heroku open
            echo "✅ Deploy no Heroku concluído!"
        else
            echo "❌ Heroku CLI não encontrado."
            echo "📥 Instale em: https://devcenter.heroku.com/articles/heroku-cli"
        fi
        ;;
    3)
        echo ""
        echo "🟠 RENDER DEPLOY:"
        echo "1. Acesse: https://render.com"
        echo "2. Conecte GitHub"
        echo "3. 'New Web Service'"
        echo "4. Selecione repositório"
        echo "5. Configurações:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn app:app"
        echo "   - Environment: Python 3"
        echo ""
        echo "📋 Fazer push para GitHub? (y/n)"
        read -p "> " github
        if [ "$github" = "y" ]; then
            read -p "📝 URL do seu repositório GitHub: " repo_url
            git remote add origin $repo_url
            git branch -M main
            git push -u origin main
            echo "✅ Push para GitHub concluído!"
        fi
        ;;
    4)
        echo ""
        echo "🟡 VERCEL DEPLOY:"
        # Criar vercel.json
        cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
EOF
        echo "📄 vercel.json criado"
        
        if command -v vercel &> /dev/null; then
            vercel
            echo "✅ Deploy no Vercel concluído!"
        else
            echo "❌ Vercel CLI não encontrado."
            echo "📥 Instale com: npm i -g vercel"
            echo "🔗 Ou acesse: https://vercel.com"
        fi
        ;;
    5)
        echo ""
        echo "📋 ARQUIVOS PREPARADOS:"
        echo "✅ app.py - Aplicação web"
        echo "✅ requirements.txt - Dependências"
        echo "✅ Procfile - Para Heroku"
        echo "✅ runtime.txt - Versão Python"
        echo ""
        echo "📖 Leia DEPLOY_ONLINE.md para instruções detalhadas"
        ;;
    *)
        echo "❌ Opção inválida"
        ;;
esac

echo ""
echo "📚 DOCUMENTAÇÃO COMPLETA:"
echo "📄 Leia: DEPLOY_ONLINE.md"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Escolha uma plataforma"
echo "2. Siga as instruções"
echo "3. Teste com seus arquivos"
echo "4. Compartilhe a URL!"
echo ""
echo "✨ Sua aplicação estará online em minutos!" 