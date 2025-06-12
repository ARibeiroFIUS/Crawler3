#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler PDF - Versão Web para Deploy
====================================
Versão otimizada para rodar em servidores como Heroku
"""

import os
import tempfile
import shutil
from datetime import datetime
import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz
from flask import Flask, render_template_string, request, jsonify, send_file
import threading
import re

class CrawlerPDFWeb:
    def __init__(self):
        self.threshold = 80
        self.results = []
        self.processing = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.last_output_file = None
        self.last_output_filename = None
        
    def read_excel_clients(self, excel_path):
        """Lê clientes do arquivo Excel."""
        try:
            print(f"📊 Lendo Excel: {excel_path}")
            df = pd.read_excel(excel_path)
            
            if df.empty:
                return []
            
            clients = df.iloc[:, 0].dropna().astype(str).tolist()
            clients = [client.strip() for client in clients if client.strip()]
            
            print(f"📊 {len(clients)} clientes encontrados")
            for i, client in enumerate(clients):
                if 'ems' in client.lower():
                    print(f"📊 *** EMS encontrado: '{client}' ***")
            
            return clients
            
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {e}")
            return []
    
    def read_pdf_text(self, pdf_path):
        """Lê texto do PDF."""
        try:
            print(f"📄 Lendo PDF: {pdf_path}")
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"📄 PDF tem {len(reader.pages)} páginas")
                
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    print(f"📄 Página {i+1}: {len(page_text)} caracteres")
                    
                    if 'ems' in page_text.lower():
                        print(f"📄 *** EMS encontrado na página {i+1}! ***")
                    
                    text += page_text + "\n"
            
            print(f"📄 Total: {len(text)} caracteres extraídos")
            
            if 'ems' in text.lower():
                print("📄 *** EMS encontrado no texto completo! ***")
            else:
                print("📄 EMS não encontrado no texto")
                
            return text
            
        except Exception as e:
            print(f"❌ Erro ao ler PDF: {e}")
            return ""
    
    def find_matches(self, client_list, pdf_text):
        """Busca correspondências com algoritmos melhorados."""
        results = []
        pdf_lower = pdf_text.lower()
        total = len(client_list)
        
        # Pré-processar PDF
        pdf_clean = re.sub(r'[^\w\s]', ' ', pdf_lower)
        pdf_spaces = re.sub(r'\s+', ' ', pdf_clean)
        pdf_words = set(pdf_spaces.split())
        
        print(f"🔍 Processando {total} clientes contra PDF com {len(pdf_words)} palavras únicas")
        
        for i, client in enumerate(client_list):
            if not client:
                continue
                
            client_original = str(client).strip()
            client_lower = client_original.lower()
            
            # Pré-processar cliente
            client_clean = re.sub(r'[^\w\s]', ' ', client_lower)
            client_spaces = re.sub(r'\s+', ' ', client_clean).strip()
            client_words = client_spaces.split()
            
            # Algoritmos de busca
            exact_match = client_lower in pdf_lower
            clean_match = client_spaces in pdf_spaces
            
            # Busca por palavras
            word_matches = []
            for word in client_words:
                if len(word) >= 2 and word in pdf_words:
                    word_matches.append(word)
            
            # Busca flexível
            flexible_matches = []
            for word in client_words:
                if len(word) >= 3:
                    variations = [
                        word,
                        word.replace('.', ''),
                        word.replace('s.a.', 'sa'),
                        word.replace('ltda', ''),
                    ]
                    
                    for variation in variations:
                        if variation and variation in pdf_lower:
                            flexible_matches.append(f"{word}→{variation}")
                            break
            
            # Busca fuzzy
            similarity_partial = fuzz.partial_ratio(client_lower, pdf_lower)
            similarity_token = fuzz.token_sort_ratio(client_lower, pdf_lower)
            similarity_set = fuzz.token_set_ratio(client_lower, pdf_lower)
            
            best_similarity = max(similarity_partial, similarity_token, similarity_set)
            
            # Determinar correspondência
            found = False
            match_type = "N/A"
            
            if exact_match:
                found = True
                match_type = "Exata"
            elif clean_match:
                found = True
                match_type = "Sem pontuação"
            elif len(word_matches) > 0 and len(word_matches) / len(client_words) >= 0.5:
                found = True
                match_type = f"Palavras ({len(word_matches)}/{len(client_words)})"
            elif len(flexible_matches) > 0:
                found = True
                match_type = "Flexível"
            elif best_similarity >= self.threshold:
                found = True
                match_type = f"Fuzzy ({best_similarity}%)"
            
            # Debug para EMS
            if "ems" in client_lower:
                print(f"🔍 EMS DEBUG: '{client_original}' -> {found} ({match_type})")
                print(f"   Palavras: {word_matches}")
                print(f"   Flexível: {flexible_matches}")
                print(f"   Similaridade: {best_similarity}%")
            
            results.append({
                "cliente": client_original,
                "encontrado": "Sim" if found else "Não",
                "similaridade": f"{best_similarity}%",
                "tipo": match_type,
                "palavras_encontradas": ', '.join(word_matches) if word_matches else "Nenhuma"
            })
            
            # Atualizar progresso
            self.progress = int((i + 1) / total * 100)
            self.status_message = f"Processando cliente {i + 1} de {total}..."
        
        return results
    
    def process_files(self, excel_path, pdf_path, threshold):
        """Processa os arquivos."""
        print(f"🚀 Iniciando processamento com threshold={threshold}")
        self.processing = True
        self.progress = 0
        self.threshold = threshold
        
        try:
            # Ler Excel
            self.status_message = "Lendo arquivo Excel..."
            clients = self.read_excel_clients(excel_path)
            
            if not clients:
                self.status_message = "❌ Nenhum cliente encontrado no Excel"
                self.processing = False
                return None
            
            # Ler PDF
            self.status_message = f"📊 {len(clients)} clientes carregados. Lendo PDF..."
            pdf_text = self.read_pdf_text(pdf_path)
            
            if not pdf_text:
                self.status_message = "❌ Não foi possível ler o PDF"
                self.processing = False
                return None
            
            # Buscar correspondências
            self.status_message = "🔍 Buscando correspondências..."
            results = self.find_matches(clients, pdf_text)
            
            # Salvar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"resultados_crawler_{timestamp}.xlsx"
            
            # Para servidores online, usar diretório temporário
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
            print(f"💾 Salvando em: {output_path}")
            
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False)
            
            self.last_output_file = output_path
            self.last_output_filename = output_filename
            
            found_count = sum(1 for r in results if r['encontrado'] == 'Sim')
            self.status_message = f"✅ Concluído! {found_count}/{len(results)} clientes encontrados"
            self.results = results
            self.processing = False
            
            print(f"✅ Processamento concluído: {found_count}/{len(results)} encontrados")
            
            return {
                'success': True,
                'total': len(results),
                'found': found_count,
                'file': output_filename,
                'results': results
            }
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            self.status_message = f"❌ Erro: {str(e)}"
            self.processing = False
            return None

# Instância global do crawler
crawler = CrawlerPDFWeb()

# Criar aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'crawler_pdf_secret_key')

# Template HTML otimizado
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler PDF Online</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input[type="file"] { width: 100%; padding: 12px; border: 2px dashed #ddd; border-radius: 8px; background: #f9f9f9; }
        .tolerance-group { display: flex; align-items: center; gap: 15px; }
        .tolerance-slider { flex: 1; }
        .tolerance-value { font-weight: bold; color: #667eea; min-width: 40px; }
        .btn { padding: 15px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5a6fd8; transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .progress-section { display: none; }
        .progress-bar { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 15px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.3s; }
        .results-section { display: none; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .stat-number { font-size: 24px; font-weight: bold; color: #667eea; }
        .download-btn { background: #28a745; color: white; }
        .download-btn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Crawler PDF Online</h1>
            <p>Busque clientes do Excel em documentos PDF</p>
        </div>

        <div class="card">
            <form id="crawlerForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="excelFile">📊 Arquivo Excel com clientes:</label>
                    <input type="file" id="excelFile" name="excelFile" accept=".xlsx,.xls" required>
                </div>

                <div class="form-group">
                    <label for="pdfFile">📄 Arquivo PDF para busca:</label>
                    <input type="file" id="pdfFile" name="pdfFile" accept=".pdf" required>
                </div>

                <div class="form-group">
                    <label>🎯 Tolerância de Similaridade:</label>
                    <div class="tolerance-group">
                        <input type="range" id="tolerance" name="tolerance" min="50" max="100" value="80" class="tolerance-slider">
                        <span id="toleranceValue" class="tolerance-value">80%</span>
                    </div>
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
            <p id="statusMessage">Iniciando processamento...</p>
        </div>

        <div class="card results-section" id="resultsSection">
            <h3>📊 Resultados</h3>
            <div class="stats" id="resultsStats"></div>
            <button class="btn download-btn" id="downloadBtn">
                💾 Baixar Resultados
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
        const toleranceSlider = document.getElementById('tolerance');
        const toleranceValue = document.getElementById('toleranceValue');
        
        let currentResultFile = null;
        
        toleranceSlider.addEventListener('input', function() {
            toleranceValue.textContent = this.value + '%';
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            progressSection.style.display = 'block';
            resultsSection.style.display = 'none';
            processBtn.disabled = true;
            
            try {
                const response = await fetch('/process', {
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
                const response = await fetch('/progress');
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
                    <div class="stat-number">${((results.found / results.total) * 100).toFixed(1)}%</div>
                    <div class="stat-label">Taxa de Sucesso</div>
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
        print("📤 Recebida requisição de processamento")
        
        excel_file = request.files.get('excelFile')
        pdf_file = request.files.get('pdfFile')
        tolerance = request.form.get('tolerance')
        
        if not excel_file or not pdf_file:
            return jsonify({'success': False, 'error': 'Arquivos não enviados'}), 400
        
        threshold = int(tolerance)
        
        # Salvar arquivos temporários
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, f"excel_{excel_file.filename}")
        pdf_path = os.path.join(temp_dir, f"pdf_{pdf_file.filename}")
        
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        
        print(f"📁 Arquivos salvos: Excel={os.path.getsize(excel_path)}b, PDF={os.path.getsize(pdf_path)}b")
        
        # Processar em thread separada
        def process_thread():
            result = crawler.process_files(excel_path, pdf_path, threshold)
            # Limpar arquivos temporários
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro na rota /process: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/progress')
def get_progress():
    """Retorna o progresso atual."""
    if not crawler.processing and crawler.results:
        found_count = sum(1 for r in crawler.results if r['encontrado'] == 'Sim')
        
        return jsonify({
            'processing': False,
            'progress': 100,
            'status': crawler.status_message,
            'results': {
                'total': len(crawler.results),
                'found': found_count,
                'file': crawler.last_output_filename or f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        })
    else:
        return jsonify({
            'processing': crawler.processing,
            'progress': crawler.progress,
            'status': crawler.status_message
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download do arquivo de resultados."""
    try:
        if crawler.last_output_file and os.path.exists(crawler.last_output_file):
            return send_file(crawler.last_output_file, as_attachment=True, download_name=filename)
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return f"Erro ao baixar: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 