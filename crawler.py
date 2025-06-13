# crawler.py

import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz
import os

def read_excel_clients(excel_path):
    """
    Lê um arquivo Excel e extrai os nomes dos clientes.
    Assume que os nomes dos clientes estão na primeira coluna da primeira aba.
    """
    try:
    df = pd.read_excel(excel_path)
        # Remove valores nulos e converte para string
        clients = df.iloc[:, 0].dropna().astype(str).tolist()
        print(f"Clientes carregados: {len(clients)}")
    return clients
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
        return []

def read_pdf_text(pdf_path):
    """
    Lê um arquivo PDF e extrai todo o texto.
    """
    try:
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
        print(f"Texto extraído do PDF: {len(text)} caracteres")
    return text
    except Exception as e:
        print(f"Erro ao ler o arquivo PDF: {e}")
        return ""

def find_matches(client_list, pdf_text, threshold=80):
    """
    Compara cada cliente da lista with o texto do PDF usando similaridade (fuzzywuzzy).
    Retorna uma lista de dicionários com o cliente, se encontrado, e a similaridade.
    """
    results = []
    print(f"Buscando correspondências com tolerância de {threshold}%...")
    
    for i, client in enumerate(client_list):
        if not client or pd.isna(client):
            continue
            
        # Usar partial_ratio para melhor detecção de nomes dentro do texto
        match = fuzz.partial_ratio(str(client).lower(), pdf_text.lower())
        
        if match >= threshold:
            results.append({
                "cliente": client, 
                "encontrado": "Sim", 
                "similaridade": f"{match}%"
            })
            print(f"✓ Cliente '{client}' encontrado (similaridade: {match}%)")
        else:
            results.append({
                "cliente": client, 
                "encontrado": "Não", 
                "similaridade": f"{match}%"
            })
        
        # Mostrar progresso a cada 10 clientes
        if (i + 1) % 10 == 0:
            print(f"Processados {i + 1}/{len(client_list)} clientes...")
    
    return results

def create_directories():
    """
    Cria as pastas input e output se não existirem.
    """
    for folder in ['input', 'output']:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Pasta '{folder}' criada.")

def main(excel_path, pdf_path, output_path, threshold=80):
    print("=== CRAWLER DE CLIENTES EM PDF ===")
    print(f"Arquivo Excel: {excel_path}")
    print(f"Arquivo PDF: {pdf_path}")
    print(f"Arquivo de saída: {output_path}")
    print(f"Tolerância de similaridade: {threshold}%")
    print("=" * 40)
    
    # Verificar se os arquivos existem
    if not os.path.exists(excel_path):
        print(f"ERRO: Arquivo Excel não encontrado: {excel_path}")
        return
    
    if not os.path.exists(pdf_path):
        print(f"ERRO: Arquivo PDF não encontrado: {pdf_path}")
        return
    
    # Ler dados
    clients = read_excel_clients(excel_path)
    if not clients:
        print("ERRO: Nenhum cliente encontrado no arquivo Excel.")
        return
    
    pdf_text = read_pdf_text(pdf_path)
    if not pdf_text:
        print("ERRO: Não foi possível extrair texto do arquivo PDF.")
        return
    
    # Buscar correspondências
    matches = find_matches(clients, pdf_text, threshold)

    # Criar DataFrame com os resultados
    results_df = pd.DataFrame(matches)
    
    # Criar pasta de saída se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar resultados
    results_df.to_excel(output_path, index=False)
    
    # Estatísticas finais
    found_count = sum(1 for match in matches if match['encontrado'] == 'Sim')
    total_count = len(matches)
    
    print("\n=== RESULTADOS ===")
    print(f"Total de clientes: {total_count}")
    print(f"Clientes encontrados: {found_count}")
    print(f"Clientes não encontrados: {total_count - found_count}")
    print(f"Taxa de sucesso: {found_count/total_count*100:.1f}%")
    print(f"Resultados salvos em: {output_path}")

if __name__ == "__main__":
    # Criar estrutura de diretórios
    create_directories()
    
    # Caminhos dos arquivos
    excel_file = "clientes.xlsx"  # Arquivo direto na raiz do projeto
    pdf_file = "documento.pdf"     # Arquivo direto na raiz do projeto
    output_file = "output/resultados_busca.xlsx"

    # Executar o crawler
    main(excel_file, pdf_file, output_file)


