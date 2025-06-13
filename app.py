#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler PDF V3.0 - Matching Robusto para QGC
=============================================
Versão com normalização pesada e fuzzy matching otimizado
"""

import os
import tempfile
import shutil
import hashlib
import json
import time
from datetime import datetime
import pandas as pd
import PyPDF2
import unidecode
from rapidfuzz import fuzz
from flask import Flask, render_template_string, request, jsonify, send_file
import threading
import re

# ----------- Funções de Normalização e Aliases -----------

COMMON_WORDS = {
    'sa', 's.a', 'ltda', 'eireli', 'me', 'empresa', 'cia', 'inc', 'corp', 'co', 
    'do', 'da', 'de', 'dos', 'das', 'e', 'em', 'com', 'para', 'por', 'a', 'o', 'as', 'os',
    'the', 'and', 'or', 'of', 'in', 'to', 'for', 'at', 'by', 'with'
}

def normalize_name(name):
    """Remove acentos, pontuação e termos muito genéricos, mas preserva palavras importantes"""
    if not name or not isinstance(name, str):
        return ""
    
    name = unidecode.unidecode(name)  # Remove acentos
    name = name.lower()
    name = re.sub(r'[^\w\s]', ' ', name)  # Remove pontuação, substitui por espaço
    name = re.sub(r'\s+', ' ', name).strip()  # Normaliza espaços
    
    # Remove apenas palavras muito genéticas e curtas
    words = []
    for word in name.split():
        if len(word) >= 3 and word not in COMMON_WORDS:
            words.append(word)
    
    return ' '.join(words)

def match_client_in_text(client_name, text, min_threshold=80):
    """Busca nomes de empresas completos com tolerância para variações."""
    text_normalized = normalize_name(text)
    client_normalized = normalize_name(client_name)
    
    if not client_normalized or len(client_normalized) < 3:
        return {
            'found': False,
            'confidence': 0,
            'alias': client_normalized,
            'context': 'Nome muito curto após normalização'
        }
    
    client_words = client_normalized.split()
    melhor_score = 0
    melhor_alias = ''
    melhor_contexto = ''
    
    # Estratégia 1: Nome completo com variações de pontuação/formatação
    # Criar variações do nome original para lidar com S.A./S/A, etc.
    original_lower = client_name.lower()
    variações_nome = [
        client_normalized,
        original_lower,
        original_lower.replace('s.a.', 'sa').replace('s/a', 'sa').replace('s.a', 'sa'),
        original_lower.replace('ltda.', 'ltda').replace('limitada', 'ltda'),
        # Remover preposições opcionais
        client_normalized.replace(' do ', ' ').replace(' da ', ' ').replace(' de ', ' '),
        # Versão sem espaços para casos extremos
        client_normalized.replace(' ', '')
    ]
    
    # Testar cada variação
    for variacao in variações_nome:
        if not variacao or len(variacao) < 3:
            continue
            
        # Usar partial_ratio para encontrar a variação dentro do texto
        score = fuzz.partial_ratio(variacao, text_normalized)
        
        if score > melhor_score:
            melhor_score = score
            melhor_alias = variacao
            
            # Encontrar contexto
            idx = text_normalized.find(variacao)
            if idx >= 0:
                start = max(0, idx-50)
                end = min(len(text), idx+len(variacao)+50)
                melhor_contexto = text[start:end]
    
    # Estratégia 2: Para nomes longos, testar sem algumas palavras menos importantes
    if len(client_words) >= 3:
        # Testar removendo uma palavra por vez (exceto a primeira)
        for i in range(1, len(client_words)):
            palavras_sem_uma = client_words[:i] + client_words[i+1:]
            variacao = ' '.join(palavras_sem_uma)
            
            if len(variacao) >= 6:  # Manter um mínimo razoável
                score = fuzz.partial_ratio(variacao, text_normalized)
                
                if score > melhor_score:
                    melhor_score = score
                    melhor_alias = variacao
                    
                    idx = text_normalized.find(variacao)
                    if idx >= 0:
                        start = max(0, idx-50)
                        end = min(len(text), idx+len(variacao)+50)
                        melhor_contexto = text[start:end]
    
    # Estratégia 3: Busca por sequências de palavras significativas
    # Para nomes com 2+ palavras, exigir que pelo menos 2 palavras consecutivas sejam encontradas
    if len(client_words) >= 2:
        for i in range(len(client_words) - 1):
            # Testar pares de palavras consecutivas
            par_palavras = ' '.join(client_words[i:i+2])
            if len(par_palavras) >= 6:
                score = fuzz.partial_ratio(par_palavras, text_normalized)
                
                # Bonus se encontrar mais palavras do nome na sequência
                if score >= 85:  # Só considerar se o par já tem boa correspondência
                    # Verificar quantas palavras do nome aparecem na sequência
                    palavras_encontradas = 0
                    for word in client_words:
                        if word in text_normalized:
                            palavras_encontradas += 1
                    
                    # Ajustar score baseado na proporção de palavras encontradas
                    proporcao = palavras_encontradas / len(client_words)
                    score_ajustado = score * (0.7 + 0.3 * proporcao)
                    
                    if score_ajustado > melhor_score:
                        melhor_score = score_ajustado
                        melhor_alias = f"{par_palavras} (+{palavras_encontradas-2} palavras)"
                        
                        idx = text_normalized.find(par_palavras)
                        if idx >= 0:
                            start = max(0, idx-50)
                            end = min(len(text), idx+len(par_palavras)+50)
                            melhor_contexto = text[start:end]
    
    # Critérios para determinar se foi encontrado
    found = False
    
    if len(client_words) == 1:
        # Para uma palavra: só aceitar se for muito específica e com score altíssimo
        if len(client_words[0]) >= 6 and melhor_score >= 98:
            found = True
    elif len(client_words) == 2:
        # Para duas palavras: score alto
        if melhor_score >= 85:
            found = True
    else:
        # Para 3+ palavras: usar threshold, mas com mínimo de 80%
        threshold_adjusted = max(min_threshold, 80)
        if melhor_score >= threshold_adjusted:
            found = True
    
    return {
        'found': found,
        'confidence': int(melhor_score),
        'alias': melhor_alias,
        'context': melhor_contexto.strip()
    }

# -------------- Classe principal --------------

class CrawlerPDFV3:
    def __init__(self):
        self.threshold = 80
        self.results = []
        self.processing = False
        self.cancelled = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.last_output_file = None
        self.last_output_filename = None
        self.stats = {
            'processing_start': None,
            'total_clients': 0,
            'found_clients': 0
        }

    def reset_processing(self):
        self.cancelled = False
        self.processing = False
        self.progress = 0
        self.results = []
        self.status_message = "Pronto para processar"
        self.stats['found_clients'] = 0

    def cancel_processing(self):
        self.cancelled = True
        self.status_message = "❌ Processamento cancelado"
        self.processing = False

    def read_excel_clients(self, excel_path: str):
        df = pd.read_excel(excel_path)
        if df.empty:
            return []
        clients = df.iloc[:, 0].dropna().astype(str).tolist()
        return [client.strip() for client in clients if client.strip()]

    def read_pdf(self, pdf_path: str):
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            for i, page in enumerate(reader.pages):
                self.progress = int((i / total_pages) * 30)  # 0-30% para leitura
                self.status_message = f"📄 Processando página {i+1}/{total_pages}"
                text += page.extract_text() or ""
                if self.cancelled:
                    return None
        return text

    def process_files(self, excel_path, pdf_path, threshold):
        try:
            self.reset_processing()
            self.processing = True
            self.threshold = threshold
            self.stats['processing_start'] = time.time()
            self.status_message = "📊 Lendo arquivo Excel..."
            self.progress = 5
            clients = self.read_excel_clients(excel_path)
            if not clients:
                self.status_message = "❌ Nenhum cliente encontrado"
                self.processing = False
                return None
            self.stats['total_clients'] = len(clients)

            self.status_message = "📄 Processando PDF..."
            self.progress = 10
            pdf_text = self.read_pdf(pdf_path)
            if self.cancelled or not pdf_text:
                return None

            results = []
            for i, client in enumerate(clients):
                if self.cancelled:
                    break
                self.progress = 30 + int((i / len(clients)) * 60)  # 30-90%
                self.status_message = f"🔍 Buscando: {client} ({i+1}/{len(clients)})"
                match_result = match_client_in_text(client, pdf_text, threshold)
                if match_result['found']:
                    self.stats['found_clients'] += 1
                results.append({
                    'cliente': client,
                    'encontrado': 'Sim' if match_result['found'] else 'Não',
                    'confianca': f"{match_result['confidence']}%",
                    'alias_usado': match_result['alias'],
                    'contexto': match_result['context'][:150] + '...' if len(match_result['context']) > 150 else match_result['context']
                })
                time.sleep(0.01)

            if self.cancelled:
                return None

            self.progress = 95
            self.status_message = "💾 Salvando resultados..."
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"crawler_v3_{timestamp}.xlsx"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            df = pd.DataFrame(results)

            stats_data = {
                'Métrica': [
                    'Total de Clientes',
                    'Clientes Encontrados',
                    'Taxa de Sucesso (%)'
                ],
                'Valor': [
                    len(results),
                    self.stats['found_clients'],
                    f"{(self.stats['found_clients'] / len(results) * 100):.1f}%"
                ]
            }
            df_stats = pd.DataFrame(stats_data)

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Resultados', index=False)
                df_stats.to_excel(writer, sheet_name='Estatísticas', index=False)

            self.results = results
            self.processing = False
            self.last_output_file = output_path
            self.last_output_filename = output_filename

            processing_time = time.time() - self.stats['processing_start']
            self.status_message = f"✅ Concluído! {self.stats['found_clients']}/{len(results)} encontrados em {processing_time:.1f}s"
            self.progress = 100

            return {
                'success': True,
                'total': len(results),
                'found': self.stats['found_clients'],
                'file': output_filename,
                'results': results,
                'processing_time': processing_time
            }
        except Exception as e:
            self.status_message = f"❌ Erro: {str(e)}"
            self.processing = False
            return None

# ------------ Flask app ------------

crawler_v3 = CrawlerPDFV3()
app = Flask(__name__)
app.secret_key = 'crawler_v3_secret'

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔍 Crawler PDF V3.0</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                padding: 20px;
            }
            .container { max-width: 800px; margin: 0 auto; }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 30px; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .card { 
                background: white; 
                border-radius: 15px; 
                padding: 30px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                margin-bottom: 20px; 
            }
            .form-group { margin-bottom: 25px; }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #333; 
                font-size: 1.1em;
            }
            input[type="file"] { 
                width: 100%; 
                padding: 15px; 
                border: 2px dashed #ddd; 
                border-radius: 8px; 
                background: #f9f9f9; 
                font-size: 1em;
                transition: border-color 0.3s;
            }
            input[type="file"]:hover { border-color: #667eea; }
            input[type="number"] {
                width: 150px;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1em;
            }
            .btn { 
                padding: 15px 30px; 
                border: none; 
                border-radius: 8px; 
                font-weight: 600; 
                cursor: pointer; 
                transition: all 0.3s; 
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .btn-primary { 
                background: linear-gradient(45deg, #667eea, #764ba2); 
                color: white; 
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-primary:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            .btn:disabled { 
                opacity: 0.6; 
                cursor: not-allowed; 
                transform: none !important;
            }
            .progress-section { 
                display: none; 
                text-align: center;
            }
            .progress-bar { 
                width: 100%; 
                height: 25px; 
                background: #f0f0f0; 
                border-radius: 15px; 
                overflow: hidden; 
                margin: 20px 0; 
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }
            .progress-fill { 
                height: 100%; 
                background: linear-gradient(90deg, #667eea, #764ba2); 
                transition: width 0.3s; 
                border-radius: 15px;
            }
            .status-message {
                font-size: 1.1em;
                color: #333;
                margin: 15px 0;
                font-weight: 500;
            }
            .results-section { 
                display: none; 
            }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 25px 0; 
            }
            .stat-card { 
                text-align: center; 
                padding: 20px; 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                border-radius: 12px; 
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }
            .stat-number { 
                font-size: 2.5em; 
                font-weight: bold; 
                color: #667eea; 
                margin-bottom: 5px;
            }
            .stat-label { 
                color: #666; 
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 0.9em;
            }
            .download-btn { 
                background: linear-gradient(45deg, #28a745, #20c997); 
                color: white; 
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
            }
            .download-btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
            }
            .version-badge {
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-top: 10px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Crawler PDF V3.0</h1>
                <p>Busque clientes do Excel em documentos PDF com IA</p>
                <div class="version-badge">✨ Algoritmo Otimizado com RapidFuzz</div>
            </div>

            <div class="card">
                <form id="crawlerForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="excelFile">📊 Arquivo Excel com lista de clientes:</label>
                        <input type="file" id="excelFile" name="excelFile" accept=".xlsx,.xls" required>
                        <small style="color: #666; margin-top: 5px; display: block;">
                            💡 O sistema lerá a primeira coluna do Excel
                        </small>
                    </div>

                    <div class="form-group">
                        <label for="pdfFile">📄 Arquivo PDF para busca:</label>
                        <input type="file" id="pdfFile" name="pdfFile" accept=".pdf" required>
                        <small style="color: #666; margin-top: 5px; display: block;">
                            💡 Documentos QGC, processos jurídicos, etc.
                        </small>
                    </div>

                    <div class="form-group">
                        <label for="tolerance">🎯 Tolerância de Similaridade:</label>
                        <input type="number" id="tolerance" name="tolerance" min="50" max="100" value="80">
                        <small style="color: #666; margin-left: 10px;">
                            (50-100%) - Recomendado: 80%
                        </small>
                    </div>

                    <button type="submit" id="processBtn" class="btn btn-primary">
                        🚀 Processar Arquivos
                    </button>
                </form>
            </div>

            <div class="card progress-section" id="progressSection">
                <h3>⏳ Processando...</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <div class="status-message" id="statusMessage">Iniciando processamento...</div>
            </div>

            <div class="card results-section" id="resultsSection">
                <h3>📊 Resultados do Processamento</h3>
                <div class="stats" id="resultsStats"></div>
                <button class="btn download-btn" id="downloadBtn">
                    💾 Baixar Planilha de Resultados
                </button>
            </div>
        </div>

        <script>
            const form = document.getElementById('crawlerForm');
            const processBtn = document.getElementById('processBtn');
            const progressSection = document.getElementById('progressSection');
            const resultsSection = document.getElementById('resultsSection');
            const progressFill = document.getElementById('progressFill');
            const statusMessage = document.getElementById('statusMessage');
            
            let currentResultFile = null;
            
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(form);
                
                // Mostrar seção de progresso
                progressSection.style.display = 'block';
                resultsSection.style.display = 'none';
                processBtn.disabled = true;
                processBtn.textContent = '⏳ Processando...';
                
                try {
                    const response = await fetch('/process_v3', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        monitorProgress();
                    } else {
                        throw new Error('Erro no servidor');
                    }
                    
                } catch (error) {
                    alert('Erro: ' + error.message);
                    resetUI();
                }
            });
            
            async function monitorProgress() {
                try {
                    const response = await fetch('/progress_v3');
                    const data = await response.json();
                    
                    progressFill.style.width = data.progress + '%';
                    statusMessage.textContent = data.status;
                    
                    if (data.processing) {
                        setTimeout(monitorProgress, 1000);
                    } else if (data.results) {
                        showResults(data.results);
                    } else {
                        alert('Erro durante processamento');
                        resetUI();
                    }
                    
                } catch (error) {
                    console.error('Erro:', error);
                    setTimeout(monitorProgress, 2000);
                }
            }
            
            function showResults(results) {
                progressSection.style.display = 'none';
                resultsSection.style.display = 'block';
                
                const successRate = ((results.found / results.total) * 100).toFixed(1);
                
                document.getElementById('resultsStats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${results.total}</div>
                        <div class="stat-label">Total de Clientes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${results.found}</div>
                        <div class="stat-label">Encontrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${successRate}%</div>
                        <div class="stat-label">Taxa de Sucesso</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${results.processing_time}s</div>
                        <div class="stat-label">Tempo de Processamento</div>
                    </div>
                `;
                
                currentResultFile = results.file;
                resetUI();
            }
            
            document.getElementById('downloadBtn').addEventListener('click', function() {
                if (currentResultFile) {
                    window.open('/download/' + encodeURIComponent(currentResultFile));
                }
            });
            
            function resetUI() {
                processBtn.disabled = false;
                processBtn.textContent = '🚀 Processar Arquivos';
            }
        </script>
    </body>
    </html>
    """

@app.route('/process_v3', methods=['POST'])
def process_files_v3():
    try:
        excel_file = request.files.get('excelFile')
        pdf_file = request.files.get('pdfFile')
        tolerance = request.form.get('tolerance', 80)
        if not excel_file or not pdf_file:
            return jsonify({'success': False, 'error': 'Arquivos não enviados'}), 400
        threshold = int(tolerance)
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, f"excel_{excel_file.filename}")
        pdf_path = os.path.join(temp_dir, f"pdf_{pdf_file.filename}")
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        def process_thread():
            crawler_v3.process_files(excel_path, pdf_path, threshold)
            shutil.rmtree(temp_dir, ignore_errors=True)
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/progress_v3')
def get_progress_v3():
    if not crawler_v3.processing and crawler_v3.results:
        return jsonify({
            'processing': False,
            'progress': 100,
            'status': crawler_v3.status_message,
            'results': {
                'total': len(crawler_v3.results),
                'found': crawler_v3.stats['found_clients'],
                'file': crawler_v3.last_output_filename,
                'processing_time': f"{time.time() - crawler_v3.stats['processing_start']:.1f}"
            }
        })
    else:
        return jsonify({
            'processing': crawler_v3.processing,
            'progress': crawler_v3.progress,
            'status': crawler_v3.status_message,
            'stats': crawler_v3.stats
        })

@app.route('/cancel', methods=['POST'])
def cancel_processing():
    try:
        crawler_v3.cancel_processing()
        return jsonify({'success': True, 'message': 'Processamento cancelado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        if crawler_v3.last_output_file and os.path.exists(crawler_v3.last_output_file):
            return send_file(crawler_v3.last_output_file, as_attachment=True, download_name=filename)
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return f"Erro ao baixar: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 