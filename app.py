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
        self.cancelled = False
        self.document_type = "processo"  # "qgc" ou "processo"
        
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
        """Busca correspondências com algoritmos otimizados."""
        results = []
        pdf_lower = pdf_text.lower()
        total = len(client_list)
        
        # Normalização extensiva do PDF
        pdf_normalized = pdf_lower
        # Normalizar formatos societários
        pdf_normalized = re.sub(r's\s*/\s*a\b', 'sa', pdf_normalized)
        pdf_normalized = re.sub(r's\s*\.\s*a\s*\.?', 'sa', pdf_normalized)
        pdf_normalized = re.sub(r'ltda\s*\.?', 'ltda', pdf_normalized)
        pdf_normalized = re.sub(r'limitada', 'ltda', pdf_normalized)
        pdf_normalized = re.sub(r'me\b', '', pdf_normalized)
        pdf_normalized = re.sub(r'epp\b', '', pdf_normalized)
        pdf_normalized = re.sub(r'eireli\b', '', pdf_normalized)
        
        # Normalizar palavras comuns
        pdf_normalized = pdf_normalized.replace('comercio', 'com')
        pdf_normalized = pdf_normalized.replace('industria', 'ind')
        pdf_normalized = pdf_normalized.replace('laboratorio', 'lab')
        pdf_normalized = pdf_normalized.replace('farmaceutica', 'farm')
        
        # Remover pontuação e normalizar espaços
        pdf_clean = re.sub(r'[^\w\s]', ' ', pdf_normalized)
        pdf_spaces = re.sub(r'\s+', ' ', pdf_clean).strip()
        pdf_words = set(pdf_spaces.split())
        
        print(f"🔍 Processando {total} clientes contra PDF com {len(pdf_words)} palavras únicas")
        
        for i, client in enumerate(client_list):
            if self.cancelled:
                print("⚠️ Processamento cancelado pelo usuário")
                break
                
            if not client:
                continue
                
            client_original = str(client).strip()
            client_lower = client_original.lower()
            
            # Normalização extensiva do cliente
            client_normalized = client_lower
            client_normalized = re.sub(r's\s*/\s*a\b', 'sa', client_normalized)
            client_normalized = re.sub(r's\s*\.\s*a\s*\.?', 'sa', client_normalized)
            client_normalized = re.sub(r'ltda\s*\.?', 'ltda', client_normalized)
            client_normalized = re.sub(r'limitada', 'ltda', client_normalized)
            client_normalized = re.sub(r'me\b', '', client_normalized)
            client_normalized = re.sub(r'epp\b', '', client_normalized)
            client_normalized = re.sub(r'eireli\b', '', client_normalized)
            
            client_normalized = client_normalized.replace('comercio', 'com')
            client_normalized = client_normalized.replace('industria', 'ind')
            client_normalized = client_normalized.replace('laboratorio', 'lab')
            client_normalized = client_normalized.replace('farmaceutica', 'farm')
            
            # Criar múltiplas variações do nome
            client_variations = [
                client_normalized,
                client_normalized.replace(' do ', ' '),
                client_normalized.replace(' de ', ' '),
                client_normalized.replace(' da ', ' '),
                client_normalized.replace(' dos ', ' '),
                client_normalized.replace(' das ', ' '),
                re.sub(r'\s+(sa|ltda).*$', '', client_normalized),  # Remove sufixos
                re.sub(r'\s+', '', client_normalized),  # Remove todos os espaços
            ]
            
            # Limpar variações vazias e duplicadas
            client_variations = list(set([v.strip() for v in client_variations if v.strip()]))
            
            # Processar palavras do cliente
            client_clean = re.sub(r'[^\w\s]', ' ', client_normalized)
            client_spaces = re.sub(r'\s+', ' ', client_clean).strip()
            client_words = [w for w in client_spaces.split() if len(w) >= 2]
            
            # Busca exata com variações
            exact_match = any(variation in pdf_normalized for variation in client_variations)
            
            # Busca por palavras significativas
            word_matches = []
            significant_words = []
            common_words = {
                'ltda', 'sa', 'cia', 'inc', 'corp', 'limited', 'tech', 'group', 'international', 
                'brasil', 'brazil', 'company', 'solutions', 'services', 'industria', 'comercio', 
                'distribuidora', 'center', 'centre', 'industrias', 'laboratorio', 'farmacia', 
                'saude', 'health', 'medical', 'global', 'nacional', 'do', 'de', 'e', 'com', 
                'para', 'por', 'a', 'o', 'as', 'os', 'das', 'dos', 'em', 'me', 'epp', 'eireli', 
                'mei', 'da', 'no', 'na', 'um', 'uma', 'the', 'and', 'or', 'of', 'in', 'to', 'for'
            }
            
            for word in client_words:
                if len(word) >= 3 and word not in common_words:
                    significant_words.append(word)
                    
                    # Buscar palavra e variações
                    word_variations = [
                        word,
                        word.rstrip('s'),  # Singular
                        word + 's',       # Plural
                        word.replace('z', 's'),
                        word.replace('s', 'z'),
                        word.replace('ç', 'c'),
                        word.replace('c', 'ç'),
                    ]
                    
                    if any(var in pdf_words for var in word_variations if len(var) >= 3):
                        word_matches.append(word)
            
            # Busca fuzzy otimizada
            best_similarity = 0
            for variation in client_variations:
                if len(variation) >= 3:  # Só testar variações válidas
                    similarities = [
                        fuzz.ratio(variation, pdf_normalized),
                        fuzz.partial_ratio(variation, pdf_normalized),
                        fuzz.token_sort_ratio(variation, pdf_normalized),
                        fuzz.token_set_ratio(variation, pdf_normalized)
                    ]
                    best_similarity = max(best_similarity, max(similarities))
            
            # Lógica de decisão otimizada
            found = False
            match_type = "N/A"
            confidence = 0
            
            if exact_match:
                found = True
                match_type = "Exata"
                confidence = 100
            elif len(significant_words) > 0:
                match_ratio = len(word_matches) / len(significant_words)
                
                # Critérios baseados no tamanho do nome
                if len(significant_words) == 1:
                    # Nome com 1 palavra significativa
                    if len(word_matches) >= 1:
                        found = True
                        match_type = "Palavra única"
                        confidence = 90
                elif len(significant_words) == 2:
                    # Nome com 2 palavras significativas
                    if len(word_matches) >= 1:
                        found = True
                        match_type = f"Palavras ({len(word_matches)}/2)"
                        confidence = 80 + (match_ratio * 20)
                else:
                    # Nome com 3+ palavras significativas
                    if match_ratio >= 0.4:  # 40% das palavras
                        found = True
                        match_type = f"Palavras ({len(word_matches)}/{len(significant_words)})"
                        confidence = 60 + (match_ratio * 40)
            
            # Fallback para similaridade fuzzy
            if not found and best_similarity >= max(50, self.threshold - 20):
                threshold_adjusted = 60 if len(client_words) <= 2 else 70
                if best_similarity >= threshold_adjusted:
                    found = True
                    match_type = f"Fuzzy ({best_similarity}%)"
                    confidence = best_similarity
            
            # Debug simplificado (só para casos importantes)
            if not found and any(word in client_normalized for word in ['ems', 'banco', 'brasil']):
                print(f"🔍 DEBUG: '{client_original}' -> NÃO ENCONTRADO")
                print(f"   Variações: {client_variations[:3]}...")
                print(f"   Palavras significativas: {significant_words}")
                print(f"   Palavras encontradas: {word_matches}")
                print(f"   Melhor similaridade: {best_similarity}%")
                print("   ---")
            elif found:
                print(f"✅ ENCONTRADO: '{client_original}' -> {match_type} (confiança: {confidence:.0f}%)")
            
            results.append({
                "cliente": client_original,
                "encontrado": "Sim" if found else "Não",
                "similaridade": f"{best_similarity}%",
                "tipo": match_type,
                "palavras_encontradas": ', '.join(word_matches) if word_matches else "Nenhuma"
            })
            
            self.progress = int((i + 1) / total * 100)
            self.status_message = f"Processando cliente {i + 1} de {total}..."
        
        return results
    
    def cancel_processing(self):
        """Cancela o processamento atual."""
        print("🛑 Cancelamento solicitado")
        self.cancelled = True
        self.status_message = "❌ Processamento cancelado pelo usuário"
        
    def reset_processing(self):
        """Reseta o estado para novo processamento."""
        self.cancelled = False
        self.processing = False
        self.progress = 0
        self.results = []
        self.status_message = "Pronto para processar"
    
    def process_files(self, excel_path, pdf_path, threshold, document_type="processo"):
        """Processa os arquivos."""
        print(f"🚀 Iniciando processamento com threshold={threshold}, tipo={document_type}")
        self.processing = True
        self.cancelled = False  # Reset cancelamento
        self.progress = 0
        self.threshold = threshold
        self.document_type = document_type
        
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
            
            # Processar baseado no tipo de documento
            if document_type == "qgc":
                self.status_message = "📋 Extraindo seção QGC do documento..."
                pdf_text = self.extract_qgc_section(pdf_text)
                print(f"📋 Modo QGC: analisando {len(pdf_text)} caracteres")
            else:
                print(f"📄 Modo Processo Íntegra: analisando {len(pdf_text)} caracteres")
            
            # Buscar correspondências
            self.status_message = "🔍 Buscando correspondências..."
            results = self.find_matches(clients, pdf_text)
            
            # Verificar se foi cancelado durante o processamento
            if self.cancelled:
                self.processing = False
                return None
            
            # Salvar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_type_suffix = "QGC" if document_type == "qgc" else "Processo"
            output_filename = f"resultados_crawler_{doc_type_suffix}_{timestamp}.xlsx"
            
            # Para servidores online, usar diretório temporário
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
            print(f"💾 Salvando em: {output_path}")
            
            # Adicionar informações sobre o tipo de documento nos resultados
            df = pd.DataFrame(results)
            df.insert(0, 'tipo_documento', document_type.upper())
            df.to_excel(output_path, index=False)
            
            self.last_output_file = output_path
            self.last_output_filename = output_filename
            
            found_count = sum(1 for r in results if r['encontrado'] == 'Sim')
            doc_info = f"({document_type.upper()})"
            self.status_message = f"✅ Concluído! {found_count}/{len(results)} clientes encontrados {doc_info}"
            self.results = results
            self.processing = False
            
            print(f"✅ Processamento concluído: {found_count}/{len(results)} encontrados")
            
            return {
                'success': True,
                'total': len(results),
                'found': found_count,
                'file': output_filename,
                'results': results,
                'document_type': document_type
            }
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            self.status_message = f"❌ Erro: {str(e)}"
            self.processing = False
            return None

    def extract_qgc_section(self, pdf_text):
        """Extrai apenas a seção QGC do PDF."""
        try:
            text_lower = pdf_text.lower()
            
            # Padrões para identificar início do QGC
            qgc_patterns = [
                r'quadro\s+geral\s+de\s+cotistas',
                r'qgc',
                r'quadro.*cotistas',
                r'composição\s+societária',
                r'estrutura\s+societária'
            ]
            
            # Padrões para identificar fim do QGC
            end_patterns = [
                r'administração',
                r'diretoria',
                r'conselho',
                r'representação',
                r'objeto\s+social',
                r'atividade\s+principal',
                r'capital\s+social'
            ]
            
            qgc_start = -1
            qgc_end = len(pdf_text)
            
            # Encontrar início do QGC
            for pattern in qgc_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    qgc_start = match.start()
                    print(f"📋 QGC encontrado em: posição {qgc_start} (padrão: {pattern})")
                    break
            
            if qgc_start == -1:
                print("⚠️ Seção QGC não encontrada, analisando documento completo")
                return pdf_text
            
            # Encontrar fim do QGC (procurar a partir do início encontrado)
            text_after_qgc = pdf_text[qgc_start:]
            text_after_qgc_lower = text_after_qgc.lower()
            
            for pattern in end_patterns:
                match = re.search(pattern, text_after_qgc_lower)
                if match:
                    qgc_end = qgc_start + match.start()
                    print(f"📋 Fim do QGC em: posição {qgc_end} (padrão: {pattern})")
                    break
            
            # Extrair seção QGC
            qgc_section = pdf_text[qgc_start:qgc_end]
            
            print(f"📋 QGC extraído: {len(qgc_section)} caracteres (de {len(pdf_text)} total)")
            
            # Se a seção ficou muito pequena, usar documento completo
            if len(qgc_section) < 200:
                print("⚠️ Seção QGC muito pequena, usando documento completo")
                return pdf_text
            
            return qgc_section
            
        except Exception as e:
            print(f"❌ Erro ao extrair QGC: {e}")
            return pdf_text

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
        .btn-cancel { background: #dc3545; color: white; margin-left: 10px; }
        .btn-cancel:hover { background: #c82333; transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .button-group { display: flex; align-items: center; }
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
                    <label>📋 Tipo de Documento:</label>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                            <input type="radio" name="documentType" value="processo" checked>
                            📄 Processo na Íntegra
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                            <input type="radio" name="documentType" value="qgc">
                            📋 Apenas QGC (Quadro Geral de Cotistas)
                        </label>
                    </div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        💡 <strong>QGC:</strong> Busca apenas na seção de cotistas/sócios. <strong>Processo:</strong> Busca em todo o documento.
                    </small>
                </div>

                <div class="form-group">
                    <label>🎯 Tolerância de Similaridade:</label>
                    <div class="tolerance-group">
                        <input type="range" id="tolerance" name="tolerance" min="50" max="100" value="80" class="tolerance-slider">
                        <span id="toleranceValue" class="tolerance-value">80%</span>
                    </div>
                </div>

                <div class="button-group">
                    <button type="submit" id="processBtn" class="btn btn-primary">
                        🚀 Processar Arquivos
                    </button>
                    <button type="button" id="cancelBtn" class="btn btn-cancel" style="display: none;">
                        ⏹️ Cancelar
                    </button>
                </div>
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
        const cancelBtn = document.getElementById('cancelBtn');
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
        
        cancelBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/cancel', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    progressSection.style.display = 'none';
                    resetUI();
                    alert('Processamento cancelado com sucesso!');
                } else {
                    throw new Error('Erro ao cancelar');
                }
            } catch (error) {
                alert('Erro ao cancelar: ' + error.message);
            }
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            progressSection.style.display = 'block';
            resultsSection.style.display = 'none';
            processBtn.disabled = true;
            cancelBtn.style.display = 'inline-block';
            
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
                } else if (data.status && data.status.includes('cancelado')) {
                    // Processamento foi cancelado
                    progressSection.style.display = 'none';
                    resetUI();
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
            cancelBtn.style.display = 'none';
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
        document_type = request.form.get('documentType', 'processo')
        
        if not excel_file or not pdf_file:
            return jsonify({'success': False, 'error': 'Arquivos não enviados'}), 400
        
        threshold = int(tolerance)
        print(f"📋 Tipo de documento selecionado: {document_type}")
        
        # Salvar arquivos temporários
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, f"excel_{excel_file.filename}")
        pdf_path = os.path.join(temp_dir, f"pdf_{pdf_file.filename}")
        
        excel_file.save(excel_path)
        pdf_file.save(pdf_path)
        
        print(f"📁 Arquivos salvos: Excel={os.path.getsize(excel_path)}b, PDF={os.path.getsize(pdf_path)}b")
        
        # Processar em thread separada
        def process_thread():
            result = crawler.process_files(excel_path, pdf_path, threshold, document_type)
            # Limpar arquivos temporários
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro na rota /process: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/cancel', methods=['POST'])
def cancel_processing():
    """Cancela o processamento atual."""
    try:
        crawler.cancel_processing()
        return jsonify({'success': True, 'message': 'Processamento cancelado'})
    except Exception as e:
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