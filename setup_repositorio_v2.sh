#!/bin/bash

echo "🚀 SETUP CRAWLER PDF V2.0"
echo "=========================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📦 Criando repositório para Versão 2.0...${NC}"
echo ""

# 1. Criar nova pasta para V2
mkdir -p "crawler-pdf-v2"
cd "crawler-pdf-v2"

echo -e "${GREEN}✅ Pasta criada: crawler-pdf-v2${NC}"

# 2. Copiar arquivos V2
cp "../app_v2.py" "app.py"
cp "../template_v2.html" "."
cp "../requirements_v2.txt" "requirements.txt"
cp "../README_V2.md" "README.md"

# 3. Criar arquivos de deploy
cat > Procfile << 'EOF'
web: gunicorn app:app
EOF

cat > runtime.txt << 'EOF'
python-3.11.9
EOF

cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
venv/
.env
.DS_Store
*.log
temp/
cache/
EOF

echo -e "${GREEN}✅ Arquivos V2.0 preparados${NC}"

# 4. Inicializar Git
git init
git add .
git commit -m "🚀 Crawler PDF V2.0 - Sistema Avançado com IA para QGC

✨ Novidades:
- 🤖 Detecção automática de documentos (QGC, Editais)
- ⚡ Cache inteligente (10x mais rápido)
- 📊 Extração de valores e CNPJs
- 🎯 Algoritmos otimizados (menos falsos positivos)
- 📈 Interface moderna com estatísticas em tempo real
- 💾 Relatórios avançados com múltiplas abas

🎯 Especializado para Quadro Geral de Credores"

echo -e "${GREEN}✅ Repositório Git inicializado${NC}"
echo ""

echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1️⃣ ${BLUE}Criar repositório no GitHub:${NC}"
echo "   - Acesse: https://github.com/new"
echo "   - Nome: crawler-pdf-v2"
echo "   - Público ✅"
echo "   - Create repository"
echo ""

echo "2️⃣ ${BLUE}Conectar e fazer push:${NC}"
echo "   git remote add origin https://github.com/ARibeiroFIUS/crawler-pdf-v2.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "3️⃣ ${BLUE}Deploy no Render:${NC}"
echo "   - Acesse: https://render.com"
echo "   - New Web Service"
echo "   - Conecte: crawler-pdf-v2"
echo "   - Deploy automático!"
echo ""

echo -e "${GREEN}🎉 Versão 2.0 pronta para deploy!${NC}"
echo ""
echo -e "${BLUE}📁 Arquivos criados:${NC}"
ls -la

echo ""
echo -e "${YELLOW}💡 Para testar localmente:${NC}"
echo "   cd crawler-pdf-v2"
echo "   pip install -r requirements.txt"
echo "   python app.py"
echo ""

echo -e "${GREEN}✨ Sua aplicação V2.0 estará em: http://localhost:5000${NC}" 