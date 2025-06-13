#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawler de Clientes em PDF - Versão Avançada
============================================

Este script busca uma lista de clientes (de um arquivo Excel) em documentos PDF
usando algoritmos de similaridade fuzzy com tolerância configurável.

Autor: Assistant AI
Data: 2024
"""

import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz, process
import os
import sys
import glob
import argparse
from datetime import datetime

class PDFClientCrawler:
    def __init__(self, threshold=80, verbose=True):
        """
        Inicializa o crawler com configurações.
        
        Args:
            threshold (int): Tolerância de similaridade (0-100%)
            verbose (bool): Se deve mostrar mensagens detalhadas
        """
        self.threshold = threshold
        self.verbose = verbose
        self.results = []
        
    def log(self, message):
        """Imprime mensagem se modo verbose estiver ativo."""
        if self.verbose:
            print(message)
    
    def read_excel_clients(self, excel_path, column=0, sheet=0):
        """
        Lê um arquivo Excel e extrai os nomes dos clientes.
        
        Args:
            excel_path (str): Caminho para o arquivo Excel
            column (int): Índice da coluna a ser lida (0-indexado)
            sheet (int): Índice da aba a ser lida (0-indexado)
        
        Returns:
            list: Lista de nomes de clientes
        """
        try:
            # Ler arquivo Excel especificando a aba
            df = pd.read_excel(excel_path, sheet_name=sheet)
            
            # Verificar se o DataFrame não está vazio
            if df.empty:
                self.log(f"AVISO: Arquivo Excel está vazio: {excel_path}")
                return []
            
            # Verificar se a coluna existe
            if column >= len(df.columns):
                self.log(f"ERRO: Coluna {column} não existe. Total de colunas: {len(df.columns)}")
                return []
            
            # Extrair dados da coluna especificada
            clients = df.iloc[:, column].dropna().astype(str).tolist()
            
            # Filtrar strings vazias e limpar espaços
            clients = [client.strip() for client in clients if client.strip()]
            
            self.log(f"✓ Clientes carregados: {len(clients)}")
            if len(clients) > 0:
                self.log(f"  Primeiro cliente: '{clients[0]}'")
                self.log(f"  Último cliente: '{clients[-1]}'")
            
            return clients
            
        except Exception as e:
            self.log(f"ERRO ao ler o arquivo Excel: {e}")
            return []
    
    def read_pdf_text(self, pdf_path):
        """
        Lê um arquivo PDF e extrai todo o texto.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
        
        Returns:
            str: Texto extraído do PDF
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                self.log(f"  PDF possui {total_pages} páginas")
                
                for page_num in range(total_pages):
                    page_text = reader.pages[page_num].extract_text()
                    text += page_text + "\n"
                    
                    if self.verbose and page_num % 5 == 0:
                        self.log(f"  Processando página {page_num + 1}/{total_pages}")
            
            self.log(f"✓ Texto extraído: {len(text)} caracteres")
            return text
            
        except Exception as e:
            self.log(f"ERRO ao ler o arquivo PDF: {e}")
            return ""
    
    def find_matches_advanced(self, client_list, pdf_text):
        """
        Busca correspondências usando múltiplos algoritmos de similaridade.
        
        Args:
            client_list (list): Lista de nomes de clientes
            pdf_text (str): Texto do PDF
        
        Returns:
            list: Lista de dicionários com resultados
        """
        results = []
        pdf_lower = pdf_text.lower()
        
        self.log(f"Buscando correspondências com tolerância de {self.threshold}%...")
        
        for i, client in enumerate(client_list):
            if not client or pd.isna(client):
                continue
            
            client_lower = str(client).lower()
            
            # Múltiplos algoritmos de similaridade
            partial_ratio = fuzz.partial_ratio(client_lower, pdf_lower)
            ratio = fuzz.ratio(client_lower, pdf_lower)
            token_sort_ratio = fuzz.token_sort_ratio(client_lower, pdf_lower)
            
            # Usar o maior score
            best_score = max(partial_ratio, ratio, token_sort_ratio)
            
            # Verificar correspondência exata (case-insensitive)
            exact_match = client_lower in pdf_lower
            
            if best_score >= self.threshold or exact_match:
                match_type = "Exata" if exact_match else "Fuzzy"
                results.append({
                    "cliente": client,
                    "encontrado": "Sim",
                    "similaridade": f"{best_score}%",
                    "tipo_match": match_type,
                    "score_partial": partial_ratio,
                    "score_ratio": ratio,
                    "score_token": token_sort_ratio
                })
                self.log(f"✓ '{client}' encontrado ({match_type}, {best_score}%)")
            else:
                results.append({
                    "cliente": client,
                    "encontrado": "Não",
                    "similaridade": f"{best_score}%",
                    "tipo_match": "N/A",
                    "score_partial": partial_ratio,
                    "score_ratio": ratio,
                    "score_token": token_sort_ratio
                })
            
            # Mostrar progresso
            if (i + 1) % 20 == 0:
                self.log(f"  Processados {i + 1}/{len(client_list)} clientes...")
        
        return results
    
    def save_results(self, results, output_path, include_metadata=True):
        """
        Salva os resultados em um arquivo Excel.
        
        Args:
            results (list): Lista de resultados
            output_path (str): Caminho do arquivo de saída
            include_metadata (bool): Se deve incluir metadados na saída
        """
        try:
            # Criar DataFrame principal
            df = pd.DataFrame(results)
            
            # Criar pasta de saída se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if include_metadata:
                # Criar metadados
                metadata = {
                    "Informação": [
                        "Data/Hora da Execução",
                        "Tolerância de Similaridade",
                        "Total de Clientes",
                        "Clientes Encontrados",
                        "Taxa de Sucesso (%)"
                    ],
                    "Valor": [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        f"{self.threshold}%",
                        len(results),
                        sum(1 for r in results if r['encontrado'] == 'Sim'),
                        f"{(sum(1 for r in results if r['encontrado'] == 'Sim') / len(results) * 100):.1f}%" if results else "0%"
                    ]
                }
                metadata_df = pd.DataFrame(metadata)
                
                # Salvar com múltiplas abas
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Resultados', index=False)
                    metadata_df.to_excel(writer, sheet_name='Metadados', index=False)
            else:
                # Salvar apenas os resultados
                df.to_excel(output_path, index=False)
            
            self.log(f"✓ Resultados salvos em: {output_path}")
            
        except Exception as e:
            self.log(f"ERRO ao salvar resultados: {e}")
    
    def process_files(self, excel_path, pdf_path, output_path=None, excel_column=0, excel_sheet=0):
        """
        Processa um arquivo Excel e um PDF.
        
        Args:
            excel_path (str): Caminho do arquivo Excel
            pdf_path (str): Caminho do arquivo PDF
            output_path (str): Caminho do arquivo de saída (opcional)
            excel_column (int): Coluna do Excel a ser lida
            excel_sheet (int): Aba do Excel a ser lida
        
        Returns:
            dict: Estatísticas do processamento
        """
        self.log("=" * 50)
        self.log("🔍 CRAWLER DE CLIENTES EM PDF - VERSÃO AVANÇADA")
        self.log("=" * 50)
        self.log(f"📊 Arquivo Excel: {excel_path}")
        self.log(f"📄 Arquivo PDF: {pdf_path}")
        self.log(f"🎯 Tolerância: {self.threshold}%")
        self.log("-" * 50)
        
        # Verificar arquivos
        if not os.path.exists(excel_path):
            self.log(f"❌ ERRO: Arquivo Excel não encontrado: {excel_path}")
            return None
        
        if not os.path.exists(pdf_path):
            self.log(f"❌ ERRO: Arquivo PDF não encontrado: {pdf_path}")
            return None
        
        # Processar arquivos
        clients = self.read_excel_clients(excel_path, excel_column, excel_sheet)
        if not clients:
            self.log("❌ ERRO: Nenhum cliente encontrado no arquivo Excel.")
            return None
        
        pdf_text = self.read_pdf_text(pdf_path)
        if not pdf_text:
            self.log("❌ ERRO: Não foi possível extrair texto do arquivo PDF.")
            return None
        
        # Buscar correspondências
        results = self.find_matches_advanced(clients, pdf_text)
        
        # Definir arquivo de saída se não especificado
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/resultados_{timestamp}.xlsx"
        
        # Salvar resultados
        self.save_results(results, output_path)
        
        # Calcular estatísticas
        found_count = sum(1 for r in results if r['encontrado'] == 'Sim')
        total_count = len(results)
        success_rate = (found_count / total_count * 100) if total_count > 0 else 0
        
        stats = {
            'total_clients': total_count,
            'found_clients': found_count,
            'not_found_clients': total_count - found_count,
            'success_rate': success_rate,
            'output_file': output_path
        }
        
        # Mostrar estatísticas finais
        self.log("\n" + "=" * 30)
        self.log("📊 ESTATÍSTICAS FINAIS")
        self.log("=" * 30)
        self.log(f"📈 Total de clientes: {total_count}")
        self.log(f"✅ Clientes encontrados: {found_count}")
        self.log(f"❌ Clientes não encontrados: {total_count - found_count}")
        self.log(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        self.log(f"💾 Arquivo de saída: {output_path}")
        
        return stats

def main():
    """Função principal com interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Crawler para buscar clientes de Excel em arquivos PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python crawler_advanced.py clientes.xlsx documento.pdf
  python crawler_advanced.py clientes.xlsx documento.pdf -t 90 -o resultados.xlsx
  python crawler_advanced.py clientes.xlsx documento.pdf --coluna 1 --aba 0
        """
    )
    
    parser.add_argument('excel', help='Arquivo Excel com lista de clientes')
    parser.add_argument('pdf', help='Arquivo PDF para buscar')
    parser.add_argument('-o', '--output', help='Arquivo de saída (opcional)')
    parser.add_argument('-t', '--threshold', type=int, default=80, 
                        help='Tolerância de similaridade (0-100, padrão: 80)')
    parser.add_argument('-c', '--coluna', type=int, default=0,
                        help='Coluna do Excel (0-indexado, padrão: 0)')
    parser.add_argument('-a', '--aba', type=int, default=0,
                        help='Aba do Excel (0-indexado, padrão: 0)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Modo silencioso (menos mensagens)')
    
    args = parser.parse_args()
    
    # Validar threshold
    if not 0 <= args.threshold <= 100:
        print("ERRO: Threshold deve estar entre 0 e 100")
        return
    
    # Criar crawler
    crawler = PDFClientCrawler(
        threshold=args.threshold,
        verbose=not args.quiet
    )
    
    # Processar arquivos
    stats = crawler.process_files(
        excel_path=args.excel,
        pdf_path=args.pdf,
        output_path=args.output,
        excel_column=args.coluna,
        excel_sheet=args.aba
    )
    
    if stats:
        return 0  # Sucesso
    else:
        return 1  # Erro

if __name__ == "__main__":
    sys.exit(main()) 