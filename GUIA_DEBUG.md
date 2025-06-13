# 🔍 GUIA DE DEBUG - IDENTIFICAR O PROBLEMA

## 🎯 OBJETIVO

Identificar exatamente onde está ocorrendo o erro quando você clica em "Processar Arquivos".

---

## 📋 PASSOS PARA DEBUG

### **1. Execute a Nova Versão com Logs:**

```bash
cd CrawlerPDF_Desktop_App
./CrawlerPDF_Desktop
```

### **2. Teste o Processamento:**

1. **Abra a interface** no navegador (deve abrir automaticamente)
2. **Selecione os arquivos exemplo:**
   - Excel: `clientes.xlsx`
   - PDF: `documento.pdf`
3. **Mantenha tolerância em 80%**
4. **Clique "Processar Arquivos"**

### **3. Observe o Terminal:**

Agora o terminal mostrará logs detalhados como:

```
🔍 DEBUG: Recebida requisição POST /process
🔍 DEBUG: Excel file: clientes.xlsx
🔍 DEBUG: PDF file: documento.pdf
🔍 DEBUG: Tolerance: 80
🔍 DEBUG: Threshold convertido: 80
🔍 DEBUG: Thread iniciada
🔍 DEBUG: Iniciando thread de processamento
🔍 DEBUG: Iniciando process_files com threshold=80
🔍 DEBUG: Salvando arquivos temporários...
🔍 DEBUG: Diretório temporário criado: /tmp/tmpXXXXXX
🔍 DEBUG: Salvando arquivo Excel...
🔍 DEBUG: Excel salvo em: /tmp/tmpXXXXXX/temp_excel.xlsx
🔍 DEBUG: Salvando arquivo PDF...
🔍 DEBUG: PDF salvo em: /tmp/tmpXXXXXX/temp_pdf.pdf
🔍 DEBUG: Lendo arquivo Excel...
🔍 DEBUG: X clientes encontrados
🔍 DEBUG: Lendo arquivo PDF...
🔍 DEBUG: PDF lido, X caracteres
🔍 DEBUG: Buscando correspondências...
🔍 DEBUG: X resultados processados
🔍 DEBUG: Salvando resultados em: resultados_crawler_YYYYMMDD_HHMMSS.xlsx
🔍 DEBUG: Arquivo Excel salvo com sucesso
🔍 DEBUG: Limpando arquivos temporários...
🔍 DEBUG: Processamento concluído com sucesso!
🔍 DEBUG: Thread concluída, resultado: True
```

---

## 🚨 POSSÍVEIS CENÁRIOS DE ERRO

### **Cenário 1: Erro na Requisição**
```
🔍 DEBUG: ERRO na rota /process: [mensagem de erro]
```
**Solução:** Problema no upload dos arquivos

### **Cenário 2: Erro no Salvamento**
```
🔍 DEBUG: Salvando arquivo Excel...
🔍 DEBUG: ERRO durante processamento: [mensagem de erro]
```
**Solução:** Problema de permissões ou espaço em disco

### **Cenário 3: Erro na Leitura do Excel**
```
🔍 DEBUG: Lendo arquivo Excel...
🔍 DEBUG: 0 clientes encontrados
```
**Solução:** Arquivo Excel vazio ou formato incorreto

### **Cenário 4: Erro na Leitura do PDF**
```
🔍 DEBUG: PDF lido, 0 caracteres
```
**Solução:** PDF corrompido ou protegido

### **Cenário 5: Erro no Processamento**
```
🔍 DEBUG: Buscando correspondências...
🔍 DEBUG: ERRO durante processamento: [mensagem de erro]
```
**Solução:** Problema na lógica de busca

---

## 📝 COMO REPORTAR O PROBLEMA

### **Copie e cole EXATAMENTE:**

1. **Todas as mensagens de DEBUG** que aparecem no terminal
2. **A última mensagem antes do erro**
3. **Qualquer traceback ou stack trace**

### **Exemplo do que preciso ver:**

```
🔍 DEBUG: Recebida requisição POST /process
🔍 DEBUG: Excel file: clientes.xlsx
🔍 DEBUG: PDF file: documento.pdf
🔍 DEBUG: Tolerance: 80
🔍 DEBUG: Threshold convertido: 80
🔍 DEBUG: Thread iniciada
🔍 DEBUG: Iniciando thread de processamento
🔍 DEBUG: Iniciando process_files com threshold=80
🔍 DEBUG: Salvando arquivos temporários...
🔍 DEBUG: ERRO durante processamento: [ERRO ESPECÍFICO AQUI]
🔍 DEBUG: Tipo do erro: [TIPO DO ERRO]
🔍 DEBUG: Traceback completo:
[STACK TRACE COMPLETO AQUI]
```

---

## 🔧 TESTES ALTERNATIVOS

### **Se o executável não funcionar, teste o código Python:**

```bash
cd /Users/andreribeiro/Downloads/Desenvolver\ crawler\ para\ buscar\ dados\ de\ Excel\ em\ PDFs
source venv/bin/activate
python teste_app.py
```

### **Teste manual dos componentes:**

```python
# Teste 1: Importações
python -c "import pandas, PyPDF2, fuzzywuzzy, flask; print('✅ Todas as dependências OK')"

# Teste 2: Leitura do Excel
python -c "import pandas as pd; df = pd.read_excel('clientes.xlsx'); print(f'✅ Excel OK: {len(df)} linhas')"

# Teste 3: Leitura do PDF
python -c "import PyPDF2; f=open('documento.pdf','rb'); r=PyPDF2.PdfReader(f); print(f'✅ PDF OK: {len(r.pages)} páginas')"
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Execute a aplicação**
2. **Teste o processamento**
3. **Copie TODOS os logs do terminal**
4. **Me envie os logs completos**
5. **Vou identificar e corrigir o problema específico**

---

**💡 Com os logs detalhados, conseguirei identificar exatamente onde está o problema e criar uma correção precisa!** 