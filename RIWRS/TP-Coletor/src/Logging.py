# ==============================================================================
# log_config.py (VERSÃO FINAL: Logs com Timestamp e Pasta)
# ==============================================================================
import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configura o sistema de logging do coletor.
    
    Cria a pasta 'logs/' e configura um FileHandler para gerar um arquivo
    de log com timestamp único a cada execução.
    """
    
    # 1. Definir o caminho da pasta de logs
    LOG_DIR = 'logs'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    # 2. Gerar o nome do arquivo com timestamp (YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(LOG_DIR, f'coletor_run_{timestamp}.log')

    # 3. Configuração do Logger
    logger = logging.getLogger('ColetorLogger')
    logger.setLevel(logging.INFO) # Nível mínimo para logging

    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para o arquivo (novo log a cada execução)
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler para o console (acompanhamento em tempo real)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Limpar handlers antigos, se houver
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    # Notificar o usuário sobre o novo arquivo de log
    logger.info(f"O log desta execução está sendo salvo em: {log_filename}")
    
    return logger