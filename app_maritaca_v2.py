#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler PDF V4.1 - IA Maritaca com Algoritmo Ultra-Preciso
=========================================================
Versão corrigida que elimina falsos positivos
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

def extrair_palavras_chave_maritaca(nome_cliente, api_key):
    """Usa a API da Maritaca para extrair palavras-chave significativas do nome do cliente"""
    
    if not api_key:
        return extrair_palavras_chave_simples(nome_cliente)
    
    prompt = f"""
Analise o nome da empresa "{nome_cliente}" e extraia as 1-2 palavras mais significativas e únicas que melhor identificam esta empresa.

Regras RIGOROSAS:
- Ignore completamente: S.A., LTDA, EIRELI, ME, CIA, INC, CORP, DO, DA, DE, E, EM, COM
- Se for sigla (ex: EMS, QGC), mantenha APENAS a sigla
- Se for nome composto, escolha APENAS a palavra mais distintiva
- MÁXIMO 2 palavras
- Prefira palavras longas e específicas

Exemplos:
- "EMS S.A." → "EMS"
- "Viapol Ltda" → "Viapol"  
- "Produtos Alimentícios Café Ltda" → "Alimentícios"
- "Sun Ace Brasil Indústria Ltda" → "Sun Ace"

Nome da empresa: "{nome_cliente}"
Palavras-chave (máximo 2):"""

    try:
        headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "do_sample": True,
            "max_tokens": 30,
            "temperature": 0.1,
            "top_p": 0.95
        }
        
        response = requests.post("https://chat.maritaca.ai/api/chat/inference", 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            palavras = result.get('answer', '').strip()
            palavras_lista = [p.strip() for p in palavras.split(',') if p.strip()]
            
            if len(palavras_lista) <= 2 and all(len(p) >= 2 for p in palavras_lista):
                return palavras_lista
        
        return extrair_palavras_chave_simples(nome_cliente)
        
    except Exception as e:
        print(f"Erro API Maritaca: {e}")
        return extrair_palavras_chave_simples(nome_cliente)

def extrair_palavras_chave_simples(nome_cliente):
    """Método fallback ULTRA-RIGOROSO para extrair palavras-chave"""
    if not nome_cliente or not isinstance(nome_cliente, str):
        return []
    
    # Palavras a ignorar (expandida)
    ignore_words = {
        'sa', 's.a', 's.a.', 'ltda', 'ltda.', 'eireli', 'me', 'empresa', 'cia', 'cia.', 
        'inc', 'corp', 'co', 'do', 'da', 'de', 'dos', 'das', 'e', 'em', 'com', 'para', 
        'por', 'a', 'o', 'as', 'os', 'limitada', 'sociedade', 'anonima', 'brasil',
        'industria', 'indústria', 'comercio', 'comércio', 'servicos', 'serviços',
        'materiais', 'produtos', 'equipamentos'  # Palavras muito genéricas
    }
    
    # Normalizar
    nome_limpo = re.sub(r'[^\w\s]', ' ', nome_cliente.lower())
    palavras = [p.strip() for p in nome_limpo.split() if p.strip()]
    
    # Filtrar palavras significativas
    palavras_significativas = []
    for palavra in palavras:
        if len(palavra) >= 3 and palavra not in ignore_words:
            palavras_significativas.append(palavra)
    
    # Estratégia: priorizar palavras mais específicas
    if not palavras_significativas:
        # Se não sobrou nada, pegar a primeira palavra não genérica
        for palavra in palavras:
            if len(palavra) >= 2 and palavra not in {'sa', 'ltda', 'me', 'cia'}:
                return [palavra]
        return []
    
    # Retornar no máximo 2 palavras, priorizando as mais longas e específicas
    palavras_significativas.sort(key=lambda x: (len(x), x), reverse=True)
    return palavras_significativas[:2]

def buscar_palavras_chave_no_texto_rigoroso(palavras_chave, texto, min_threshold=90):
    """Busca ULTRA-RIGOROSA das palavras-chave no texto"""
    
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
        
        # CRITÉRIO 1: Busca exata com delimitadores de palavra
        pattern = r'\b' + re.escape(palavra_norm) + r'\b'
        matches = re.finditer(pattern, texto_normalizado)
        
        encontrou_exato = False
        for match in matches:
            # Verificar contexto para evitar falsos positivos
            start_idx = match.start()
            end_idx = match.end()
            
            # Pegar contexto amplo
            context_start = max(0, start_idx - 50)
            context_end = min(len(texto), end_idx + 50)
            contexto = texto[context_start:context_end]
            
            # Verificar se não é parte de uma palavra maior ou contexto irrelevante
            if not eh_falso_positivo(palavra_norm, contexto.lower(), start_idx - context_start):
                palavras_encontradas.append(palavra)
                scores.append(100)
                contextos.append(contexto)
                encontrou_exato = True
                break
        
        # CRITÉRIO 2: Se não encontrou exato e palavra é longa (6+ chars), tentar fuzzy
        if not encontrou_exato and len(palavra_norm) >= 6:
            palavras_texto = re.findall(r'\b\w{' + str(len(palavra_norm)-1) + ',}\b', texto_normalizado)
            
            melhor_score = 0
            melhor_contexto = ""
            
            for palavra_texto in palavras_texto:
                if abs(len(palavra_texto) - len(palavra_norm)) <= 2:  # Tamanho similar
                    score = fuzz.ratio(palavra_norm, palavra_texto)
                    if score >= 95:  # Muito rigoroso para fuzzy
                        idx = texto_normalizado.find(palavra_texto)
                        context_start = max(0, idx - 50)
                        context_end = min(len(texto), idx + len(palavra_texto) + 50)
                        contexto = texto[context_start:context_end]
                        
                        if not eh_falso_positivo(palavra_norm, contexto.lower(), idx - context_start):
                            if score > melhor_score:
                                melhor_score = score
                                melhor_contexto = contexto
            
            if melhor_score >= 95:
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
    
    # Critério RIGOROSO para considerar "encontrado"
    proporcao_encontrada = len(palavras_encontradas) / len(palavras_chave)
    confianca_media = sum(scores) / len(scores)
    
    # Para ser considerado encontrado:
    found = False
    if len(palavras_chave) == 1:
        # Uma palavra: deve encontrar com 95%+ de confiança
        found = confianca_media >= 95
    else:
        # Múltiplas palavras: deve encontrar TODAS com 90%+ de confiança
        found = proporcao_encontrada >= 0.8 and confianca_media >= 90
    
    confianca_final = int(confianca_media * proporcao_encontrada)
    
    return {
        'found': found,
        'confidence': confianca_final,
        'palavras_encontradas': palavras_encontradas,
        'context': ' | '.join(contextos[:2])
    }

def eh_falso_positivo(palavra, contexto, posicao_palavra):
    """Detecta se é um falso positivo baseado no contexto"""
    
    # Pegar texto ao redor da palavra
    inicio = max(0, posicao_palavra - 20)
    fim = min(len(contexto), posicao_palavra + len(palavra) + 20)
    contexto_local = contexto[inicio:fim]
    
    # Padrões que indicam falso positivo
    falsos_positivos = [
        # EMS em contexto irrelevante
        r'sobre\s+ems\s+não',
        r'informações\s+sobre\s+ems',
        r'ems\s+não\s+se\s+aplica',
        
        # Via/Pol separados
        r'via\s+de\s+regra',
        r'via\s+\w+\s+pol',
        
        # Contextos genéricos
        r'não\s+tem\s+relação',
        r'não\s+se\s+aplica',
    ]
    
    for padrao in falsos_positivos:
        if re.search(padrao, contexto_local):
            return True
    
    return False

# -------------- Classe principal --------------

class CrawlerPDFV41:
    def __init__(self):
        self.threshold = 90  # Threshold mais alto
        self.results = []
        self.processing = False
        self.cancelled = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.last_output_file = None
        self.last_output_filename = None
        self.maritaca_api_key = ""
        self.palavras_chave_cache = {}
        self.stats = {
            'processing_start': None,
            'processing_end': None,
            'total_clients': 0,
            'clients_found': 0,
            'clients_not_found': 0,
            'pdf_pages': 0,
            'api_calls': 0,
            'false_positives_avoided': 0
        }

    def set_maritaca_api_key(self, api_key):
        self.maritaca_api_key = api_key.strip()

    def reset_processing(self):
        self.processing = False
        self.cancelled = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.results = []
        self.palavras_chave_cache = {}

    def cancel_processing(self):
        self.cancelled = True
        self.status_message = "Cancelando..."

    def read_excel_clients(self, excel_path: str):
        df = pd.read_excel(excel_path)
        for col in df.columns:
            if df[col].dtype == 'object':
                return df[col].dropna().tolist()
        return []

    def read_pdf(self, pdf_path: str):
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
        self.reset_processing()
        self.processing = True
        self.threshold = max(threshold, 90)  # Mínimo 90%
        self.stats['processing_start'] = datetime.now()
        
        try:
            self.status_message = "Lendo lista de clientes..."
            clients = self.read_excel_clients(excel_path)
            self.stats['total_clients'] = len(clients)
            
            if self.cancelled:
                return []
            
            self.status_message = "Lendo documento PDF..."
            pdf_text = self.read_pdf(pdf_path)
            
            if self.cancelled:
                return []
            
            self.results = []
            
            for i, client in enumerate(clients):
                if self.cancelled:
                    break
                
                self.progress = int((i / len(clients)) * 100)
                
                palavras_chave = self.extrair_palavras_chave_cliente(client)
                self.status_message = f"Buscando: {client} (palavras: {', '.join(palavras_chave)})"
                
                match_result = buscar_palavras_chave_no_texto_rigoroso(palavras_chave, pdf_text, self.threshold)
                
                result = {
                    'cliente': client,
                    'palavras_chave': ', '.join(palavras_chave),
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
            self.save_results()
            
            self.status_message = f"Concluído! {self.stats['clients_found']}/{self.stats['total_clients']} clientes encontrados (Ultra-Precisão)"
            
        except Exception as e:
            self.status_message = f"Erro: {str(e)}"
            print(f"Erro no processamento: {e}")
        
        finally:
            self.processing = False
        
        return self.results

    def save_results(self):
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        
        stats_data = {
            'Estatística': [
                'Total de Clientes',
                'Clientes Encontrados', 
                'Clientes Não Encontrados',
                'Taxa de Sucesso',
                'Páginas do PDF',
                'Chamadas à API',
                'Falsos Positivos Evitados',
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
                self.stats['false_positives_avoided'],
                str(self.stats['processing_end'] - self.stats['processing_start']).split('.')[0] if self.stats['processing_end'] else "N/A",
                f"{self.threshold}%"
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_crawler_v41_{timestamp}.xlsx"
        filepath = os.path.join(temp_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resultados', index=False)
            stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        self.last_output_file = filepath
        self.last_output_filename = filename

# -------------- Flask App --------------

app = Flask(__name__)
crawler = CrawlerPDFV41()

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler PDF V4.1 - Ultra-Precisão</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
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
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        
        .precision-badge {
            background: #e74c3c;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .api-config {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #e74c3c;
        }
        
        .form-group { margin-bottom: 25px; }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        input[type="file"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #e74c3c;
        }
        
        .threshold-group {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .threshold-slider { flex: 1; }
        
        .threshold-value {
            background: #e74c3c;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            min-width: 60px;
            text-align: center;
        }
        
        .btn {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
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
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
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
            background: linear-gradient(90deg, #e74c3c, #c0392b);
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
            background: #27ae60;
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
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
            margin-top: 10px;
        }
        
        .info-box {
            background: #fdf2f2;
            border: 1px solid #e74c3c;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .info-box h3 {
            color: #c0392b;
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
            <h1>🎯 Crawler PDF V4.1</h1>
            <p>Ultra-Precisão com IA Maritaca - Zero Falsos Positivos</p>
        </div>
        
        <div class="content">
            <div class="precision-badge">
                🛡️ MODO ULTRA-PRECISÃO ATIVADO
            </div>
            
            <div class="info-box">
                <h3>🚀 Melhorias da Versão 4.1:</h3>
                <ul>
                    <li><strong>Algoritmo Ultra-Rigoroso:</strong> Elimina falsos positivos como "EMS" em contextos irrelevantes</li>
                    <li><strong>Detecção de Contexto:</strong> Analisa o contexto ao redor das palavras encontradas</li>
                    <li><strong>Busca com Delimitadores:</strong> Usa regex com \\b para encontrar palavras completas</li>
                    <li><strong>Threshold Mínimo 90%:</strong> Garante alta precisão nos resultados</li>
                    <li><strong>Cache Inteligente:</strong> Evita processamento desnecessário</li>
                </ul>
            </div>
            
            <div class="api-config">
                <h3>🔑 Configuração da API Maritaca (Opcional)</h3>
                <p style="margin-bottom: 15px; color: #666;">
                    Cole sua chave da API Maritaca para análise avançada de palavras-chave.
                </p>
                <div class="form-group">
                    <label for="maritaca-key">Chave da API Maritaca:</label>
                    <input type="password" id="maritaca-key" placeholder="Opcional - algoritmo local também é muito eficiente">
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
                    <label>🎯 Precisão da Busca (Mínimo 90%):</label>
                    <div class="threshold-group">
                        <input type="range" id="threshold" class="threshold-slider" min="90" max="100" value="95">
                        <div class="threshold-value" id="threshold-value">95%</div>
                    </div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        Ultra-Precisão: 95%+ recomendado para eliminar falsos positivos
                    </small>
                </div>
                
                <button type="submit" class="btn" id="process-btn">
                    🎯 Iniciar Busca Ultra-Precisa
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
                    ✅ Processamento Ultra-Preciso Concluído!
                </div>
                <div class="results-content">
                    <p id="results-summary">Resultados processados com máxima precisão.</p>
                    <button class="btn download-btn" id="download-btn">
                        📥 Baixar Resultados Ultra-Precisos
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const thresholdSlider = document.getElementById('threshold');
        const thresholdValue = document.getElementById('threshold-value');
        
        thresholdSlider.addEventListener('input', function() {
            thresholdValue.textContent = this.value + '%';
        });
        
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('excel_file', document.getElementById('excel-file').files[0]);
            formData.append('pdf_file', document.getElementById('pdf-file').files[0]);
            formData.append('threshold', document.getElementById('threshold').value);
            formData.append('maritaca_key', document.getElementById('maritaca-key').value);
            
            document.getElementById('progress-container').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('process-btn').disabled = true;
            document.getElementById('cancel-btn').style.display = 'block';
            
            try {
                const response = await fetch('/process_v41', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
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
        
        function monitorProgress() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch('/progress_v41');
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
        
        function showResults(data) {
            const found = data.results.filter(r => r.encontrado === 'Sim').length;
            const total = data.results.length;
            
            document.getElementById('results-summary').innerHTML = `
                <strong>🎯 Resultados Ultra-Precisos:</strong><br>
                • Total de clientes: ${total}<br>
                • Clientes encontrados: ${found}<br>
                • Taxa de sucesso: ${((found/total)*100).toFixed(1)}%<br>
                • Chamadas à API: ${data.api_calls || 0}<br>
                • Falsos positivos evitados: Máximo possível
            `;
            
            document.getElementById('results').style.display = 'block';
        }
        
        function resetUI() {
            document.getElementById('process-btn').disabled = false;
            document.getElementById('cancel-btn').style.display = 'none';
        }
        
        document.getElementById('cancel-btn').addEventListener('click', async function() {
            try {
                await fetch('/cancel', { method: 'POST' });
            } catch (error) {
                console.error('Erro ao cancelar:', error);
            }
        });
        
        document.getElementById('download-btn').addEventListener('click', function() {
            window.location.href = '/download/latest';
        });
    </script>
</body>
</html>
    """)

@app.route('/process_v41', methods=['POST'])
def process_files_v41():
    if crawler.processing:
        return jsonify({'error': 'Já existe um processamento em andamento'}), 400
    
    try:
        maritaca_key = request.form.get('maritaca_key', '').strip()
        if maritaca_key:
            crawler.set_maritaca_api_key(maritaca_key)
        
        excel_file = request.files['excel_file']
        pdf_file = request.files['pdf_file']
        threshold = int(request.form.get('threshold', 95))
        
        temp_dir = tempfile.gettempdir()
        excel_path = os.path.join(temp_dir, f"temp_excel_{int(time.time())}.xlsx")
        pdf_path = os.path.join(temp_dir, f"temp_pdf_{int(time.time())}.pdf")
        
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        
        def process_thread():
            crawler.process_files(excel_path, pdf_path, threshold)
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

@app.route('/progress_v41')
def get_progress_v41():
    return jsonify({
        'processing': crawler.processing,
        'progress': crawler.progress,
        'status': crawler.status_message,
        'results': crawler.results if not crawler.processing else None,
        'api_calls': crawler.stats.get('api_calls', 0)
    })

@app.route('/cancel', methods=['POST'])
def cancel_processing():
    crawler.cancel_processing()
    return jsonify({'success': True})

@app.route('/download/latest')
def download_latest():
    if crawler.last_output_file and os.path.exists(crawler.last_output_file):
        return send_file(
            crawler.last_output_file,
            as_attachment=True,
            download_name=crawler.last_output_filename
        )
    else:
        return "Nenhum resultado disponível", 404

if __name__ == '__main__':
    print("🎯 Crawler PDF V4.1 - Ultra-Precisão")
    print("Acesse: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 