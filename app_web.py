#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Web para o Crawler de Clientes em PDF
==================================================

Interface web usando Flask para facilitar o uso do crawler.
Compatível com qualquer sistema operacional.

Autor: Assistant AI
Data: 2024
"""

from flask import Flask, render_template_string, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
from datetime import datetime
import threading
import json
from werkzeug.utils import secure_filename
from crawler_advanced import PDFClientCrawler

app = Flask(__name__)
app.secret_key = 'crawler_pdf_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo

# Configurações
UPLOAD_FOLDER = 'temp_uploads'
RESULTS_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf'}

# Criar pastas se não existirem
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Status global do processamento
processing_status = {
    'is_processing': False,
    'progress': 0,
    'message': 'Aguardando...',
    'results': None,
    'log': []
}

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_message(message):
    """Adiciona mensagem ao log."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    processing_status['log'].append(log_entry)
    # Manter apenas as últimas 100 mensagens
    if len(processing_status['log']) > 100:
        processing_status['log'] = processing_status['log'][-100:]

class WebCrawler(PDFClientCrawler):
    """Versão customizada do crawler para interface web."""
    
    def __init__(self, threshold=80, verbose=True):
        super().__init__(threshold, verbose)
    
    def log(self, message):
        """Override do log para enviar para a interface web."""
        log_message(message)
        print(message)  # Manter log no console também

# Template HTML principal
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Crawler de Clientes em PDF</title>
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
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        .form-group input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px dashed #ddd;
            border-radius: 8px;
            background: #f9f9f9;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .form-group input[type="file"]:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .form-group input[type="range"] {
            width: 100%;
            margin: 10px 0;
        }
        
        .form-group input[type="number"] {
            width: 80px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
        }
        
        .range-display {
            text-align: center;
            margin-top: 10px;
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .advanced-options {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .advanced-options h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .options-row {
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .status-panel {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .status-panel.active {
            display: block;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .log-area {
            background: #1a1a1a;
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            margin-top: 15px;
        }
        
        .results-panel {
            background: #e8f5e8;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .results-panel.active {
            display: block;
        }
        
        .results-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .download-btn {
            background: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 12px 25px;
            border-radius: 8px;
            display: inline-block;
            margin-top: 15px;
            transition: all 0.3s ease;
        }
        
        .download-btn:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        
        .help-section {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .help-section h3 {
            color: #856404;
            margin-bottom: 15px;
        }
        
        .help-section ul {
            color: #856404;
            padding-left: 20px;
        }
        
        .help-section li {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Crawler de Clientes em PDF</h1>
            <p>Busque nomes de clientes do Excel em documentos PDF com inteligência artificial</p>
        </div>
        
        <div class="content">
            <form id="crawlerForm" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="excel_file">📊 Arquivo Excel (.xlsx):</label>
                    <input type="file" id="excel_file" name="excel_file" accept=".xlsx,.xls" required>
                    <small style="color: #666;">Selecione o arquivo Excel com a lista de clientes</small>
                </div>
                
                <div class="form-group">
                    <label for="pdf_file">📄 Arquivo PDF:</label>
                    <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required>
                    <small style="color: #666;">Selecione o arquivo PDF onde buscar os clientes</small>
                </div>
                
                <div class="advanced-options">
                    <h3>🔧 Configurações Avançadas</h3>
                    
                    <div class="form-group">
                        <label for="threshold">🎯 Tolerância de Similaridade:</label>
                        <input type="range" id="threshold" name="threshold" min="50" max="100" value="80" oninput="updateThreshold(this.value)">
                        <div class="range-display" id="thresholdDisplay">80%</div>
                        <small style="color: #666;">70-90% recomendado para a maioria dos casos</small>
                    </div>
                    
                    <div class="options-row">
                        <div>
                            <label for="excel_column">📊 Coluna do Excel (0=primeira):</label>
                            <input type="number" id="excel_column" name="excel_column" min="0" max="50" value="0">
                        </div>
                        <div>
                            <label for="excel_sheet">📋 Aba do Excel (0=primeira):</label>
                            <input type="number" id="excel_sheet" name="excel_sheet" min="0" max="20" value="0">
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    🚀 INICIAR PROCESSAMENTO
                </button>
            </form>
            
            <!-- Painel de Status -->
            <div class="status-panel" id="statusPanel">
                <h3>📊 Status do Processamento</h3>
                <div id="statusMessage">Aguardando...</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="log-area" id="logArea"></div>
            </div>
            
            <!-- Painel de Resultados -->
            <div class="results-panel" id="resultsPanel">
                <h3>📈 Resultados do Processamento</h3>
                <div class="results-stats" id="resultsStats"></div>
                <div id="downloadSection"></div>
            </div>
            
            <!-- Seção de Ajuda -->
            <div class="help-section">
                <h3>💡 Dicas de Uso</h3>
                <ul>
                    <li><strong>Tolerância 70-80%:</strong> Recomendado para dados com variações</li>
                    <li><strong>Tolerância 85-95%:</strong> Para dados muito limpos e precisos</li>
                    <li><strong>PDFs com texto selecionável:</strong> Funcionam melhor que PDFs escaneados</li>
                    <li><strong>Primeira coluna:</strong> Por padrão, o sistema lê a primeira coluna do Excel</li>
                    <li><strong>Teste pequeno:</strong> Teste com poucos clientes primeiro</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        function updateThreshold(value) {
            document.getElementById('thresholdDisplay').textContent = value + '%';
        }
        
        document.getElementById('crawlerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            startProcessing();
        });
        
        function startProcessing() {
            const formData = new FormData(document.getElementById('crawlerForm'));
            const submitBtn = document.getElementById('submitBtn');
            const statusPanel = document.getElementById('statusPanel');
            const resultsPanel = document.getElementById('resultsPanel');
            
            // Validar arquivos
            const excelFile = document.getElementById('excel_file').files[0];
            const pdfFile = document.getElementById('pdf_file').files[0];
            
            if (!excelFile || !pdfFile) {
                alert('Por favor, selecione ambos os arquivos (Excel e PDF).');
                return;
            }
            
            // Desabilitar botão e mostrar status
            submitBtn.disabled = true;
            submitBtn.textContent = '🔄 Processando...';
            statusPanel.classList.add('active');
            resultsPanel.classList.remove('active');
            
            // Limpar log
            document.getElementById('logArea').innerHTML = '';
            
            // Fazer upload e processar
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLogMessage('✅ Upload realizado com sucesso!');
                } else {
                    addLogMessage('❌ Erro: ' + data.message);
                    alert('Erro no processamento: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                addLogMessage('❌ Erro de conexão: ' + error.message);
                alert('Erro de conexão. Verifique se o servidor está rodando.');
            })
            .finally(() => {
                // Reabilitar botão apenas quando terminar o processamento
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 INICIAR PROCESSAMENTO';
                }, 3000);
            });
            
            // Iniciar monitoramento do progresso
            monitorProgress();
        }
        
        function monitorProgress() {
            const interval = setInterval(() => {
                fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data);
                    
                    // Verificar se terminou
                    if (!data.is_processing && data.results) {
                        showResults(data.results);
                        clearInterval(interval);
                    } else if (!data.is_processing) {
                        clearInterval(interval);
                    }
                })
                .catch(error => {
                    console.error('Erro ao monitorar progresso:', error);
                    clearInterval(interval);
                });
            }, 1000);
        }
        
        function updateStatus(data) {
            document.getElementById('statusMessage').textContent = data.message;
            document.getElementById('progressFill').style.width = data.progress + '%';
            
            // Atualizar log
            const logArea = document.getElementById('logArea');
            if (data.log && data.log.length > 0) {
                logArea.innerHTML = data.log.join('\\n');
                logArea.scrollTop = logArea.scrollHeight;
            }
        }
        
        function addLogMessage(message) {
            const logArea = document.getElementById('logArea');
            const timestamp = new Date().toLocaleTimeString();
            logArea.innerHTML += `[${timestamp}] ${message}\\n`;
            logArea.scrollTop = logArea.scrollHeight;
        }
        
        function showResults(results) {
            const resultsPanel = document.getElementById('resultsPanel');
            const resultsStats = document.getElementById('resultsStats');
            const downloadSection = document.getElementById('downloadSection');
            
            // Mostrar estatísticas
            resultsStats.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${results.total_clients}</div>
                    <div class="stat-label">Total de Clientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${results.found_clients}</div>
                    <div class="stat-label">Encontrados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${results.not_found_clients}</div>
                    <div class="stat-label">Não Encontrados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${results.success_rate.toFixed(1)}%</div>
                    <div class="stat-label">Taxa de Sucesso</div>
                </div>
            `;
            
            // Mostrar link de download
            downloadSection.innerHTML = `
                <p><strong>Arquivo de resultados gerado:</strong></p>
                <a href="/download/${results.filename}" class="download-btn">
                    📥 Baixar Resultados (Excel)
                </a>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    O arquivo contém duas abas: "Resultados" com os dados e "Metadados" com estatísticas.
                </p>
            `;
            
            resultsPanel.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_files():
    """Processa os arquivos enviados."""
    try:
        # Verificar arquivos
        if 'excel_file' not in request.files or 'pdf_file' not in request.files:
            return jsonify({'success': False, 'message': 'Arquivos não enviados'})
        
        excel_file = request.files['excel_file']
        pdf_file = request.files['pdf_file']
        
        if excel_file.filename == '' or pdf_file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
        
        if not (allowed_file(excel_file.filename) and allowed_file(pdf_file.filename)):
            return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'})
        
        # Salvar arquivos temporários
        excel_filename = secure_filename(excel_file.filename)
        pdf_filename = secure_filename(pdf_file.filename)
        
        excel_path = os.path.join(UPLOAD_FOLDER, excel_filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        
        # Obter parâmetros
        threshold = int(request.form.get('threshold', 80))
        excel_column = int(request.form.get('excel_column', 0))
        excel_sheet = int(request.form.get('excel_sheet', 0))
        
        # Iniciar processamento em thread separada
        thread = threading.Thread(target=process_in_background, args=(
            excel_path, pdf_path, threshold, excel_column, excel_sheet
        ))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Processamento iniciado'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def process_in_background(excel_path, pdf_path, threshold, excel_column, excel_sheet):
    """Processa os arquivos em background."""
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['progress'] = 0
        processing_status['message'] = 'Iniciando processamento...'
        processing_status['log'] = []
        
        # Gerar nome do arquivo de saída
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"resultados_crawler_{timestamp}.xlsx"
        output_path = os.path.join(RESULTS_FOLDER, output_filename)
        
        # Criar crawler
        crawler = WebCrawler(threshold=threshold, verbose=True)
        
        processing_status['progress'] = 10
        processing_status['message'] = 'Lendo arquivos...'
        
        # Processar
        stats = crawler.process_files(
            excel_path=excel_path,
            pdf_path=pdf_path,
            output_path=output_path,
            excel_column=excel_column,
            excel_sheet=excel_sheet
        )
        
        processing_status['progress'] = 90
        processing_status['message'] = 'Finalizando...'
        
        if stats:
            stats['filename'] = output_filename
            processing_status['results'] = stats
            processing_status['message'] = 'Processamento concluído!'
            log_message('✅ Processamento concluído com sucesso!')
        else:
            processing_status['message'] = 'Erro no processamento'
            log_message('❌ Erro no processamento.')
        
        processing_status['progress'] = 100
        
    except Exception as e:
        processing_status['message'] = f'Erro: {str(e)}'
        log_message(f'❌ Erro: {str(e)}')
    
    finally:
        processing_status['is_processing'] = False
        
        # Limpar arquivos temporários
        try:
            if os.path.exists(excel_path):
                os.remove(excel_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except:
            pass

@app.route('/status')
def get_status():
    """Retorna o status atual do processamento."""
    return jsonify(processing_status)

@app.route('/download/<filename>')
def download_file(filename):
    """Permite download do arquivo de resultados."""
    try:
        file_path = os.path.join(RESULTS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return f"Erro ao baixar arquivo: {str(e)}", 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor web do Crawler de Clientes em PDF...")
    print("📱 Acesse: http://localhost:5000")
    print("🛑 Para parar: Ctrl+C")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 