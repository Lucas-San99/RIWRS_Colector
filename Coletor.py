# ==============================================================================
# Coletor.py - Ponto de Entrada do Coletor
# ==============================================================================
import sys
import os

# --- 1. CONFIGURAÇÃO DE PATH ---
# Adiciona o diretório 'src' ao Python Path para que ele possa encontrar
# os módulos (processador, verificador, etc.) que estão lá dentro.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.append(SRC_DIR)


# --- 2. CONFIGURAÇÃO DE LOGGING E MÓDULOS ---
try:
    from Logging import setup_logging
    from Processor import main as processador_main 
    from Processor import run_post_processing

except ImportError as e:
    print("-" * 50)
    print("ERRO CRÍTICO DE IMPORTAÇÃO!")
    print("Certifique-se de que seus arquivos .py (Verificador.py, Relatorio.py, etc.)")
    print("foram movidos para a pasta 'src/'.")
    print(f"Detalhe: {e}")
    sys.exit(1)

logger = setup_logging()
logger.info("Launcher ativado. Iniciando o Processador...")


# ==============================================================================
# 3. PONTO DE ENTRADA (EXECUÇÃO DO SCRIPT)
# ==============================================================================
if __name__ == '__main__':
    # 1. Executa a função principal (coleta) do módulo processador
    collection_successful, attempted_urls = processador_main()
    
    # 2. Executa as tarefas de pós-processamento
    run_post_processing(collection_successful, attempted_urls)