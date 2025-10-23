# ==============================================================================
# Script auxiliar para verificar o total de URLs coletadas.
# ==============================================================================
import os
import sys
import pandas as pd

# 1. Configurar o Python Path (CRUCIAL se estiver na raiz)
# Se este arquivo estiver na RAIZ, precisamos configurar o caminho para 'src'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# 2. Importar o logger (opcional, mas recomendado para formatar a saída)
try:
    from Logging import setup_logging
    # Inicializa o logger para esta execução
    logger = setup_logging()
except ImportError:
    # Fallback se o logging falhar (para que o script ainda funcione)
    def logger_info(msg):
        print(msg)
    logger = type('Logger', (object,), {'info': logger_info})()


def contar_paginas_coletadas():
    # 1. Obtém o diretório ONDE O SCRIPT ESTÁ RODANDO (E:\Documentos\RIWRS_2\src)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe um nível para encontrar a RAIZ do projeto (E:\Documentos\RIWRS_2\)
    BASE_PATH = os.path.dirname(SCRIPT_DIR)
    
    # 3. Usa o BASE_PATH para construir o caminho correto para a pasta logs
    LOG_DIR_OUTPUT = os.path.join(BASE_PATH, 'logs')
    LOG_FILE = os.path.join(LOG_DIR_OUTPUT, 'collection_log.csv')

    logger.info("-" * 40)
    logger.info(f"Verificando log em: {LOG_FILE}")
    
    if not os.path.exists(LOG_FILE):
        logger.info("AVISO: Arquivo de log mestre (collection_log.csv) não encontrado.")
        return 0

    try:
        # 1. Carrega todo o log
        # Use low_memory=False para lidar com grandes arquivos CSV
        df_log = pd.read_csv(LOG_FILE, on_bad_lines='skip', low_memory=False)
        
        # 2. Conta o total de entradas no log
        total_entradas = len(df_log)

        # 3. Filtra as entradas que começam com 'SUCCESS'
        # Usa na=False para garantir que strings vazias ou NaN sejam ignoradas no filtro
        df_success = df_log[df_log['status'].str.startswith('SUCCESS', na=False)]
        
        # 4. Filtra as entradas que começam com 'ERROR'
        df_error = df_log[df_log['status'].str.startswith('ERROR', na=True)]

        # 5. Conta as URLs únicas (nunique) para evitar contagem de duplicação por erro
        total_coletado_unico = df_success['original_url']
        
        logger.info(f"TOTAL DE TENTATIVAS REGISTRADAS (linhas no CSV): {total_entradas}")
        logger.info(f"URLs ÚNICAS COLETADAS COM SUCESSO: {total_coletado_unico}")
        logger.info(f"STATUS DE SUCESSO ENCONTRADO: {len(df_success)} entradas.")
        logger.info(f"TOTAL DE ERROS ENCONTRADOS E STATUS DESCONHECIDO: {len(df_error)} entradas.")
        logger.info("-" * 40)
        return total_coletado_unico
        
    except Exception as e:
        logger.info(f"ERRO CRÍTICO ao processar o log: {e}")
        return 0

if __name__ == '__main__':
    contar_paginas_coletadas()