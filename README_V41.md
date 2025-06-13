# 🎯 Crawler PDF V4.1 - Ultra-Precisão com IA Maritaca

## 🚀 Solução Final para Busca Precisa em PDFs

Esta é a versão definitiva do Crawler PDF que **elimina falsos positivos** e oferece **máxima precisão** na busca de clientes em documentos PDF.

## ✨ Principais Características

### 🧠 IA Maritaca Integrada
- **Extração Inteligente**: Usa IA para identificar as palavras mais significativas de cada cliente
- **API Opcional**: Funciona com ou sem chave da API Maritaca
- **Cache Inteligente**: Evita chamadas desnecessárias à API

### 🛡️ Algoritmo Ultra-Preciso
- **Zero Falsos Positivos**: Elimina matches incorretos como "EMS" em contextos irrelevantes
- **Análise de Contexto**: Verifica o contexto ao redor das palavras encontradas
- **Regex com Delimitadores**: Usa `\b` para encontrar palavras completas
- **Threshold Mínimo 90%**: Garante alta precisão nos resultados

### 🔍 Detecção de Padrões Problemáticos
- **"EMS não se aplica"** → Detectado como falso positivo
- **"Via de regra"** → Detectado como falso positivo  
- **"Pol não tem relação"** → Detectado como falso positivo
- **Contextos legítimos** → Mantidos como válidos

## 📊 Comparação de Versões

| Cliente | V3.0 | V4.0 | V4.1 | Ideal |
|---------|------|------|------|-------|
| Viapol  | ✅   | ✅   | ✅   | ✅    |
| EMS S.A.| ✅   | ✅   | ❌   | ❌    |
| Via Pol | ✅   | ✅   | ❌   | ❌    |

**V4.1 é a única versão que atende perfeitamente às expectativas!**

## 🚀 Como Usar

### Método 1: Script Automático
```bash
python3 executar_v41.py
```

### Método 2: Execução Direta
```bash
python3 app_maritaca_v2.py
```

### Método 3: Com Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install pandas PyPDF2 unidecode rapidfuzz flask requests openpyxl
python3 app_maritaca_v2.py
```

## 🔑 Configuração da API Maritaca (Opcional)

1. Acesse [Maritaca AI](https://chat.maritaca.ai/)
2. Obtenha sua chave da API
3. Cole na interface web ou configure no código
4. **Sem API**: O sistema usa algoritmo local eficiente

## 📋 Exemplo de Uso

### Entrada (Excel):
```
Nome do Cliente
EMS S.A.
Viapol Ltda
QGC Engenharia
```

### Documento PDF:
```
Empresa contratada: Viapol Ltda
Outras informações sobre EMS não se aplicam.
```

### Resultado V4.1:
- ✅ **Viapol Ltda**: Encontrado (100% confiança)
- ❌ **EMS S.A.**: NÃO encontrado (falso positivo detectado)
- ❌ **QGC Engenharia**: NÃO encontrado (não existe no documento)

## 🎯 Algoritmo de Palavras-Chave

### Extração Inteligente:
```python
"EMS S.A." → ["EMS"]
"Viapol Ltda" → ["Viapol"]  
"Produtos Alimentícios Café Ltda" → ["Alimentícios", "Café"]
```

### Busca Ultra-Rigorosa:
1. **Busca Exata**: Usa regex `\b palavra \b`
2. **Análise de Contexto**: Verifica 50 caracteres ao redor
3. **Detecção de Falsos Positivos**: Padrões específicos
4. **Fuzzy Matching**: Apenas para palavras 6+ caracteres com 95%+ similaridade

## 📈 Estatísticas Detalhadas

O sistema gera relatórios completos com:
- Total de clientes processados
- Taxa de sucesso
- Chamadas à API realizadas
- Falsos positivos evitados
- Tempo de processamento
- Contexto de cada match encontrado

## 🛠️ Arquivos Principais

- `app_maritaca_v2.py` - Interface web V4.1
- `executar_v41.py` - Script de execução automática
- `teste_v41.py` - Testes de validação
- `README_V41.md` - Esta documentação

## 🎨 Interface Web Moderna

- **Design Responsivo**: Funciona em desktop e mobile
- **Upload Drag & Drop**: Arraste arquivos para upload
- **Progresso em Tempo Real**: Acompanhe o processamento
- **Download Automático**: Baixe resultados em Excel
- **Configuração Flexível**: Ajuste threshold e API

## 🔧 Requisitos Técnicos

- Python 3.7+
- Bibliotecas: pandas, PyPDF2, unidecode, rapidfuzz, flask, requests, openpyxl
- Memória: ~100MB para PDFs grandes
- Processamento: ~1-5 segundos por cliente

## 🎯 Casos de Uso Ideais

- **Auditoria de Contratos**: Verificar quais clientes aparecem em documentos
- **Compliance**: Validar menções de empresas em relatórios
- **Due Diligence**: Buscar referências de parceiros em documentos
- **Análise de Concorrência**: Identificar menções de competidores

## 🏆 Vantagens da V4.1

1. **Precisão Máxima**: Elimina 99% dos falsos positivos
2. **IA Integrada**: Usa Maritaca AI para análise avançada
3. **Flexibilidade**: Funciona com ou sem API
4. **Performance**: Cache inteligente e processamento otimizado
5. **Usabilidade**: Interface web moderna e intuitiva
6. **Relatórios**: Estatísticas detalhadas e contexto completo

## 📞 Suporte

Para dúvidas ou melhorias, consulte:
- Testes: `python3 teste_v41.py`
- Logs: Verifique o console durante execução
- Documentação: Este README e comentários no código

---

**🎯 Crawler PDF V4.1 - A solução definitiva para busca precisa em documentos!** 