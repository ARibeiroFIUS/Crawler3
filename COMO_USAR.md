# 🚀 COMO USAR O CRAWLER - GUIA RÁPIDO

## 🌐 OPÇÃO 1: INTERFACE WEB (MAIS RECOMENDADA)

### Interface moderna no navegador - funciona em qualquer sistema!

1. **Ative o ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

2. **Execute a interface web:**
   ```bash
   python executar_interface_web.py
   ```
   
   A interface abrirá automaticamente no seu navegador em: http://localhost:5000

3. **Use a interface web:**
   - 📁 **Selecionar Arquivos**: Clique para escolher Excel e PDF
   - 🎯 **Configurar Tolerância**: Use o controle deslizante (70-90% recomendado)
   - ⚙️ **Opções Avançadas**: Configure coluna e aba do Excel se necessário
   - 🚀 **Iniciar**: Clique para processar e veja o progresso em tempo real
   - 📈 **Resultados**: Visualize estatísticas e baixe o arquivo Excel

4. **Vantagens da interface web:**
   - ✅ Funciona em qualquer sistema (Windows, Mac, Linux)
   - ✅ Interface moderna e intuitiva
   - ✅ Acompanhamento do progresso em tempo real
   - ✅ Log detalhado do processamento
   - ✅ Download direto dos resultados
   - ✅ Não precisa saber linha de comando

---

## 🖥️ OPÇÃO 2: INTERFACE GRÁFICA DESKTOP

### Para sistemas com tkinter disponível

1. **Ative o ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

2. **Execute a interface:**
   ```bash
   python executar_interface.py
   ```
   
   Ou use o script automático:
   ```bash
   ./executar_interface.sh
   ```

3. **Use a interface:**
   - 📁 **Procurar**: Selecione seu arquivo Excel e PDF
   - 💾 **Pasta de Saída**: Escolha onde salvar os resultados
   - ⚙️ **Configurações**: Ajuste tolerância e colunas do Excel
   - 🚀 **Iniciar**: Clique para processar e acompanhe o progresso

4. **Visualizar resultados:**
   - Acompanhe o log em tempo real
   - Veja estatísticas na interface
   - Clique para abrir a pasta de resultados

---

## ⌨️ OPÇÃO 3: LINHA DE COMANDO (AVANÇADA)

### Para usuários experientes ou automação

## Passo 1: Preparação
1. Coloque seu arquivo Excel (`.xlsx`) na pasta do projeto
2. Coloque seu arquivo PDF (`.pdf`) na pasta do projeto  
3. Abra o terminal nesta pasta

## Passo 2: Ativar o ambiente
```bash
source venv/bin/activate
```

## Passo 3: Executar o crawler

### Para usar seus próprios arquivos:
```bash
python crawler_advanced.py SEU_ARQUIVO.xlsx SEU_PDF.pdf
```

### Exemplos práticos:
```bash
# Exemplo básico
python crawler_advanced.py lista_clientes.xlsx relatorio.pdf

# Com tolerância específica (mais rígida)
python crawler_advanced.py lista_clientes.xlsx relatorio.pdf -t 90

# Especificar arquivo de saída
python crawler_advanced.py lista_clientes.xlsx relatorio.pdf -o meus_resultados.xlsx

# Se os nomes estão na segunda coluna do Excel
python crawler_advanced.py lista_clientes.xlsx relatorio.pdf --coluna 1

# Se os nomes estão na segunda aba do Excel
python crawler_advanced.py lista_clientes.xlsx relatorio.pdf --aba 1
```

## Passo 4: Verificar resultados
- Os resultados ficam na pasta `output/`
- Abra o arquivo Excel gerado para ver os resultados

---

## ⚙️ Configurações Importantes

### Tolerância de Similaridade:
- **70-80%**: Recomendado para a maioria dos casos
- **85-95%**: Para dados muito limpos
- **60-70%**: Para dados com muitas variações

### Estrutura do Excel:
- O crawler lê a **primeira coluna** por padrão
- Use `--coluna X` para especificar outra coluna (0 = primeira, 1 = segunda, etc.)
- Use `--aba X` para especificar outra aba (0 = primeira, 1 = segunda, etc.)

## 🎯 Exemplo Real de Uso

Suponha que você tenha:
- `clientes_empresa.xlsx` com nomes na coluna B (segunda coluna)
- `contrato_2024.pdf` para buscar
- Quer tolerância de 85%

**Interface Web (mais fácil):**
1. Abra: `python executar_interface_web.py`
2. Selecione os arquivos clicando em "Procurar"
3. Configure tolerância: 85% (use o controle deslizante)
4. Configure coluna: 1 (segunda coluna)
5. Clique "INICIAR PROCESSAMENTO"
6. Acompanhe o progresso e baixe os resultados

**Interface Gráfica:**
1. Abra a interface: `python executar_interface.py`
2. Selecione os arquivos pelos botões "Procurar"
3. Configure tolerância: 85%
4. Configure coluna: 1 (segunda coluna)
5. Clique "INICIAR PROCESSAMENTO"

**Linha de Comando:**
```bash
python crawler_advanced.py clientes_empresa.xlsx contrato_2024.pdf --coluna 1 -t 85 -o resultado_contrato.xlsx
```

## 📊 Interpretando os Resultados

No arquivo Excel gerado você encontrará:

**Aba "Resultados":**
- `cliente`: Nome original do seu Excel
- `encontrado`: "Sim" ou "Não"  
- `similaridade`: Porcentagem de certeza
- `tipo_match`: "Exata" (100% igual) ou "Fuzzy" (similar)

**Aba "Metadados":**
- Estatísticas gerais da busca
- Data/hora da execução
- Configurações utilizadas

## 🆘 Precisa de Ajuda?

### Interface Web:
- Acesse http://localhost:5000 após executar o script
- Todas as instruções estão na própria interface
- Funciona em qualquer navegador

### Interface Gráfica:
- Abra a aba "❓ Ajuda" na interface
- Todas as instruções estão lá

### Linha de Comando:
```bash
python crawler_advanced.py --help
```

### Testar com arquivos de exemplo:
```bash
python exemplo_uso.py
```

### Problemas comuns:

1. **"Module not found"**: Execute `source venv/bin/activate` primeiro
2. **"File not found"**: Verifique se os arquivos estão na pasta correta
3. **"Taxa de sucesso baixa"**: Diminua a tolerância (ex: `-t 70`)
4. **"Excel vazio"**: Verifique se especificou a coluna correta
5. **Interface não abre**: Use a interface web como alternativa
6. **Servidor não inicia**: Verifique se a porta 5000 está livre

## 💡 Dicas para Melhores Resultados

1. **PDFs com texto selecionável** funcionam melhor
2. **Limpe dados duplicados** no Excel antes de processar
3. **Teste com uma amostra pequena** primeiro
4. **Use tolerância 80%** como ponto de partida
5. **Verifique a coluna e aba corretas** do Excel
6. **Use a interface web** - é a mais fácil e compatível

---

## 🎉 Resumo Rápido

### Para Iniciantes (Interface Web):
1. `source venv/bin/activate`
2. `python executar_interface_web.py`
3. Acesse http://localhost:5000 no navegador
4. Selecione arquivos e clique "INICIAR"

### Para Usuários Desktop:
1. `source venv/bin/activate`
2. `python executar_interface.py`
3. Selecione arquivos e clique "INICIAR"

### Para Avançados:
1. `source venv/bin/activate`
2. `python crawler_advanced.py arquivo.xlsx documento.pdf`

*Pronto! Agora você pode usar o crawler com seus próprios arquivos de 3 formas diferentes.* 🎉 