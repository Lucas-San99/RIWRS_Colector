# ==============================================================================
# src/SearchEngine.py
# Módulo principal da Etapa 3, responsável pela busca, ranking e mapeamento.
# ==============================================================================
import os
import json
import ijson
from logging import getLogger
from Config import LOG_DIR_OUTPUT

logger = getLogger('ColetorLogger')

# Caminho para o arquivo document_map.json (na pasta de logs da raiz do projeto)
DOCUMENT_MAP_FILE = os.path.join(LOG_DIR_OUTPUT, 'document_map.json')

class SearchEngine:
    # Caminho para o arquivo indice_invertido.json (na pasta de logs da raiz do projeto)
    INDICE_INVERTIDO_FILE = os.path.join(LOG_DIR_OUTPUT, 'indice_invertido.json')

    @classmethod
    def buscar_postings_por_termo(cls, termo_processado):
        """
        Tarefa de Luana Mateus: Busca direta no índice invertido.
        Dado um termo processado (após limpeza/stemming), retorna a lista de DocIDs e suas frequências (TF).

        :param termo_processado: Termo já processado (string)
        :return: Dicionário {doc_id: tf, ...} ou None se termo não encontrado
        Exemplo de uso:
            postings = SearchEngine.buscar_postings_por_termo('log')
            if postings:
                print(postings)  # {"123": 5, "456": 2, ...}
        """
        if not os.path.exists(cls.INDICE_INVERTIDO_FILE):
            logger.critical(f"Arquivo de índice invertido não encontrado em: {cls.INDICE_INVERTIDO_FILE}. A indexação deve ser rodada primeiro.")
            return None

        try:
            with open(cls.INDICE_INVERTIDO_FILE, 'r', encoding='utf-8') as f:
                # Busca incremental usando ijson para não carregar tudo na memória
                for termo, termo_info in ijson.kvitems(f, ''):
                    if termo == termo_processado:
                        if 'postings' in termo_info:
                            return termo_info['postings']
                        else:
                            logger.info(f"Termo '{termo_processado}' não possui postings no índice.")
                            return None
                logger.info(f"Termo '{termo_processado}' não encontrado no índice.")
                return None
        except Exception as e:
            logger.critical(f"Erro ao buscar termo no indice_invertido.json: {e}")
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