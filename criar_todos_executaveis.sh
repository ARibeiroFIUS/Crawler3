#!/bin/bash

echo "🚀 CRIANDO TODOS OS EXECUTÁVEIS DO CRAWLER PDF"
echo "=" * 60

# Criar executável da interface web
echo "📦 1/3 - Criando executável da Interface Web..."
pyinstaller --onefile --name "CrawlerPDF_Web" \
  --hidden-import pandas \
  --hidden-import openpyxl \
  --hidden-import PyPDF2 \
  --hidden-import fuzzywuzzy \
  --hidden-import Levenshtein \
  --hidden-import flask \
  --hidden-import werkzeug \
  --hidden-import jinja2 \
  executar_interface_web.py

echo "✅ Interface Web criada!"

# Criar executável da linha de comando
echo "📦 2/3 - Criando executável de Linha de Comando..."
pyinstaller --onefile --name "CrawlerPDF_Console" \
  --hidden-import pandas \
  --hidden-import openpyxl \
  --hidden-import PyPDF2 \
  --hidden-import fuzzywuzzy \
  --hidden-import Levenshtein \
  crawler_advanced.py

echo "✅ Linha de Comando criada!"

# Criar executável simplificado
echo "📦 3/3 - Criando executável Simplificado..."
pyinstaller --onefile --name "CrawlerPDF_Simples" \
  --hidden-import pandas \
  --hidden-import openpyxl \
  --hidden-import PyPDF2 \
  --hidden-import fuzzywuzzy \
  --hidden-import Levenshtein \
  crawler.py

echo "✅ Simplificado criado!"

# Organizar executáveis
echo "📁 Organizando executáveis..."
mkdir -p executaveis_prontos
cp dist/* executaveis_prontos/ 2>/dev/null || true

# Criar documentação
cat > executaveis_prontos/COMO_USAR.txt << 'EOF'
🚀 EXECUTÁVEIS DO CRAWLER DE CLIENTES EM PDF
==========================================

📁 ARQUIVOS INCLUÍDOS:

🌐 CrawlerPDF_Web
   • Interface web moderna no navegador
   • Execute e acesse: http://localhost:5000
   • Mais fácil de usar - recomendado para iniciantes

⌨️ CrawlerPDF_Console  
   • Versão linha de comando
   • Uso: ./CrawlerPDF_Console arquivo.xlsx documento.pdf -t 80
   • Ideal para automação e scripts

📊 CrawlerPDF_Simples
   • Versão básica simplificada
   • Uso: ./CrawlerPDF_Simples
   • Para uso rápido com arquivos padrão

🔧 COMO USAR:

1. INTERFACE WEB (Recomendado):
   - Execute: ./CrawlerPDF_Web
   - Acesse: http://localhost:5000 no navegador
   - Selecione seus arquivos Excel e PDF
   - Configure tolerância (80% recomendado)
   - Clique "INICIAR PROCESSAMENTO"

2. LINHA DE COMANDO:
   - Execute: ./CrawlerPDF_Console arquivo.xlsx documento.pdf
   - Adicione -t 80 para tolerância de 80%
   - Adicione -o resultado.xlsx para arquivo específico

3. VERSÃO SIMPLES:
   - Coloque clientes.xlsx e documento.pdf na pasta
   - Execute: ./CrawlerPDF_Simples
   - Resultados em output/

💡 DICAS:
• Primeira execução pode ser lenta (normal)
• Mac: Pode pedir permissão em Preferências > Segurança
• Windows: Pode ser bloqueado pelo antivírus inicialmente
• Tamanho: ~35MB cada (incluem Python e dependências)

🎯 NÃO PRECISA INSTALAR PYTHON OU DEPENDÊNCIAS!
Estes executáveis funcionam sozinhos em qualquer computador.

Desenvolvido com ❤️ para sua produtividade!
EOF

# Mostrar resultados
echo ""
echo "🎉 EXECUTÁVEIS CRIADOS COM SUCESSO!"
echo "📁 Localização: executaveis_prontos/"
echo ""
echo "📋 Arquivos criados:"
ls -lh executaveis_prontos/

echo ""
echo "✅ PRONTO! Você tem 3 executáveis diferentes:"
echo "   🌐 Web: CrawlerPDF_Web (interface no navegador)"
echo "   ⌨️  Console: CrawlerPDF_Console (linha de comando)" 
echo "   📊 Simples: CrawlerPDF_Simples (versão básica)"
echo ""
echo "💡 Estes arquivos podem ser copiados para qualquer computador"
echo "   e executados sem instalar Python ou dependências!"

# Limpeza opcional
read -p "🗑️ Deseja remover arquivos temporários? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -rf build/ dist/ *.spec
    echo "✅ Arquivos temporários removidos"
else
    echo "⏭️ Arquivos temporários mantidos"
fi

echo ""
echo "🏁 PROCESSO CONCLUÍDO!" 