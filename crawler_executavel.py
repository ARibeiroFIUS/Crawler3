#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler de Clientes em PDF - Versão Executável
==============================================

Versão otimizada para ser compilada em executável.
"""

import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class CrawlerPDFExecutavel:
    def __init__(self):
        self.threshold = 80
        self.results = []
        
    def read_excel_clients(self, excel_path):
        """Lê clientes do arquivo Excel."""
        try:
            df = pd.read_excel(excel_path)
            if df.empty:
                return []
            
            # Pega a primeira coluna com dados
            clients = df.iloc[:, 0].dropna().astype(str).tolist()
            clients = [client.strip() for client in clients if client.strip()]
            
            return clients
        except Exception as e:
            print(f"Erro ao ler Excel: {e}")
            return []
    
    def read_pdf_text(self, pdf_path):
        """Lê texto do PDF."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
            return ""
    
    def find_matches(self, client_list, pdf_text):
        """Busca correspondências."""
        results = []
        pdf_lower = pdf_text.lower()
        
        for client in client_list:
            if not client:
                continue
                
            client_lower = str(client).lower()
            
            # Busca exata
            exact_match = client_lower in pdf_lower
            
            # Busca fuzzy
            similarity = fuzz.partial_ratio(client_lower, pdf_lower)
            
            if exact_match or similarity >= self.threshold:
                results.append({
                    "cliente": client,
                    "encontrado": "Sim",
                    "similaridade": f"{similarity}%"
                })
            else:
                results.append({
                    "cliente": client,
                    "encontrado": "Não", 
                    "similaridade": f"{similarity}%"
                })
        
        return results
    
    def save_results(self, results, output_path):
        """Salva resultados."""
        try:
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def process_files(self, excel_path, pdf_path, output_path):
        """Processa os arquivos."""
        print("🔍 Iniciando processamento...")
        
        # Ler clientes
        clients = self.read_excel_clients(excel_path)
        if not clients:
            print("❌ Erro: Nenhum cliente encontrado no Excel")
            return False
        
        print(f"📊 {len(clients)} clientes carregados")
        
        # Ler PDF
        pdf_text = self.read_pdf_text(pdf_path)
        if not pdf_text:
            print("❌ Erro: Não foi possível ler o PDF")
            return False
        
        print("📄 PDF lido com sucesso")
        
        # Buscar correspondências
        print("🔍 Buscando correspondências...")
        results = self.find_matches(clients, pdf_text)
        
        # Salvar resultados
        if self.save_results(results, output_path):
            found_count = sum(1 for r in results if r['encontrado'] == 'Sim')
            print(f"✅ Processamento concluído!")
            print(f"📈 {found_count}/{len(results)} clientes encontrados")
            print(f"💾 Resultados salvos em: {output_path}")
            return True
        else:
            print("❌ Erro ao salvar resultados")
            return False


class InterfaceGrafica:
    def __init__(self):
        self.crawler = CrawlerPDFExecutavel()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface."""
        self.root = tk.Tk()
        self.root.title("🔍 Crawler PDF - Buscar Clientes")
        self.root.geometry("600x500")
        
        # Título
        title_label = tk.Label(
            self.root,
            text="🔍 CRAWLER DE CLIENTES EM PDF",
            font=("Arial", 16, "bold"),
            fg="blue"
        )
        title_label.pack(pady=20)
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Seleção de arquivo Excel
        excel_frame = ttk.LabelFrame(main_frame, text="📊 Arquivo Excel (Lista de Clientes)", padding=10)
        excel_frame.pack(fill="x", pady=5)
        
        self.excel_path = tk.StringVar()
        excel_entry = ttk.Entry(excel_frame, textvariable=self.excel_path, width=50)
        excel_entry.pack(side="left", padx=(0, 10))
        
        excel_btn = ttk.Button(excel_frame, text="Selecionar", command=self.select_excel)
        excel_btn.pack(side="right")
        
        # Seleção de arquivo PDF
        pdf_frame = ttk.LabelFrame(main_frame, text="📄 Arquivo PDF (Documento para Buscar)", padding=10)
        pdf_frame.pack(fill="x", pady=5)
        
        self.pdf_path = tk.StringVar()
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path, width=50)
        pdf_entry.pack(side="left", padx=(0, 10))
        
        pdf_btn = ttk.Button(pdf_frame, text="Selecionar", command=self.select_pdf)
        pdf_btn.pack(side="right")
        
        # Tolerância
        tolerance_frame = ttk.LabelFrame(main_frame, text="🎯 Tolerância de Similaridade", padding=10)
        tolerance_frame.pack(fill="x", pady=5)
        
        self.tolerance = tk.IntVar(value=80)
        tolerance_scale = ttk.Scale(
            tolerance_frame,
            from_=50,
            to=100,
            variable=self.tolerance,
            orient="horizontal"
        )
        tolerance_scale.pack(fill="x")
        
        tolerance_label = ttk.Label(tolerance_frame, textvariable=self.tolerance)
        tolerance_label.pack()
        
        # Botão processar
        process_btn = ttk.Button(
            main_frame,
            text="🚀 PROCESSAR ARQUIVOS",
            command=self.start_processing,
            style="Accent.TButton"
        )
        process_btn.pack(pady=20)
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=5)
    
    def log(self, message):
        """Adiciona mensagem ao log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def select_excel(self):
        """Seleciona arquivo Excel."""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            self.excel_path.set(filename)
    
    def select_pdf(self):
        """Seleciona arquivo PDF."""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.pdf_path.set(filename)
    
    def start_processing(self):
        """Inicia processamento em thread separada."""
        if not self.excel_path.get():
            messagebox.showerror("Erro", "Selecione o arquivo Excel!")
            return
        
        if not self.pdf_path.get():
            messagebox.showerror("Erro", "Selecione o arquivo PDF!")
            return
        
        self.progress.start()
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """Processa os arquivos."""
        try:
            self.crawler.threshold = self.tolerance.get()
            
            # Definir arquivo de saída
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"resultados_crawler_{timestamp}.xlsx"
            
            self.log("🔍 Iniciando processamento...")
            
            success = self.crawler.process_files(
                self.excel_path.get(),
                self.pdf_path.get(),
                output_path
            )
            
            self.progress.stop()
            
            if success:
                self.log("✅ Processamento concluído com sucesso!")
                messagebox.showinfo(
                    "Sucesso",
                    f"Processamento concluído!\n\nResultados salvos em:\n{output_path}"
                )
            else:
                self.log("❌ Erro durante o processamento")
                messagebox.showerror("Erro", "Erro durante o processamento")
                
        except Exception as e:
            self.progress.stop()
            self.log(f"❌ Erro: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")
    
    def run(self):
        """Executa a interface."""
        self.root.mainloop()


def main():
    """Função principal."""
    print("🚀 Iniciando Crawler PDF...")
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        # Modo linha de comando
        if len(sys.argv) != 3:
            print("Uso: crawler_executavel.py <arquivo.xlsx> <documento.pdf>")
            return 1
        
        excel_path = sys.argv[1]
        pdf_path = sys.argv[2]
        
        crawler = CrawlerPDFExecutavel()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"resultados_{timestamp}.xlsx"
        
        success = crawler.process_files(excel_path, pdf_path, output_path)
        return 0 if success else 1
    
    else:
        # Modo interface gráfica
        try:
            app = InterfaceGrafica()
            app.run()
            return 0
        except Exception as e:
            print(f"Erro ao iniciar interface: {e}")
            return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1) 