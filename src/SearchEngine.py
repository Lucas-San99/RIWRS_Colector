# ==============================================================================
# src/SearchEngine.py
# Módulo principal da Etapa 3, responsável pela busca, ranking e mapeamento.
# ==============================================================================
import os
import json
from logging import getLogger
from Config import LOG_DIR_OUTPUT

logger = getLogger('ColetorLogger')

# Caminho para o arquivo document_map.json (na pasta de logs da raiz do projeto)
DOCUMENT_MAP_FILE = os.path.join(LOG_DIR_OUTPUT, 'document_map.json')

class SearchEngine:
    """
    Motor de Busca para o Sistema de Recuperação de Informação.
    Gerencia o carregamento de índices, cálculos de ranking e mapeamento de DocIDs.
    """
    
    # Armazena o mapa de documentos na memória para acesso rápido (Cache)
    _document_map = None

    @classmethod
    def carregar_document_map(cls):
        """Carrega o mapa de DocID -> URL para a memória."""
        if cls._document_map is not None:
            return cls._document_map
        
        logger.info("Carregando mapa de documentos...")
        if not os.path.exists(DOCUMENT_MAP_FILE):
            logger.critical(f"Arquivo de mapa não encontrado em: {DOCUMENT_MAP_FILE}. A indexação deve ser rodada primeiro.")
            return None
        
        try:
            with open(DOCUMENT_MAP_FILE, 'r', encoding='utf-8') as f:
                # O JSON salva as chaves como strings, mas as chaves são DocIDs (inteiros). 
                # Converte-se as chaves para inteiros para busca eficiente.
                map_str = json.load(f)
                cls._document_map = {int(k): v for k, v in map_str.items()}
                logger.info(f"Mapa de documentos carregado. Total de entradas: {len(cls._document_map)}")
                return cls._document_map
        except Exception as e:
            logger.critical(f"Erro ao carregar document_map.json: {e}")
            return None

    @classmethod
    def mapear_resultados_para_urls(cls, doc_ids: list):
        """
        Tarefa de Lucas Lima: Recebe uma lista de DocIDs e retorna a lista de URLs originais.
        
        :param doc_ids: Lista de DocIDs (inteiros) ranqueados.
        :return: Lista de URLs correspondentes (strings).
        """
        doc_map = cls.carregar_document_map()
        
        if doc_map is None:
            # Não pode mapear se o mapa não foi carregado
            return []

        urls_ranqueadas = []
        for doc_id in doc_ids:
            # Usa .get() para evitar KeyErrors se o DocID for inválido/inexistente
            url = doc_map.get(doc_id)
            if url:
                urls_ranqueadas.append(url)
            # Nota: Não logamos o erro aqui, pois é trabalho do teste confirmar se ele ignora DocIDs ruins.
        
        return urls_ranqueadas

# O restante da classe SearchEngine (ranking, IDF, etc.) será adicionado pelos outros colaboradores.