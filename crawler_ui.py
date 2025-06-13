#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Gráfica para o Crawler de Clientes em PDF
==================================================

Interface amigável para facilitar o uso do crawler sem linha de comando.

Autor: Assistant AI
Data: 2024
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
import sys

# Importar o crawler
from crawler_advanced import PDFClientCrawler

class CrawlerUI:
    def __init__(self, root):
        """Inicializa a interface gráfica."""
        self.root = root
        self.root.title("🔍 Crawler de Clientes em PDF - Interface Gráfica")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variáveis
        self.excel_path = tk.StringVar()
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.threshold = tk.IntVar(value=80)
        self.excel_column = tk.IntVar(value=0)
        self.excel_sheet = tk.IntVar(value=0)
        
        # Status do processamento
        self.is_processing = False
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Cria todos os widgets da interface."""
        
        # Título principal
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=20, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="🔍 Crawler de Clientes em PDF", 
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="Busque nomes de clientes do Excel em documentos PDF com inteligência artificial",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Frame principal com notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba 1: Configuração
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="⚙️ Configuração")
        self.create_config_tab()
        
        # Aba 2: Processamento
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="🚀 Processamento")
        self.create_process_tab()
        
        # Aba 3: Ajuda
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="❓ Ajuda")
        self.create_help_tab()
    
    def create_config_tab(self):
        """Cria a aba de configuração."""
        
        # Frame de arquivos
        files_frame = ttk.LabelFrame(self.config_frame, text="📁 Seleção de Arquivos")
        files_frame.pack(fill="x", padx=10, pady=10)
        
        # Arquivo Excel
        excel_frame = ttk.Frame(files_frame)
        excel_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(excel_frame, text="📊 Arquivo Excel:", width=15).pack(side="left")
        ttk.Entry(excel_frame, textvariable=self.excel_path, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(excel_frame, text="Procurar", command=self.select_excel_file).pack(side="right", padx=5)
        
        # Arquivo PDF
        pdf_frame = ttk.Frame(files_frame)
        pdf_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(pdf_frame, text="📄 Arquivo PDF:", width=15).pack(side="left")
        ttk.Entry(pdf_frame, textvariable=self.pdf_path, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(pdf_frame, text="Procurar", command=self.select_pdf_file).pack(side="right", padx=5)
        
        # Pasta de saída
        output_frame = ttk.Frame(files_frame)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(output_frame, text="💾 Pasta de Saída:", width=15).pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Procurar", command=self.select_output_dir).pack(side="right", padx=5)
        
        # Frame de configurações avançadas
        advanced_frame = ttk.LabelFrame(self.config_frame, text="🔧 Configurações Avançadas")
        advanced_frame.pack(fill="x", padx=10, pady=10)
        
        # Tolerância
        tolerance_frame = ttk.Frame(advanced_frame)
        tolerance_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(tolerance_frame, text="🎯 Tolerância de Similaridade:").pack(side="left")
        tolerance_scale = ttk.Scale(
            tolerance_frame, 
            from_=50, 
            to=100, 
            variable=self.threshold, 
            orient="horizontal"
        )
        tolerance_scale.pack(side="left", padx=10, fill="x", expand=True)
        self.tolerance_label = ttk.Label(tolerance_frame, text="80%")
        self.tolerance_label.pack(side="right")
        
        # Configurar callback para atualizar o label
        tolerance_scale.configure(command=self.update_tolerance_label)
        
        # Configurações do Excel
        excel_config_frame = ttk.Frame(advanced_frame)
        excel_config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(excel_config_frame, text="📊 Coluna do Excel (0=primeira):").pack(side="left")
        ttk.Spinbox(
            excel_config_frame, 
            from_=0, 
            to=50, 
            textvariable=self.excel_column,
            width=5
        ).pack(side="left", padx=10)
        
        ttk.Label(excel_config_frame, text="📋 Aba do Excel (0=primeira):").pack(side="left", padx=(20, 0))
        ttk.Spinbox(
            excel_config_frame, 
            from_=0, 
            to=20, 
            textvariable=self.excel_sheet,
            width=5
        ).pack(side="left", padx=10)
        
        # Botão de processamento
        button_frame = ttk.Frame(self.config_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        self.process_button = ttk.Button(
            button_frame,
            text="🚀 INICIAR PROCESSAMENTO",
            command=self.start_processing
        )
        self.process_button.pack(pady=10)
    
    def create_process_tab(self):
        """Cria a aba de processamento."""
        
        # Status frame
        status_frame = ttk.LabelFrame(self.process_frame, text="📊 Status do Processamento")
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="⏳ Aguardando início do processamento...")
        self.status_label.pack(padx=10, pady=5)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Log do processo
        log_frame = ttk.LabelFrame(self.process_frame, text="📝 Log do Processamento")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(self.process_frame, text="📈 Resultados")
        results_frame.pack(fill="x", padx=10, pady=10)
        
        self.results_text = ttk.Label(results_frame, text="Nenhum processamento realizado ainda.")
        self.results_text.pack(padx=10, pady=10)
        
        # Botões de ação
        action_frame = ttk.Frame(self.process_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        self.open_results_button = ttk.Button(
            action_frame,
            text="📂 Abrir Pasta de Resultados",
            command=self.open_results_folder,
            state="disabled"
        )
        self.open_results_button.pack(side="left", padx=5)
        
        ttk.Button(
            action_frame,
            text="🗑️ Limpar Log",
            command=self.clear_log
        ).pack(side="left", padx=5)
    
    def create_help_tab(self):
        """Cria a aba de ajuda."""
        
        help_text = """🔍 COMO USAR O CRAWLER DE CLIENTES EM PDF

📋 PASSO A PASSO:

1️⃣ Selecione o arquivo Excel com a lista de clientes
   • O arquivo deve estar no formato .xlsx
   • Por padrão, usa a primeira coluna da primeira aba

2️⃣ Selecione o arquivo PDF onde buscar
   • Funciona melhor com PDFs que têm texto selecionável
   • PDFs escaneados podem ter resultados limitados

3️⃣ Escolha a pasta onde salvar os resultados
   • Se não especificar, criará uma pasta 'output'

4️⃣ Configure as opções avançadas (opcional):
   • Tolerância: 70-90% funciona bem na maioria dos casos
   • Coluna/Aba: especifique onde estão os nomes no Excel

5️⃣ Clique em "INICIAR PROCESSAMENTO"
   • Acompanhe o progresso na aba "Processamento"

📊 RESULTADOS:
O arquivo Excel gerado terá duas abas:
• "Resultados": lista com todos os clientes e se foram encontrados
• "Metadados": estatísticas detalhadas da busca

🎯 DICAS PARA MELHORES RESULTADOS:
• Use tolerância 80% como ponto de partida
• PDFs com texto selecionável funcionam melhor
• Teste com uma amostra pequena primeiro
• Verifique se especificou a coluna correta do Excel

⚠️ PROBLEMAS COMUNS:
• Taxa baixa de sucesso: diminua a tolerância
• "Arquivo não encontrado": verifique os caminhos
• Excel vazio: verifique coluna/aba especificadas

💡 ALGORITMOS DE SIMILARIDADE:
O sistema usa inteligência artificial para encontrar nomes mesmo com:
• Variações de maiúsculas/minúsculas
• Nomes parciais ou abreviados
• Diferentes ordens das palavras
• Pequenos erros de digitação
• Acentos e caracteres especiais

🚀 Este crawler pode processar centenas de clientes rapidamente!"""
        
        help_scroll = scrolledtext.ScrolledText(self.help_frame, wrap="word")
        help_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        help_scroll.insert("1.0", help_text)
        help_scroll.configure(state="disabled")
    
    def update_tolerance_label(self, value):
        """Atualiza o label da tolerância."""
        self.tolerance_label.configure(text=f"{int(float(value))}%")
    
    def select_excel_file(self):
        """Abre diálogo para selecionar arquivo Excel."""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.excel_path.set(filename)
    
    def select_pdf_file(self):
        """Abre diálogo para selecionar arquivo PDF."""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
    
    def select_output_dir(self):
        """Abre diálogo para selecionar pasta de saída."""
        dirname = filedialog.askdirectory(title="Selecionar Pasta de Saída")
        if dirname:
            self.output_dir.set(dirname)
    
    def log_message(self, message):
        """Adiciona mensagem ao log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpa o log."""
        self.log_text.delete("1.0", "end")
    
    def validate_inputs(self):
        """Valida os inputs antes do processamento."""
        if not self.excel_path.get():
            messagebox.showerror("Erro", "Por favor, selecione um arquivo Excel.")
            return False
        
        if not self.pdf_path.get():
            messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF.")
            return False
        
        if not os.path.exists(self.excel_path.get()):
            messagebox.showerror("Erro", "Arquivo Excel não encontrado.")
            return False
        
        if not os.path.exists(self.pdf_path.get()):
            messagebox.showerror("Erro", "Arquivo PDF não encontrado.")
            return False
        
        return True
    
    def start_processing(self):
        """Inicia o processamento em thread separada."""
        if self.is_processing:
            messagebox.showwarning("Aviso", "Processamento já em andamento!")
            return
        
        if not self.validate_inputs():
            return
        
        # Mudar para aba de processamento
        self.notebook.select(1)
        
        # Iniciar processamento em thread separada
        self.is_processing = True
        self.process_button.configure(state="disabled", text="🔄 Processando...")
        self.progress.start()
        self.clear_log()
        
        # Thread para não travar a interface
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """Processa os arquivos em thread separada."""
        try:
            self.log_message("🚀 Iniciando processamento...")
            self.status_label.configure(text="🔄 Processando arquivos...")
            
            # Configurar saída
            if not self.output_dir.get():
                output_dir = os.path.join(os.path.dirname(self.excel_path.get()), "output")
                os.makedirs(output_dir, exist_ok=True)
                self.output_dir.set(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir.get(), f"resultados_crawler_{timestamp}.xlsx")
            
            # Criar crawler personalizado com log
            crawler = CustomCrawlerForUI(
                threshold=self.threshold.get(),
                verbose=True,
                log_callback=self.log_message
            )
            
            # Processar arquivos
            stats = crawler.process_files(
                excel_path=self.excel_path.get(),
                pdf_path=self.pdf_path.get(),
                output_path=output_file,
                excel_column=self.excel_column.get(),
                excel_sheet=self.excel_sheet.get()
            )
            
            if stats:
                self.log_message("✅ Processamento concluído com sucesso!")
                
                # Atualizar resultados
                results_text = f"""📈 ESTATÍSTICAS FINAIS:
• Total de clientes: {stats['total_clients']}
• Clientes encontrados: {stats['found_clients']}
• Clientes não encontrados: {stats['not_found_clients']}
• Taxa de sucesso: {stats['success_rate']:.1f}%
• Arquivo salvo em: {os.path.basename(stats['output_file'])}"""
                
                self.root.after(0, lambda: self.results_text.configure(text=results_text))
                self.root.after(0, lambda: self.open_results_button.configure(state="normal"))
                self.root.after(0, lambda: self.status_label.configure(text="✅ Processamento concluído!"))
                
                # Mostrar mensagem de sucesso
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso!",
                    f"Processamento concluído!\n\n"
                    f"Taxa de sucesso: {stats['success_rate']:.1f}%\n"
                    f"Arquivo salvo em:\n{stats['output_file']}"
                ))
                
            else:
                self.log_message("❌ Erro no processamento.")
                self.root.after(0, lambda: self.status_label.configure(text="❌ Erro no processamento"))
                self.root.after(0, lambda: messagebox.showerror("Erro", "Falha no processamento. Verifique o log."))
        
        except Exception as e:
            self.log_message(f"❌ Erro: {str(e)}")
            self.root.after(0, lambda: self.status_label.configure(text="❌ Erro no processamento"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro no processamento:\n{str(e)}"))
        
        finally:
            # Restaurar interface
            self.is_processing = False
            self.root.after(0, lambda: self.process_button.configure(state="normal", text="🚀 INICIAR PROCESSAMENTO"))
            self.root.after(0, lambda: self.progress.stop())
    
    def open_results_folder(self):
        """Abre a pasta de resultados no explorador."""
        if self.output_dir.get() and os.path.exists(self.output_dir.get()):
            if sys.platform == "win32":
                os.startfile(self.output_dir.get())
            elif sys.platform == "darwin":  # macOS
                os.system(f"open '{self.output_dir.get()}'")
            else:  # Linux
                os.system(f"xdg-open '{self.output_dir.get()}'")
        else:
            messagebox.showwarning("Aviso", "Pasta de resultados não encontrada.")

class CustomCrawlerForUI(PDFClientCrawler):
    """Versão customizada do crawler para interface gráfica."""
    
    def __init__(self, threshold=80, verbose=True, log_callback=None):
        super().__init__(threshold, verbose)
        self.log_callback = log_callback
    
    def log(self, message):
        """Override do log para enviar para a UI."""
        if self.log_callback:
            self.log_callback(message)
        elif self.verbose:
            print(message)

def main():
    """Função principal da interface."""
    root = tk.Tk()
    
    # Configurar ícone se disponível
    try:
        # Tentar definir ícone (pode não funcionar em todos os sistemas)
        root.iconname("Crawler PDF")
    except:
        pass
    
    app = CrawlerUI(root)
    
    # Centralizar janela
    root.mainloop()

if __name__ == "__main__":
    main() 