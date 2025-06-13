# Crawler de Clientes em PDF

Este projeto implementa um crawler em Python para buscar nomes de clientes de um arquivo Excel em documentos PDF, utilizando uma tolerância de similaridade configurável.

## 🚀 Funcionalidades

- ✅ **Tolerância de similaridade configurável** (padrão: 80%)
- ✅ **Múltiplos algoritmos de busca**: ratio, partial_ratio, token_sort_ratio
- ✅ **Detecção de correspondências exatas e fuzzy**
- ✅ **Interface de linha de comando** com argumentos flexíveis
- ✅ **Relatórios detalhados** com metadados e estatísticas
- ✅ **Suporte a múltiplas abas** do Excel
- ✅ **Especificação de colunas** personalizadas
- ✅ **Processamento de PDFs** com múltiplas páginas
- ✅ **Modo silencioso** para processamento em lote

## 📋 Requisitos

### Bibliotecas Python necessárias:

- `pandas` - Manipulação de dados Excel
- `openpyxl` - Leitura de arquivos .xlsx
- `PyPDF2` - Extração de texto de PDFs
- `fuzzywuzzy` - Algoritmos de similaridade
- `python-Levenshtein` - Otimização dos algoritmos

### Instalação

1. **Clone o projeto ou baixe os arquivos**

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
```bash
   pip install -r requirements.txt
```

## 🗂️ Estrutura do Projeto

```
crawler_clientes/
├── venv/                       # Ambiente virtual (criado após instalação)
├── output/                     # Pasta de resultados (criada automaticamente)
├── clientes.xlsx              # Seu arquivo Excel com lista de clientes
├── documento.pdf              # Seu arquivo PDF para busca
├── crawler.py                 # Script básico do crawler
├── crawler_advanced.py        # Script avançado com mais funcionalidades
├── exemplo_uso.py             # Exemplos de como usar o crawler
├── requirements.txt           # Dependências do projeto
└── README.md                  # Esta documentação
```

## 🎯 Como Usar

### Uso Básico

1. **Coloque seus arquivos na pasta do projeto:**
   - Arquivo Excel (`.xlsx`) com a lista de clientes
   - Arquivo PDF (`.pdf`) onde fazer a busca

2. **Execute o crawler básico:**
   ```bash
   python crawler.py
   ```

3. **Ou use a versão avançada:**
   ```bash
   python crawler_advanced.py meu_arquivo.xlsx meu_documento.pdf
   ```

### Uso Avançado com Argumentos

    ```bash
# Exemplo básico
python crawler_advanced.py clientes.xlsx documento.pdf

# Especificar arquivo de saída e tolerância
python crawler_advanced.py clientes.xlsx documento.pdf -o resultados.xlsx -t 90

# Especificar coluna e aba do Excel
python crawler_advanced.py clientes.xlsx documento.pdf --coluna 1 --aba 0

# Modo silencioso (menos mensagens)
python crawler_advanced.py clientes.xlsx documento.pdf --quiet

# Ver todas as opções disponíveis
python crawler_advanced.py --help
```

### Argumentos Disponíveis

| Argumento | Descrição | Padrão |
|-----------|-----------|---------|
| `excel` | Arquivo Excel com lista de clientes | - |
| `pdf` | Arquivo PDF para busca | - |
| `-o, --output` | Arquivo de saída (opcional) | `output/resultados_TIMESTAMP.xlsx` |
| `-t, --threshold` | Tolerância de similaridade (0-100) | 80 |
| `-c, --coluna` | Coluna do Excel (0-indexado) | 0 |
| `-a, --aba` | Aba do Excel (0-indexado) | 0 |
| `-q, --quiet` | Modo silencioso | False |

## 📊 Entendendo os Resultados

O arquivo de saída conterá duas abas:

### Aba "Resultados"
- **cliente**: Nome do cliente do Excel
- **encontrado**: "Sim" ou "Não"
- **similaridade**: Porcentagem de similaridade
- **tipo_match**: "Exata" ou "Fuzzy"
- **score_partial**: Score do algoritmo partial_ratio
- **score_ratio**: Score do algoritmo ratio
- **score_token**: Score do algoritmo token_sort_ratio

### Aba "Metadados"
- Data/hora da execução
- Tolerância utilizada
- Estatísticas gerais

## 🧠 Algoritmos de Similaridade

O crawler usa três algoritmos principais:

1. **Ratio**: Comparação geral entre strings
2. **Partial Ratio**: Busca substring dentro do texto
3. **Token Sort Ratio**: Compara palavras reorganizadas

**Exemplo:**
```
Cliente: "João da Silva"
PDF contém: "SILVA, JOÃO DA"
→ Ratio: 65% | Partial: 87% | Token: 100%
→ Melhor score: 100% ✅ Encontrado!
```

## 💡 Dicas de Uso

### Configuração de Tolerância

- **70-80%**: Para dados com possíveis variações (recomendado)
- **85-90%**: Para dados mais limpos e precisos
- **95-100%**: Apenas correspondências quase exatas

### Preparação dos Dados

1. **Excel**: Certifique-se de que os nomes estão na coluna correta
2. **PDF**: Textos escaneados podem ter baixa qualidade de extração
3. **Formato**: Nomes com acentos, maiúsculas/minúsculas são tratados automaticamente

### Melhorando os Resultados

- Use PDFs com texto selecionável (não imagens)
- Limpe dados duplicados no Excel
- Teste diferentes tolerâncias
- Verifique a qualidade do PDF antes do processamento

## 🔍 Exemplos Práticos

### Executar exemplos demonstrativos:
```bash
python exemplo_uso.py
```

### Processar arquivo grande com progresso:
```bash
python crawler_advanced.py lista_1000_clientes.xlsx relatorio_anual.pdf -t 85
```

### Buscar em coluna específica:
```bash
python crawler_advanced.py planilha.xlsx documento.pdf --coluna 2 --aba 1
```

## 🐛 Solução de Problemas

### Erro: "Module not found"
```bash
# Ative o ambiente virtual
source venv/bin/activate
pip install -r requirements.txt
```

### PDF não processa
- Verifique se o PDF contém texto selecionável
- PDFs escaneados precisam de OCR

### Excel não encontra dados
- Verifique a coluna e aba especificadas
- Certifique-se de que há dados na primeira coluna

### Baixa taxa de sucesso
- Reduza a tolerância (ex: 70%)
- Verifique a qualidade dos dados
- Teste com uma amostra menor primeiro

## 📈 Performance

- **~100 clientes**: Alguns segundos
- **~1000 clientes**: 1-2 minutos
- **~10000 clientes**: 10-20 minutos

*Performance depende do tamanho do PDF e da capacidade do computador.*

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Este projeto foi desenvolvido para ser flexível e extensível.

## 📝 Licença

Este projeto é de uso livre para fins educacionais e comerciais.


