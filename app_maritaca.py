#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler PDF V4.0 - Com IA Maritaca para Palavras-Chave
=====================================================
Versão que usa IA generativa para identificar palavras mais significativas
"""

import os
import tempfile
import shutil
import hashlib
import json
import time
import requests
from datetime import datetime
import pandas as pd
import PyPDF2
import unidecode
from rapidfuzz import fuzz
from flask import Flask, render_template_string, request, jsonify, send_file
import threading
import re

# ----------- Configuração da API Maritaca -----------

MARITACA_API_KEY = ""  # Será configurado pelo usuário
MARITACA_API_URL = "https://chat.maritaca.ai/api/chat/inference"

def extrair_palavras_chave_maritaca(nome_cliente, api_key):
    """Usa a API da Maritaca para extrair palavras-chave significativas do nome do cliente"""
    
    if not api_key:
        # Fallback: usar método simples se não tiver API key
        return extrair_palavras_chave_simples(nome_cliente)
    
    prompt = f"""
Analise o nome da empresa "{nome_cliente}" e extraia as 1-3 palavras mais significativas e únicas que melhor identificam esta empresa.

Regras:
- Ignore palavras genéricas como: S.A., LTDA, EIRELI, ME, CIA, INC, CORP, DO, DA, DE, E, EM, COM
- Foque nas palavras que realmente identificam a empresa
- Se for sigla (ex: EMS, QGC), mantenha a sigla completa
- Se for nome composto, escolha as palavras mais distintivas
- Retorne apenas as palavras, separadas por vírgula
- Máximo 3 palavras

Exemplos:
- "EMS S.A." → "EMS"
- "Viapol Ltda" → "Viapol"  
- "Produtos Alimentícios Café Ltda" → "Produtos, Alimentícios, Café"
- "Aços Equipamentos e Serviços de Informática Ltda" → "Aços, Equipamentos, Informática"

Nome da empresa: "{nome_cliente}"
Palavras-chave:"""

    try:
        headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "do_sample": True,
            "max_tokens": 50,
            "temperature": 0.1,
            "top_p": 0.95
        }
        
        response = requests.post(MARITACA_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            palavras = result.get('answer', '').strip()
            
            # Limpar e processar resposta
            palavras_lista = [p.strip() for p in palavras.split(',') if p.strip()]
            
            # Validar que não retornou o nome completo
            if len(palavras_lista) <= 3 and all(len(p) >= 2 for p in palavras_lista):
                return palavras_lista
            else:
                # Fallback se a resposta não foi boa
                return extrair_palavras_chave_simples(nome_cliente)
                
        else:
            print(f"Erro na API Maritaca: {response.status_code}")
            return extrair_palavras_chave_simples(nome_cliente)
            
    except Exception as e:
        print(f"Erro ao chamar API Maritaca: {e}")
        return extrair_palavras_chave_simples(nome_cliente)

def extrair_palavras_chave_simples(nome_cliente):
    """Método fallback simples para extrair palavras-chave"""
    if not nome_cliente or not isinstance(nome_cliente, str):
        return []
    
    # Palavras a ignorar
    ignore_words = {
        'sa', 's.a', 's.a.', 'ltda', 'ltda.', 'eireli', 'me', 'empresa', 'cia', 'cia.', 
        'inc', 'corp', 'co', 'do', 'da', 'de', 'dos', 'das', 'e', 'em', 'com', 'para', 
        'por', 'a', 'o', 'as', 'os', 'limitada', 'sociedade', 'anonima'
    }
    
    # Normalizar e dividir
    nome_limpo = re.sub(r'[^\w\s]', ' ', nome_cliente.lower())
    palavras = [p.strip() for p in nome_limpo.split() if p.strip()]
    
    # Filtrar palavras significativas
    palavras_significativas = []
    for palavra in palavras:
        if len(palavra) >= 2 and palavra not in ignore_words:
            palavras_significativas.append(palavra)
    
    # Retornar no máximo 3 palavras mais longas
    palavras_significativas.sort(key=len, reverse=True)
    return palavras_significativas[:3]

def buscar_palavras_chave_no_texto(palavras_chave, texto, min_threshold=85):
    """Busca as palavras-chave no texto com alta precisão"""
    
    if not palavras_chave:
        return {
            'found': False,
            'confidence': 0,
            'palavras_encontradas': [],
            'context': 'Nenhuma palavra-chave definida'
        }
    
    texto_normalizado = unidecode.unidecode(texto.lower())
    palavras_encontradas = []
    contextos = []
    scores = []
    
    for palavra in palavras_chave:
        palavra_norm = unidecode.unidecode(palavra.lower())
        
        # Busca exata primeiro
        if palavra_norm in texto_normalizado:
            palavras_encontradas.append(palavra)
            scores.append(100)
            
            # Encontrar contexto
            idx = texto_normalizado.find(palavra_norm)
            start = max(0, idx-30)
            end = min(len(texto), idx+len(palavra_norm)+30)
            contextos.append(texto[start:end])
            
        else:
            # Busca fuzzy apenas para palavras longas (6+ caracteres)
            if len(palavra_norm) >= 6:
                # Dividir texto em palavras e testar cada uma
                palavras_texto = re.findall(r'\b\w+\b', texto_normalizado)
                melhor_score = 0
                melhor_contexto = ""
                
                for palavra_texto in palavras_texto:
                    if len(palavra_texto) >= len(palavra_norm) - 2:  # Tamanho similar
                        score = fuzz.ratio(palavra_norm, palavra_texto)
                        if score > melhor_score and score >= min_threshold:
                            melhor_score = score
                            
                            # Encontrar contexto
                            idx = texto_normalizado.find(palavra_texto)
                            start = max(0, idx-30)
                            end = min(len(texto), idx+len(palavra_texto)+30)
                            melhor_contexto = texto[start:end]
                
                if melhor_score >= min_threshold:
                    palavras_encontradas.append(f"{palavra} (~{melhor_score}%)")
                    scores.append(melhor_score)
                    contextos.append(melhor_contexto)
    
    # Determinar se foi encontrado
    if not palavras_encontradas:
        return {
            'found': False,
            'confidence': 0,
            'palavras_encontradas': [],
            'context': 'Nenhuma palavra-chave encontrada'
        }
    
    # Calcular confiança baseada na proporção de palavras encontradas
    proporcao_encontrada = len(palavras_encontradas) / len(palavras_chave)
    confianca_media = sum(scores) / len(scores)
    confianca_final = int(confianca_media * proporcao_encontrada)
    
    # Critério para considerar "encontrado"
    found = False
    if len(palavras_chave) == 1:
        # Para uma palavra-chave: precisa encontrar com alta confiança
        found = confianca_final >= 90
    else:
        # Para múltiplas palavras: precisa encontrar pelo menos 50% com boa confiança
        found = proporcao_encontrada >= 0.5 and confianca_final >= 80
    
    return {
        'found': found,
        'confidence': confianca_final,
        'palavras_encontradas': palavras_encontradas,
        'context': ' | '.join(contextos[:2])  # Máximo 2 contextos
    }

# -------------- Classe principal --------------

class CrawlerPDFV4:
    def __init__(self):
        self.threshold = 85  # Threshold mais alto para maior precisão
        self.results = []
        self.processing = False
        self.cancelled = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.last_output_file = None
        self.last_output_filename = None
        self.maritaca_api_key = ""
        self.palavras_chave_cache = {}  # Cache para evitar chamadas repetidas à API
        self.stats = {
            'processing_start': None,
            'processing_end': None,
            'total_clients': 0,
            'clients_found': 0,
            'clients_not_found': 0,
            'pdf_pages': 0,
            'api_calls': 0
        }

    def set_maritaca_api_key(self, api_key):
        """Define a chave da API Maritaca"""
        self.maritaca_api_key = api_key.strip()

    def reset_processing(self):
        """Reset do estado de processamento"""
        self.processing = False
        self.cancelled = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.results = []
        self.palavras_chave_cache = {}

    def cancel_processing(self):
        """Cancela o processamento"""
        self.cancelled = True
        self.status_message = "Cancelando..."

    def read_excel_clients(self, excel_path: str):
        """Lê a lista de clientes do Excel"""
        df = pd.read_excel(excel_path)
        # Pegar a primeira coluna que contém texto
        for col in df.columns:
            if df[col].dtype == 'object':
                return df[col].dropna().tolist()
        return []

    def read_pdf(self, pdf_path: str):
        """Lê o conteúdo do PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.stats['pdf_pages'] = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
        return text

    def extrair_palavras_chave_cliente(self, nome_cliente):
        """Extrai palavras-chave do cliente, usando cache"""
        
        if nome_cliente in self.palavras_chave_cache:
            return self.palavras_chave_cache[nome_cliente]
        
        self.status_message = f"Analisando palavras-chave: {nome_cliente}"
        
        if self.maritaca_api_key:
            palavras = extrair_palavras_chave_maritaca(nome_cliente, self.maritaca_api_key)
            self.stats['api_calls'] += 1
        else:
            palavras = extrair_palavras_chave_simples(nome_cliente)
        
        self.palavras_chave_cache[nome_cliente] = palavras
        return palavras

    def process_files(self, excel_path, pdf_path, threshold):
        """Processa os arquivos Excel e PDF"""
        
        self.reset_processing()
        self.processing = True
        self.threshold = threshold
        self.stats['processing_start'] = datetime.now()
        
        try:
            # Ler arquivos
            self.status_message = "Lendo lista de clientes..."
            clients = self.read_excel_clients(excel_path)
            self.stats['total_clients'] = len(clients)
            
            if self.cancelled:
                return []
            
            self.status_message = "Lendo documento PDF..."
            pdf_text = self.read_pdf(pdf_path)
            
            if self.cancelled:
                return []
            
            # Processar cada cliente
            self.results = []
            
            for i, client in enumerate(clients):
                if self.cancelled:
                    break
                
                self.progress = int((i / len(clients)) * 100)
                
                # Extrair palavras-chave
                palavras_chave = self.extrair_palavras_chave_cliente(client)
                
                self.status_message = f"Buscando: {client} (palavras: {', '.join(palavras_chave)})"
                
                # Buscar no PDF
                match_result = buscar_palavras_chave_no_texto(palavras_chave, pdf_text, self.threshold)
                
                # Preparar resultado
                result = {
                    'cliente': client,
                    'palavras_chave': palavras_chave,
                    'encontrado': 'Sim' if match_result['found'] else 'Não',
                    'similaridade': f"{match_result['confidence']}%",
                    'palavras_encontradas': ', '.join(match_result['palavras_encontradas']),
                    'contexto': match_result['context'][:200] + '...' if len(match_result['context']) > 200 else match_result['context']
                }
                
                self.results.append(result)
                
                if match_result['found']:
                    self.stats['clients_found'] += 1
                else:
                    self.stats['clients_not_found'] += 1
            
            self.progress = 100
            self.stats['processing_end'] = datetime.now()
            
            # Salvar resultados
            self.save_results()
            
            self.status_message = f"Concluído! {self.stats['clients_found']}/{self.stats['total_clients']} clientes encontrados"
            
        except Exception as e:
            self.status_message = f"Erro: {str(e)}"
            print(f"Erro no processamento: {e}")
        
        finally:
            self.processing = False
        
        return self.results

    def save_results(self):
        """Salva os resultados em Excel"""
        if not self.results:
            return
        
        # Criar DataFrame
        df = pd.DataFrame(self.results)
        
        # Adicionar estatísticas
        stats_data = {
            'Estatística': [
                'Total de Clientes',
                'Clientes Encontrados', 
                'Clientes Não Encontrados',
                'Taxa de Sucesso',
                'Páginas do PDF',
                'Chamadas à API',
                'Tempo de Processamento',
                'Threshold Usado'
            ],
            'Valor': [
                self.stats['total_clients'],
                self.stats['clients_found'],
                self.stats['clients_not_found'],
                f"{(self.stats['clients_found']/self.stats['total_clients']*100):.1f}%" if self.stats['total_clients'] > 0 else "0%",
                self.stats['pdf_pages'],
                self.stats['api_calls'],
                str(self.stats['processing_end'] - self.stats['processing_start']).split('.')[0] if self.stats['processing_end'] else "N/A",
                f"{self.threshold}%"
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        
        # Salvar em arquivo temporário
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_crawler_v4_{timestamp}.xlsx"
        filepath = os.path.join(temp_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resultados', index=False)
            stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        self.last_output_file = filepath
        self.last_output_filename = filename

# -------------- Flask App --------------

app = Flask(__name__)
crawler = CrawlerPDFV4()

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler PDF V4.0 - Com IA Maritaca</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .api-config {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        input[type="file"], input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="file"]:focus, input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .threshold-group {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .threshold-slider {
            flex: 1;
        }
        
        .threshold-value {
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            min-width: 60px;
            text-align: center;
        }
        
        .btn {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .progress-container {
            margin-top: 30px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            width: 0%;
            transition: width 0.3s;
        }
        
        .status {
            text-align: center;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .results {
            margin-top: 30px;
            display: none;
        }
        
        .results-header {
            background: #2ecc71;
            color: white;
            padding: 15px;
            border-radius: 8px 8px 0 0;
            text-align: center;
            font-weight: 600;
        }
        
        .results-content {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 0 0 8px 8px;
            border: 1px solid #e0e0e0;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            margin-top: 15px;
        }
        
        .cancel-btn {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            margin-top: 10px;
        }
        
        .info-box {
            background: #e8f4fd;
            border: 1px solid #3498db;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .info-box h3 {
            color: #2980b9;
            margin-bottom: 10px;
        }
        
        .info-box ul {
            margin-left: 20px;
        }
        
        .info-box li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Crawler PDF V4.0</h1>
            <p>Busca Inteligente com IA Maritaca - Palavras-Chave Otimizadas</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>🚀 Novidades da Versão 4.0:</h3>
                <ul>
                    <li><strong>IA Maritaca:</strong> Extrai automaticamente as palavras mais significativas de cada cliente</li>
                    <li><strong>Busca Otimizada:</strong> Foca apenas nas palavras-chave relevantes, evitando falsos positivos</li>
                    <li><strong>Maior Precisão:</strong> Reduz drasticamente matches incorretos como "EMS" em textos aleatórios</li>
                    <li><strong>Cache Inteligente:</strong> Evita chamadas desnecessárias à API</li>
                </ul>
            </div>
            
            <div class="api-config">
                <h3>🔑 Configuração da API Maritaca (Opcional)</h3>
                <p style="margin-bottom: 15px; color: #666;">
                    Se você tem uma chave da API Maritaca, cole aqui para usar IA avançada. 
                    Caso contrário, será usado um algoritmo simples mas eficiente.
                </p>
                <div class="form-group">
                    <label for="maritaca-key">Chave da API Maritaca:</label>
                    <input type="password" id="maritaca-key" placeholder="Opcional - deixe em branco para usar algoritmo simples">
                </div>
            </div>
            
            <form id="upload-form">
                <div class="form-group">
                    <label for="excel-file">📊 Arquivo Excel com Lista de Clientes:</label>
                    <input type="file" id="excel-file" accept=".xlsx,.xls" required>
                </div>
                
                <div class="form-group">
                    <label for="pdf-file">📄 Documento PDF para Busca:</label>
                    <input type="file" id="pdf-file" accept=".pdf" required>
                </div>
                
                <div class="form-group">
                    <label>🎯 Precisão da Busca:</label>
                    <div class="threshold-group">
                        <input type="range" id="threshold" class="threshold-slider" min="70" max="100" value="85">
                        <div class="threshold-value" id="threshold-value">85%</div>
                    </div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        Valores mais altos = maior precisão, menos falsos positivos
                    </small>
                </div>
                
                <button type="submit" class="btn" id="process-btn">
                    🚀 Iniciar Busca Inteligente
                </button>
                
                <button type="button" class="btn cancel-btn" id="cancel-btn" style="display: none;">
                    ❌ Cancelar Processamento
                </button>
            </form>
            
            <div class="progress-container" id="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <div class="status" id="status">Processando...</div>
            </div>
            
            <div class="results" id="results">
                <div class="results-header">
                    ✅ Processamento Concluído!
                </div>
                <div class="results-content">
                    <p id="results-summary">Resultados processados com sucesso.</p>
                    <button class="btn download-btn" id="download-btn">
                        📥 Baixar Resultados Completos
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Atualizar valor do threshold
        const thresholdSlider = document.getElementById('threshold');
        const thresholdValue = document.getElementById('threshold-value');
        
        thresholdSlider.addEventListener('input', function() {
            thresholdValue.textContent = this.value + '%';
        });
        
        // Processar formulário
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('excel_file', document.getElementById('excel-file').files[0]);
            formData.append('pdf_file', document.getElementById('pdf-file').files[0]);
            formData.append('threshold', document.getElementById('threshold').value);
            formData.append('maritaca_key', document.getElementById('maritaca-key').value);
            
            // Mostrar progresso
            document.getElementById('progress-container').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('process-btn').disabled = true;
            document.getElementById('cancel-btn').style.display = 'block';
            
            try {
                const response = await fetch('/process_v4', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    // Monitorar progresso
                    monitorProgress();
                } else {
                    alert('Erro ao iniciar processamento');
                    resetUI();
                }
            } catch (error) {
                alert('Erro: ' + error.message);
                resetUI();
            }
        });
        
        // Monitorar progresso
        function monitorProgress() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch('/progress_v4');
                    const data = await response.json();
                    
                    document.getElementById('progress-fill').style.width = data.progress + '%';
                    document.getElementById('status').textContent = data.status;
                    
                    if (!data.processing) {
                        clearInterval(interval);
                        
                        if (data.results && data.results.length > 0) {
                            showResults(data);
                        }
                        
                        resetUI();
                    }
                } catch (error) {
                    console.error('Erro ao monitorar progresso:', error);
                }
            }, 1000);
        }
        
        // Mostrar resultados
        function showResults(data) {
            const found = data.results.filter(r => r.encontrado === 'Sim').length;
            const total = data.results.length;
            
            document.getElementById('results-summary').innerHTML = `
                <strong>📊 Resumo dos Resultados:</strong><br>
                • Total de clientes: ${total}<br>
                • Clientes encontrados: ${found}<br>
                • Taxa de sucesso: ${((found/total)*100).toFixed(1)}%<br>
                • Chamadas à API: ${data.api_calls || 0}
            `;
            
            document.getElementById('results').style.display = 'block';
        }
        
        // Reset da interface
        function resetUI() {
            document.getElementById('process-btn').disabled = false;
            document.getElementById('cancel-btn').style.display = 'none';
        }
        
        // Cancelar processamento
        document.getElementById('cancel-btn').addEventListener('click', async function() {
            try {
                await fetch('/cancel', { method: 'POST' });
            } catch (error) {
                console.error('Erro ao cancelar:', error);
            }
        });
        
        // Download dos resultados
        document.getElementById('download-btn').addEventListener('click', function() {
            window.location.href = '/download/latest';
        });
    </script>
</body>
</html>
    """)

@app.route('/process_v4', methods=['POST'])
def process_files_v4():
    """Endpoint para processar arquivos com IA Maritaca"""
    
    if crawler.processing:
        return jsonify({'error': 'Já existe um processamento em andamento'}), 400
    
    try:
        # Configurar API Maritaca se fornecida
        maritaca_key = request.form.get('maritaca_key', '').strip()
        if maritaca_key:
            crawler.set_maritaca_api_key(maritaca_key)
        
        # Salvar arquivos temporários
        excel_file = request.files['excel_file']
        pdf_file = request.files['pdf_file']
        threshold = int(request.form.get('threshold', 85))
        
        temp_dir = tempfile.gettempdir()
        excel_path = os.path.join(temp_dir, f"temp_excel_{int(time.time())}.xlsx")
        pdf_path = os.path.join(temp_dir, f"temp_pdf_{int(time.time())}.pdf")
        
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        
        # Processar em thread separada
        def process_thread():
            crawler.process_files(excel_path, pdf_path, threshold)
            # Limpar arquivos temporários
            try:
                os.remove(excel_path)
                os.remove(pdf_path)
            except:
                pass
        
        thread = threading.Thread(target=process_thread)
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress_v4')
def get_progress_v4():
    """Endpoint para monitorar progresso"""
    return jsonify({
        'processing': crawler.processing,
        'progress': crawler.progress,
        'status': crawler.status_message,
        'results': crawler.results if not crawler.processing else None,
        'api_calls': crawler.stats.get('api_calls', 0)
    })

@app.route('/cancel', methods=['POST'])
def cancel_processing():
    """Endpoint para cancelar processamento"""
    crawler.cancel_processing()
    return jsonify({'success': True})

@app.route('/download/latest')
def download_latest():
    """Endpoint para download do último resultado"""
    if crawler.last_output_file and os.path.exists(crawler.last_output_file):
        return send_file(
            crawler.last_output_file,
            as_attachment=True,
            download_name=crawler.last_output_filename
        )
    else:
        return "Nenhum resultado disponível", 404

if __name__ == '__main__':
    print("🤖 Crawler PDF V4.0 - Com IA Maritaca")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 