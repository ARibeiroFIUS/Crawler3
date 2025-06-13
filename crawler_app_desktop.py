#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler PDF - Aplicação Desktop
===============================

Aplicação desktop que usa Flask para criar uma interface web
que abre automaticamente no navegador, funcionando como um app desktop.
"""

import os
import sys
import webbrowser
import threading
import time
from datetime import datetime
import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz
from flask import Flask, render_template_string, request, jsonify, send_file
import tempfile
import shutil
from pathlib import Path

class CrawlerPDFDesktop:
    def __init__(self):
        self.threshold = 80
        self.results = []
        self.processing = False
        self.progress = 0
        self.status_message = "Pronto para processar"
        self.last_output_file = None
        self.last_output_filename = None
        
    def read_excel_clients(self, excel_path):
        """Lê clientes do arquivo Excel com debug detalhado."""
        try:
            print(f"🔍 DEBUG EXCEL: Lendo arquivo: {excel_path}")
            df = pd.read_excel(excel_path)
            
            print(f"🔍 DEBUG EXCEL: Excel tem {len(df)} linhas e {len(df.columns)} colunas")
            print(f"🔍 DEBUG EXCEL: Colunas: {list(df.columns)}")
            
            if df.empty:
                print("🔍 DEBUG EXCEL: DataFrame está vazio!")
                return []
            
            # Pega a primeira coluna com dados
            clients = df.iloc[:, 0].dropna().astype(str).tolist()
            clients = [client.strip() for client in clients if client.strip()]
            
            print(f"🔍 DEBUG EXCEL: {len(clients)} clientes encontrados:")
            for i, client in enumerate(clients):
                print(f"🔍 DEBUG EXCEL: Cliente {i+1}: '{client}'")
                if 'ems' in client.lower():
                    print(f"🔍 DEBUG EXCEL: *** EMS ENCONTRADO NO EXCEL: '{client}' ***")
            
            return clients
            
        except Exception as e:
            print(f"🔍 DEBUG EXCEL: ERRO ao ler Excel: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def read_pdf_text(self, pdf_path):
        """Lê texto do PDF com debug detalhado."""
        try:
            print(f"🔍 DEBUG PDF: Lendo arquivo: {pdf_path}")
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"🔍 DEBUG PDF: PDF tem {len(reader.pages)} páginas")
                
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    print(f"🔍 DEBUG PDF: Página {i+1} - {len(page_text)} caracteres extraídos")
                    
                    # Mostrar preview da página
                    if page_text:
                        preview = page_text[:200].replace('\n', ' ').strip()
                        print(f"🔍 DEBUG PDF: Página {i+1} preview: {preview}...")
                        
                        # Verificar se contém EMS especificamente
                        if 'ems' in page_text.lower():
                            print(f"🔍 DEBUG PDF: *** EMS ENCONTRADO NA PÁGINA {i+1}! ***")
                            # Mostrar contexto onde EMS aparece
                            lines = page_text.split('\n')
                            for j, line in enumerate(lines):
                                if 'ems' in line.lower():
                                    print(f"🔍 DEBUG PDF: Linha {j+1}: {line.strip()}")
                    else:
                        print(f"🔍 DEBUG PDF: Página {i+1} - NENHUM TEXTO EXTRAÍDO!")
                    
                    text += page_text + "\n"
            
            print(f"🔍 DEBUG PDF: Total de texto extraído: {len(text)} caracteres")
            
            # Verificar se contém EMS no texto completo
            if 'ems' in text.lower():
                print("🔍 DEBUG PDF: *** EMS ENCONTRADO NO TEXTO COMPLETO! ***")
                import re
                matches = list(re.finditer(r'ems[^a-z]*', text.lower()))
                print(f"🔍 DEBUG PDF: {len(matches)} ocorrências de EMS encontradas")
                
                for i, match in enumerate(matches[:5]):  # Mostrar até 5 ocorrências
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end].replace('\n', ' ')
                    print(f"🔍 DEBUG PDF: Ocorrência {i+1}: ...{context}...")
            else:
                print("🔍 DEBUG PDF: *** EMS NÃO ENCONTRADO NO TEXTO EXTRAÍDO! ***")
                print("🔍 DEBUG PDF: Isso pode indicar:")
                print("🔍 DEBUG PDF: 1. PDF é escaneado (imagem) sem texto")
                print("🔍 DEBUG PDF: 2. Texto está em formato não extraível")
                print("🔍 DEBUG PDF: 3. EMS está escrito de forma diferente")
                
                # Mostrar amostra do texto para debug
                if text:
                    sample = text[:500].replace('\n', ' ')
                    print(f"🔍 DEBUG PDF: Amostra do texto extraído: {sample}...")
                
            return text
            
        except Exception as e:
            print(f"🔍 DEBUG PDF: ERRO ao ler PDF: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def find_matches(self, client_list, pdf_text):
        """Busca correspondências com algoritmos super melhorados."""
        results = []
        pdf_lower = pdf_text.lower()
        total = len(client_list)
        
        # Pré-processar PDF para diferentes tipos de busca
        import re
        pdf_clean = re.sub(r'[^\w\s]', ' ', pdf_lower)  # Remove pontuação
        pdf_spaces = re.sub(r'\s+', ' ', pdf_clean)     # Normaliza espaços
        pdf_words = set(pdf_spaces.split())             # Conjunto de palavras
        
        print(f"🔍 DEBUG: PDF tem {len(pdf_text)} caracteres, {len(pdf_words)} palavras únicas")
        
        for i, client in enumerate(client_list):
            if not client:
                continue
                
            client_original = str(client).strip()
            client_lower = client_original.lower()
            
            # Pré-processar cliente
            client_clean = re.sub(r'[^\w\s]', ' ', client_lower)
            client_spaces = re.sub(r'\s+', ' ', client_clean).strip()
            client_words = client_spaces.split()
            
            print(f"🔍 DEBUG: Processando '{client_original}' -> palavras: {client_words}")
            
            # === ALGORITMOS DE BUSCA ===
            
            # 1. Busca exata completa
            exact_match = client_lower in pdf_lower
            
            # 2. Busca sem pontuação
            clean_match = client_spaces in pdf_spaces
            
            # 3. Busca por palavras individuais (MELHORADA)
            word_matches = []
            word_contexts = []
            
            for word in client_words:
                if len(word) >= 2:  # Reduzido para 2+ caracteres
                    if word in pdf_words:
                        word_matches.append(word)
                        # Encontrar contexto da palavra
                        word_pattern = r'.{0,30}' + re.escape(word) + r'.{0,30}'
                        contexts = re.findall(word_pattern, pdf_lower, re.IGNORECASE)
                        if contexts:
                            word_contexts.extend(contexts[:2])  # Máximo 2 contextos por palavra
            
            # 4. Busca flexível (variações)
            flexible_matches = []
            for word in client_words:
                if len(word) >= 3:
                    # Buscar variações da palavra
                    variations = [
                        word,
                        word.replace('.', ''),
                        word.replace('s.a.', 'sa'),
                        word.replace('ltda', ''),
                        word + 's',  # plural
                        word[:-1] if word.endswith('s') else word  # singular
                    ]
                    
                    for variation in variations:
                        if variation and variation in pdf_lower:
                            flexible_matches.append(f"{word}→{variation}")
                            break
            
            # 5. Busca fuzzy com múltiplos algoritmos
            similarity_partial = fuzz.partial_ratio(client_lower, pdf_lower)
            similarity_token = fuzz.token_sort_ratio(client_lower, pdf_lower)
            similarity_set = fuzz.token_set_ratio(client_lower, pdf_lower)
            
            # Busca fuzzy por palavras individuais
            word_similarities = []
            for word in client_words:
                if len(word) >= 3:
                    word_sim = max([
                        fuzz.partial_ratio(word, pdf_lower),
                        fuzz.ratio(word, ' '.join(list(pdf_words)[:100]))  # Primeiras 100 palavras
                    ])
                    word_similarities.append(word_sim)
            
            # Melhor similaridade geral
            all_similarities = [similarity_partial, similarity_token, similarity_set] + word_similarities
            best_similarity = max(all_similarities) if all_similarities else 0
            
            # === DETERMINAÇÃO DE CORRESPONDÊNCIA ===
            
            found = False
            match_type = "N/A"
            match_details = []
            
            if exact_match:
                found = True
                match_type = "Exata"
                match_details.append("correspondência exata")
                
            elif clean_match:
                found = True
                match_type = "Sem pontuação"
                match_details.append("sem pontuação")
                
            elif len(word_matches) > 0:
                # Se encontrou pelo menos uma palavra significativa
                word_ratio = len(word_matches) / len(client_words)
                if word_ratio >= 0.5:  # 50% das palavras encontradas
                    found = True
                    match_type = f"Palavras ({len(word_matches)}/{len(client_words)})"
                    match_details.append(f"palavras: {', '.join(word_matches)}")
                    
            elif len(flexible_matches) > 0:
                found = True
                match_type = "Flexível"
                match_details.append(f"variações: {', '.join(flexible_matches)}")
                
            elif best_similarity >= self.threshold:
                found = True
                match_type = f"Fuzzy ({best_similarity}%)"
                match_details.append(f"similaridade {best_similarity}%")
            
            # === DEBUG ESPECIAL PARA EMS ===
            if "ems" in client_lower:
                print(f"🔍 DEBUG EMS DETALHADO:")
                print(f"   Cliente: '{client_original}'")
                print(f"   Palavras: {client_words}")
                print(f"   Exact: {exact_match}")
                print(f"   Clean: {clean_match}")
                print(f"   Word matches: {word_matches}")
                print(f"   Flexible: {flexible_matches}")
                print(f"   Similarities: P={similarity_partial}, T={similarity_token}, S={similarity_set}")
                print(f"   Word sims: {word_similarities}")
                print(f"   Best sim: {best_similarity}")
                print(f"   Found: {found}, Type: {match_type}")
                if word_contexts:
                    print(f"   Contextos: {word_contexts[:3]}")
            
            # === RESULTADO ===
            results.append({
                "cliente": client_original,
                "encontrado": "Sim" if found else "Não",
                "similaridade": f"{best_similarity}%",
                "tipo": match_type,
                "detalhes": '; '.join(match_details) if match_details else "Nenhuma correspondência",
                "palavras_encontradas": ', '.join(word_matches) if word_matches else "Nenhuma",
                "contextos": ' | '.join(word_contexts[:2]) if word_contexts else "N/A"
            })
            
            # Atualizar progresso
            self.progress = int((i + 1) / total * 100)
            self.status_message = f"Processando cliente {i + 1} de {total}..."
        
        return results
    
    def process_files_from_paths(self, excel_path, pdf_path, threshold, temp_dir):
        """Processa os arquivos a partir de caminhos."""
        print(f"🔍 DEBUG: Iniciando process_files_from_paths com threshold={threshold}")
        self.processing = True
        self.progress = 0
        self.threshold = threshold
        
        try:
            print("🔍 DEBUG: Lendo arquivo Excel...")
            self.status_message = "Lendo arquivo Excel..."
            clients = self.read_excel_clients(excel_path)
            print(f"🔍 DEBUG: {len(clients) if clients else 0} clientes encontrados")
            
            if not clients:
                print("🔍 DEBUG: Nenhum cliente encontrado no Excel")
                self.status_message = "❌ Erro: Nenhum cliente encontrado no Excel"
                self.processing = False
                # Limpar arquivos temporários
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None
            
            print("🔍 DEBUG: Lendo arquivo PDF...")
            self.status_message = f"📊 {len(clients)} clientes carregados. Lendo PDF..."
            pdf_text = self.read_pdf_text(pdf_path)
            print(f"🔍 DEBUG: PDF lido, {len(pdf_text) if pdf_text else 0} caracteres")
            
            if not pdf_text:
                print("🔍 DEBUG: Não foi possível ler o PDF")
                self.status_message = "❌ Erro: Não foi possível ler o PDF"
                self.processing = False
                # Limpar arquivos temporários
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None
            
            print("🔍 DEBUG: Buscando correspondências...")
            self.status_message = "🔍 Buscando correspondências..."
            results = self.find_matches(clients, pdf_text)
            print(f"🔍 DEBUG: {len(results) if results else 0} resultados processados")
            
            # Salvar resultados no diretório do usuário (Downloads)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"resultados_crawler_{timestamp}.xlsx"
            
            # Tentar salvar na pasta Downloads do usuário
            import os
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            
            if os.path.exists(downloads_dir):
                output_path = os.path.join(downloads_dir, output_filename)
            else:
                # Fallback para diretório atual
                output_path = os.path.abspath(output_filename)
            
            print(f"🔍 DEBUG: Salvando resultados em: {output_path}")
            
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False)
            print("🔍 DEBUG: Arquivo Excel salvo com sucesso")
            
            # Armazenar o caminho completo para download
            self.last_output_file = output_path
            self.last_output_filename = output_filename
            
            found_count = sum(1 for r in results if r['encontrado'] == 'Sim')
            self.status_message = f"✅ Concluído! {found_count}/{len(results)} clientes encontrados"
            self.results = results
            self.processing = False
            
            # Limpar arquivos temporários
            print("🔍 DEBUG: Limpando arquivos temporários...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            print("🔍 DEBUG: Processamento concluído com sucesso!")
            return {
                'success': True,
                'total': len(results),
                'found': found_count,
                'file': output_path,
                'results': results
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: ERRO durante processamento: {str(e)}")
            print(f"🔍 DEBUG: Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"🔍 DEBUG: Traceback completo:")
            traceback.print_exc()
            
            self.status_message = f"❌ Erro: {str(e)}"
            self.processing = False
            # Limpar arquivos temporários se existirem
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print("🔍 DEBUG: Arquivos temporários limpos após erro")
            except:
                print("🔍 DEBUG: Erro ao limpar arquivos temporários")
                pass
            return None

# Instância global do crawler
crawler = CrawlerPDFDesktop()

# Criar aplicação Flask
app = Flask(__name__)
app.secret_key = 'crawler_pdf_secret_key'

# Template HTML da aplicação
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Crawler PDF - Buscar Clientes</title>
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
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .form-group {
            margin-bottom: 30px;
        }
        
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            font-size: 1.1em;
        }
        
        .file-input {
            width: 100%;
            padding: 15px;
            border: 2px dashed #ddd;
            border-radius: 10px;
            background: #f9f9f9;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1em;
        }
        
        .file-input:hover {
            border-color: #4facfe;
            background: #f0f8ff;
        }
        
        .tolerance-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .tolerance-slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            margin: 15px 0;
        }
        
        .tolerance-value {
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            color: #4facfe;
            margin-top: 10px;
        }
        
        .process-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .process-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(40, 167, 69, 0.3);
        }
        
        .process-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .progress-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .status-message {
            text-align: center;
            font-weight: bold;
            color: #333;
            margin-top: 10px;
        }
        
        .results-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .results-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #4facfe;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .download-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(23, 162, 184, 0.3);
        }
        
        .emoji {
            font-size: 1.2em;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .processing {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Crawler PDF</h1>
            <p>Busque clientes do Excel em documentos PDF</p>
        </div>
        
        <div class="content">
            <form id="crawlerForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="excelFile">
                        <span class="emoji">📊</span>Arquivo Excel (Lista de Clientes)
                    </label>
                    <input type="file" id="excelFile" name="excelFile" accept=".xlsx,.xls" 
                           class="file-input" required>
                </div>
                
                <div class="form-group">
                    <label for="pdfFile">
                        <span class="emoji">📄</span>Arquivo PDF (Documento para Buscar)
                    </label>
                    <input type="file" id="pdfFile" name="pdfFile" accept=".pdf" 
                           class="file-input" required>
                </div>
                
                <div class="form-group">
                    <div class="tolerance-group">
                        <label>
                            <span class="emoji">🎯</span>Tolerância de Similaridade
                        </label>
                        <input type="range" id="tolerance" name="tolerance" 
                               min="50" max="100" value="80" class="tolerance-slider">
                        <div class="tolerance-value">
                            <span id="toleranceValue">80</span>%
                        </div>
                        <small style="color: #666; text-align: center; display: block; margin-top: 10px;">
                            Maior = mais rigoroso | Menor = mais flexível
                        </small>
                    </div>
                </div>
                
                <button type="submit" class="process-btn" id="processBtn">
                    <span class="emoji">🚀</span>Processar Arquivos
                </button>
            </form>
            
            <div class="progress-section" id="progressSection">
                <h3>Processando...</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="status-message" id="statusMessage">Iniciando...</div>
            </div>
            
            <div class="results-section" id="resultsSection">
                <h3>✅ Processamento Concluído!</h3>
                <div class="results-stats" id="resultsStats">
                    <!-- Stats serão inseridas aqui -->
                </div>
                <button class="download-btn" id="downloadBtn">
                    <span class="emoji">💾</span>Baixar Resultados
                </button>
            </div>
        </div>
    </div>

    <script>
        // Elementos do DOM
        const form = document.getElementById('crawlerForm');
        const processBtn = document.getElementById('processBtn');
        const progressSection = document.getElementById('progressSection');
        const resultsSection = document.getElementById('resultsSection');
        const progressFill = document.getElementById('progressFill');
        const statusMessage = document.getElementById('statusMessage');
        const toleranceSlider = document.getElementById('tolerance');
        const toleranceValue = document.getElementById('toleranceValue');
        
        let currentResultFile = null;
        
        // Atualizar valor da tolerância
        toleranceSlider.addEventListener('input', function() {
            toleranceValue.textContent = this.value;
        });
        
        // Processar formulário
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            // Mostrar progresso
            progressSection.style.display = 'block';
            resultsSection.style.display = 'none';
            processBtn.disabled = true;
            processBtn.classList.add('processing');
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    // Iniciar monitoramento do progresso
                    monitorProgress();
                } else {
                    throw new Error('Erro no servidor');
                }
                
            } catch (error) {
                alert('Erro ao processar arquivos: ' + error.message);
                resetUI();
            }
        });
        
        // Monitorar progresso
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
                    alert('Erro durante o processamento');
                    resetUI();
                }
                
            } catch (error) {
                console.error('Erro ao monitorar progresso:', error);
                setTimeout(monitorProgress, 2000);
            }
        }
        
        // Mostrar resultados
        function showResults(results) {
            progressSection.style.display = 'none';
            resultsSection.style.display = 'block';
            
            const statsContainer = document.getElementById('resultsStats');
            statsContainer.innerHTML = `
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
        
        // Download dos resultados
        document.getElementById('downloadBtn').addEventListener('click', function() {
            if (currentResultFile) {
                window.open('/download/' + encodeURIComponent(currentResultFile));
            }
        });
        
        // Reset da UI
        function resetUI() {
            processBtn.disabled = false;
            processBtn.classList.remove('processing');
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
        print("🔍 DEBUG: Recebida requisição POST /process")
        
        excel_file = request.files.get('excelFile')
        pdf_file = request.files.get('pdfFile')
        tolerance = request.form.get('tolerance')
        
        print(f"🔍 DEBUG: Excel file: {excel_file.filename if excel_file else 'None'}")
        print(f"🔍 DEBUG: PDF file: {pdf_file.filename if pdf_file else 'None'}")
        print(f"🔍 DEBUG: Tolerance: {tolerance}")
        
        if not excel_file or not pdf_file:
            print("🔍 DEBUG: Arquivos não foram enviados corretamente")
            return jsonify({'success': False, 'error': 'Arquivos não enviados'}), 400
        
        threshold = int(tolerance)
        print(f"🔍 DEBUG: Threshold convertido: {threshold}")
        
        # CORREÇÃO: Salvar arquivos ANTES da thread
        print("🔍 DEBUG: Salvando arquivos antes da thread...")
        temp_dir = tempfile.mkdtemp()
        excel_temp_path = os.path.join(temp_dir, f"temp_excel_{excel_file.filename}")
        pdf_temp_path = os.path.join(temp_dir, f"temp_pdf_{pdf_file.filename}")
        
        # Salvar arquivos imediatamente
        print(f"🔍 DEBUG: Salvando Excel: {excel_file.filename} -> {excel_temp_path}")
        excel_file.save(excel_temp_path)
        
        print(f"🔍 DEBUG: Salvando PDF: {pdf_file.filename} -> {pdf_temp_path}")
        pdf_file.save(pdf_temp_path)
        
        print(f"🔍 DEBUG: Arquivos salvos em: {temp_dir}")
        
        # Verificar se arquivos foram salvos corretamente
        import os
        excel_size = os.path.getsize(excel_temp_path) if os.path.exists(excel_temp_path) else 0
        pdf_size = os.path.getsize(pdf_temp_path) if os.path.exists(pdf_temp_path) else 0
        
        print(f"🔍 DEBUG: Excel salvo: {excel_size} bytes")
        print(f"🔍 DEBUG: PDF salvo: {pdf_size} bytes")
        
        if excel_size == 0:
            print("🔍 DEBUG: ERRO - Arquivo Excel está vazio!")
        if pdf_size == 0:
            print("🔍 DEBUG: ERRO - Arquivo PDF está vazio!")
        
        # Processar em thread separada com caminhos dos arquivos
        def process_thread():
            print("🔍 DEBUG: Iniciando thread de processamento")
            result = crawler.process_files_from_paths(excel_temp_path, pdf_temp_path, threshold, temp_dir)
            print(f"🔍 DEBUG: Thread concluída, resultado: {result is not None}")
        
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        print("🔍 DEBUG: Thread iniciada")
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"🔍 DEBUG: ERRO na rota /process: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/progress')
def get_progress():
    """Retorna o progresso atual."""
    if not crawler.processing and crawler.results:
        # Processamento concluído
        found_count = sum(1 for r in crawler.results if r['encontrado'] == 'Sim')
        
        # Usar o nome do arquivo salvo ou gerar um padrão
        filename = crawler.last_output_filename
        if not filename:
            filename = f"resultados_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return jsonify({
            'processing': False,
            'progress': 100,
            'status': crawler.status_message,
            'results': {
                'total': len(crawler.results),
                'found': found_count,
                'file': filename
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
        print(f"🔍 DEBUG DOWNLOAD: Tentando baixar arquivo: {filename}")
        print(f"🔍 DEBUG DOWNLOAD: last_output_file: {crawler.last_output_file}")
        
        # 1. Usar o último arquivo salvo (prioridade)
        if crawler.last_output_file and os.path.exists(crawler.last_output_file):
            print(f"🔍 DEBUG DOWNLOAD: Usando arquivo salvo: {crawler.last_output_file}")
            return send_file(crawler.last_output_file, as_attachment=True, download_name=crawler.last_output_filename or filename)
        
        # 2. Procurar na pasta Downloads do usuário
        home_dir = os.path.expanduser("~")
        downloads_dir = os.path.join(home_dir, "Downloads")
        downloads_path = os.path.join(downloads_dir, filename)
        
        if os.path.exists(downloads_path):
            print(f"🔍 DEBUG DOWNLOAD: Encontrado em Downloads: {downloads_path}")
            return send_file(downloads_path, as_attachment=True)
        
        # 3. Procurar no diretório atual
        current_dir = os.getcwd()
        current_path = os.path.join(current_dir, filename)
        
        if os.path.exists(current_path):
            print(f"🔍 DEBUG DOWNLOAD: Encontrado no diretório atual: {current_path}")
            return send_file(current_path, as_attachment=True)
        
        # 4. Procurar qualquer arquivo com padrão similar
        import glob
        
        # Procurar em Downloads
        pattern = os.path.join(downloads_dir, "resultados_crawler_*.xlsx")
        files = glob.glob(pattern)
        if files:
            latest_file = max(files, key=os.path.getctime)  # Arquivo mais recente
            print(f"🔍 DEBUG DOWNLOAD: Usando arquivo mais recente: {latest_file}")
            return send_file(latest_file, as_attachment=True)
        
        # Procurar no diretório atual
        pattern = os.path.join(current_dir, "resultados_crawler_*.xlsx")
        files = glob.glob(pattern)
        if files:
            latest_file = max(files, key=os.path.getctime)
            print(f"🔍 DEBUG DOWNLOAD: Usando arquivo mais recente (atual): {latest_file}")
            return send_file(latest_file, as_attachment=True)
        
        print(f"🔍 DEBUG DOWNLOAD: Arquivo não encontrado em lugar nenhum!")
        return f"Arquivo não encontrado: {filename}. Verifique se o processamento foi concluído.", 404
        
    except Exception as e:
        print(f"🔍 DEBUG DOWNLOAD: ERRO: {e}")
        import traceback
        traceback.print_exc()
        return f"Erro ao baixar arquivo: {e}", 500

def open_browser():
    """Abre o navegador após um delay."""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    """Função principal."""
    print("🚀 Iniciando Crawler PDF Desktop...")
    print("📱 Abrindo aplicação no navegador...")
    
    # Abrir navegador em thread separada
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Iniciar servidor Flask
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")

if __name__ == "__main__":
    main() 