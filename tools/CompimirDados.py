# ==============================================================================
# tools/ComprimirDados.py
# Script para compactar a pasta logs/ visando upload para o GitHub.
# Tenta usar compressão máxima.
# ==============================================================================
import os
import sys
import zipfile
import zlib
from tqdm import tqdm

# Adiciona o diretório pai ao path para importar Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.Config import BASE_PATH, LOG_DIR_OUTPUT
except ImportError:
    # Fallback se rodar fora da estrutura
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR_OUTPUT = os.path.join(BASE_PATH, 'logs')

# Configurações
SOURCE_DIR = LOG_DIR_OUTPUT
OUTPUT_ZIP = os.path.join(BASE_PATH, 'dados_compactados_riwrs.zip')
# Pastas ou arquivos para IGNORAR na compressão (para economizar espaço)
IGNORE_PATTERNS = ['temp_html', '.log'] # Ignora HTMLs brutos e logs de execução

def format_size(bytes_size):
    """Formata bytes para MB ou GB."""
    gb = bytes_size / (1024 * 1024 * 1024)
    mb = bytes_size / (1024 * 1024)
    if gb >= 1: return f"{gb:.2f} GB"
    return f"{mb:.2f} MB"

def comprimir_logs():
    print("-" * 60)
    print("FERRAMENTA DE COMPRESSÃO DE DADOS (RIWRS)")
    print("-" * 60)
    print(f"Origem: {SOURCE_DIR}")
    print(f"Destino: {OUTPUT_ZIP}")
    print(f"Ignorando: {IGNORE_PATTERNS}")
    print("Iniciando compressão máxima (Nível 9). Isso vai demorar...")
    print("-" * 60)

    if not os.path.exists(SOURCE_DIR):
        print(f"Erro: Pasta de logs não encontrada: {SOURCE_DIR}")
        return

    # 1. Listar todos os arquivos para calcular o total
    files_to_zip = []
    total_source_size = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Remove pastas ignoradas da lista de navegação
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]
        
        for file in files:
            # Verifica se o arquivo deve ser ignorado pela extensão
            if any(file.endswith(ext) for ext in IGNORE_PATTERNS if ext.startswith('.')):
                continue
                
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, BASE_PATH) # Caminho relativo dentro do ZIP
            files_to_zip.append((file_path, arcname))
            total_source_size += os.path.getsize(file_path)

    print(f"Total a comprimir: {len(files_to_zip)} arquivos ({format_size(total_source_size)})")
    print("Comprimindo...")

    # 2. Criar o ZIP com compressão máxima
    try:
        # Usa ZIP_DEFLATED com nível de compressão 9 (máximo)
        # Requer Python 3.7+ para o parâmetro compresslevel
        with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path, arcname in tqdm(files_to_zip, desc="Progresso", unit="arq"):
                zipf.write(file_path, arcname)
                
    except Exception as e:
        print(f"\nERRO CRÍTICO durante a compressão: {e}")
        return

    # 3. Verificar o resultado
    final_size = os.path.getsize(OUTPUT_ZIP)
    final_size_mb = final_size / (1024 * 1024)
    
    print("-" * 60)
    print("COMPRESSÃO CONCLUÍDA!")
    print(f"Tamanho Original: {format_size(total_source_size)}")
    print(f"Tamanho Final (ZIP): {format_size(final_size)}")
    print("-" * 60)

    # 4. Veredito para o GitHub
    GITHUB_LIMIT_MB = 100
    YOUR_LIMIT_MB = 400

    if final_size_mb < GITHUB_LIMIT_MB:
        print("SUCESSO TOTAL: O arquivo é menor que 100MB.")
        print("Você pode fazer o commit e push normalmente para o GitHub.")
    elif final_size_mb < YOUR_LIMIT_MB:
        print(f"AVISO: O arquivo tem {final_size_mb:.0f}MB (menor que seus 400MB alvo).")
        print("PORÉM, é maior que o limite padrão de 100MB do GitHub.")
        print("Você precisará usar o 'Git LFS' para subir este arquivo.")
    else:
        print("FALHA: O arquivo ainda está muito grande para o GitHub.")
        print("Sugestões:")
        print("1. Use Git LFS (obrigatório).")
        print("2. Ou tente dividir o arquivo em partes menores usando o 7-Zip (externo).")

if __name__ == '__main__':
    # Verifica se tem a lib de compressão necessária
    if not 'zlib' in sys.modules:
        print("Aviso: Biblioteca zlib não detectada. A compressão será ineficiente.")
    comprimir_logs()