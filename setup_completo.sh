#!/bin/bash

echo "🚀 SETUP COMPLETO - CRAWLER PDF ONLINE"
echo "======================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git não está instalado!${NC}"
    echo "📥 Instale o Git em: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${GREEN}✅ Git está instalado: $(git --version)${NC}"
echo ""

# Verificar configuração do Git
echo "🔧 CONFIGURANDO GIT..."
echo ""

# Pedir nome se não estiver configurado
if ! git config --global user.name > /dev/null 2>&1; then
    echo "📝 Precisamos configurar seu Git primeiro:"
    read -p "Digite seu nome completo: " user_name
    git config --global user.name "$user_name"
    echo -e "${GREEN}✅ Nome configurado: $user_name${NC}"
else
    current_name=$(git config --global user.name)
    echo -e "${GREEN}✅ Nome já configurado: $current_name${NC}"
fi

# Pedir email se não estiver configurado
if ! git config --global user.email > /dev/null 2>&1; then
    read -p "Digite seu email: " user_email
    git config --global user.email "$user_email"
    echo -e "${GREEN}✅ Email configurado: $user_email${NC}"
else
    current_email=$(git config --global user.email)
    echo -e "${GREEN}✅ Email já configurado: $current_email${NC}"
fi

echo ""

# Verificar se já é um repositório Git
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório Git..."
    git init
    echo -e "${GREEN}✅ Repositório Git criado!${NC}"
else
    echo -e "${GREEN}✅ Repositório Git já existe!${NC}"
fi

# Adicionar arquivos importantes
echo "📋 Adicionando arquivos ao Git..."
git add app.py requirements.txt Procfile runtime.txt DEPLOY_ONLINE.md

# Verificar se há mudanças para commitar
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️ Nenhuma mudança nova para commitar${NC}"
else
    git commit -m "Crawler PDF - Arquivos para deploy online"
    echo -e "${GREEN}✅ Commit realizado!${NC}"
fi

echo ""
echo "🌐 AGORA VAMOS COLOCAR ONLINE!"
echo "Escolha uma das opções abaixo:"
echo ""
echo -e "${BLUE}1. 🔵 Railway${NC} (Mais fácil - Recomendado)"
echo -e "${GREEN}2. 🟢 Heroku${NC} (Clássico)"
echo -e "${YELLOW}3. 🟠 Render${NC} (Gratuito)"
echo -e "${BLUE}4. 🟡 Vercel${NC} (Rápido)"
echo "5. 📋 Apenas preparar (sem deploy)"
echo "6. 📚 Ver instruções detalhadas"
echo ""

read -p "Digite sua escolha (1-6): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}🔵 RAILWAY DEPLOY:${NC}"
        echo ""
        echo "🔗 Primeiro, você precisa de uma conta GitHub (gratuita)"
        echo ""
        echo "❓ Você já tem conta no GitHub? (y/n)"
        read -p "> " has_github
        
        if [ "$has_github" = "y" ]; then
            echo ""
            echo "📝 Cole aqui a URL do seu repositório GitHub:"
            echo "   (exemplo: https://github.com/seuusuario/crawler-pdf.git)"
            read -p "> " repo_url
            
            if [ ! -z "$repo_url" ]; then
                echo "📤 Fazendo push para GitHub..."
                git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url
                git branch -M main
                git push -u origin main
                echo -e "${GREEN}✅ Push para GitHub concluído!${NC}"
                echo ""
                echo -e "${BLUE}🎯 PRÓXIMO PASSO:${NC}"
                echo "1. Acesse: https://railway.app"
                echo "2. Faça login com sua conta GitHub"
                echo "3. Clique 'Deploy from GitHub repo'"
                echo "4. Selecione seu repositório"
                echo "5. ✅ Deploy automático em 2-3 minutos!"
            else
                echo -e "${RED}❌ URL não fornecida${NC}"
            fi
        else
            echo ""
            echo "📋 PASSOS PARA CRIAR CONTA GITHUB:"
            echo "1. Acesse: https://github.com"
            echo "2. Clique 'Sign up'"
            echo "3. Crie sua conta (gratuita)"
            echo "4. Crie um novo repositório"
            echo "5. Execute este script novamente"
        fi
        ;;
    2)
        echo ""
        echo -e "${GREEN}🟢 HEROKU DEPLOY:${NC}"
        if command -v heroku &> /dev/null; then
            echo "📝 Digite o nome da sua app (ex: crawler-pdf-joao):"
            read -p "> " app_name
            
            if [ ! -z "$app_name" ]; then
                echo "🚀 Criando app no Heroku..."
                heroku create $app_name
                echo "📤 Fazendo deploy..."
                git push heroku main
                echo "🌐 Abrindo aplicação..."
                heroku open
                echo -e "${GREEN}✅ Deploy no Heroku concluído!${NC}"
            fi
        else
            echo -e "${RED}❌ Heroku CLI não encontrado.${NC}"
            echo "📥 Instale em: https://devcenter.heroku.com/articles/heroku-cli"
            echo "   Depois execute este script novamente"
        fi
        ;;
    3)
        echo ""
        echo -e "${YELLOW}🟠 RENDER DEPLOY:${NC}"
        echo ""
        echo "❓ Você já tem conta no GitHub? (y/n)"
        read -p "> " has_github
        
        if [ "$has_github" = "y" ]; then
            echo ""
            echo "📝 Cole a URL do seu repositório GitHub:"
            read -p "> " repo_url
            
            if [ ! -z "$repo_url" ]; then
                git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url
                git branch -M main
                git push -u origin main
                echo -e "${GREEN}✅ Push para GitHub concluído!${NC}"
                echo ""
                echo -e "${YELLOW}🎯 PRÓXIMO PASSO:${NC}"
                echo "1. Acesse: https://render.com"
                echo "2. Conecte sua conta GitHub"
                echo "3. Clique 'New Web Service'"
                echo "4. Selecione seu repositório"
                echo "5. Configurações:"
                echo "   - Build Command: pip install -r requirements.txt"
                echo "   - Start Command: gunicorn app:app"
                echo "   - Environment: Python 3"
                echo "6. ✅ Deploy!"
            fi
        else
            echo "Crie uma conta GitHub primeiro em: https://github.com"
        fi
        ;;
    4)
        echo ""
        echo -e "${BLUE}🟡 VERCEL DEPLOY:${NC}"
        
        # Criar vercel.json se não existir
        if [ ! -f "vercel.json" ]; then
            cat > vercel.json << 'EOF'
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
            git add vercel.json
            git commit -m "Adicionar configuração Vercel"
        fi
        
        if command -v vercel &> /dev/null; then
            echo "🚀 Fazendo deploy no Vercel..."
            vercel --prod
            echo -e "${GREEN}✅ Deploy no Vercel concluído!${NC}"
        else
            echo -e "${RED}❌ Vercel CLI não encontrado.${NC}"
            echo "📥 Instale com: npm i -g vercel"
            echo "🔗 Ou acesse: https://vercel.com e faça upload manual"
        fi
        ;;
    5)
        echo ""
        echo -e "${GREEN}📋 ARQUIVOS PREPARADOS:${NC}"
        echo "✅ app.py - Aplicação web"
        echo "✅ requirements.txt - Dependências"
        echo "✅ Procfile - Para Heroku"
        echo "✅ runtime.txt - Versão Python"
        echo "✅ Repositório Git inicializado"
        echo ""
        echo "📖 Leia DEPLOY_ONLINE.md para instruções detalhadas"
        ;;
    6)
        echo ""
        echo -e "${BLUE}📚 DOCUMENTAÇÃO:${NC}"
        echo "📄 Leia o arquivo: DEPLOY_ONLINE.md"
        echo "📂 Todos os arquivos estão prontos para deploy"
        echo ""
        if command -v open &> /dev/null; then
            echo "🔍 Abrindo documentação..."
            open DEPLOY_ONLINE.md
        fi
        ;;
    *)
        echo -e "${RED}❌ Opção inválida${NC}"
        ;;
esac

echo ""
echo -e "${BLUE}🎯 RESUMO:${NC}"
echo "✅ Git configurado"
echo "✅ Repositório criado"
echo "✅ Arquivos commitados"
echo "✅ Pronto para deploy online"
echo ""
echo -e "${YELLOW}💡 DICA:${NC} Use Railway para deploy mais fácil!"
echo "🔗 https://railway.app"
echo ""
echo -e "${GREEN}✨ Sua aplicação estará online em minutos!${NC}" 