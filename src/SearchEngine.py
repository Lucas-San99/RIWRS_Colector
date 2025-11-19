# ==============================================================================
# src/SearchEngine.py
# Módulo principal da Etapa 3, responsável pela busca, ranking e mapeamento.
# ==============================================================================
import os
import json
import ijson
import math
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
    
    @staticmethod
    def similaridade_cosseno(vetor1: dict, vetor2: dict) -> float:
        """
        Tarefa de Ana Paula: Calcula a Similaridade do Cosseno entre dois vetores TF-IDF.
        Cada vetor deve ser um dicionário {termo: peso_TF_IDF}.
        """
        numerador = sum(vetor1[t] * vetor2[t] for t in vetor1 if t in vetor2)
        norma1 = math.sqrt(sum(p ** 2 for p in vetor1.values()))
        norma2 = math.sqrt(sum(p ** 2 for p in vetor2.values()))
        if norma1 == 0 or norma2 == 0:
            return 0.0
        return numerador / (norma1 * norma2)

    @classmethod
    def calcular_pesos_tf_idf(cls, termos_tf: dict, idf_map: dict) -> dict:
        """
        Retorna o vetor TF-IDF aplicando o IDF correspondente a cada termo.
        """
        return {t: tf * idf_map.get(t, 0.0) for t, tf in termos_tf.items()}

    @classmethod
    def ranquear_documentos(cls, consulta_tf: dict, indice_invertido: dict, idf_map: dict, limite: int = 10):
        """
        Ranqueia documentos com base na Similaridade do Cosseno entre
        o vetor TF-IDF da consulta e os vetores TF-IDF dos documentos.
        """
        logger.info("Iniciando cálculo de ranking via Similaridade do Cosseno...")

        consulta_tfidf = cls.calcular_pesos_tf_idf(consulta_tf, idf_map)

        documentos_vetores = {}
        for termo, peso_consulta in consulta_tfidf.items():
            if termo not in indice_invertido:
                continue
            for doc_id, tf_doc in indice_invertido[termo].items():
                if doc_id not in documentos_vetores:
                    documentos_vetores[doc_id] = {}
                documentos_vetores[doc_id][termo] = tf_doc * idf_map.get(termo, 0.0)

        scores = {
            int(doc_id): cls.similaridade_cosseno(consulta_tfidf, vetor_doc)
            for doc_id, vetor_doc in documentos_vetores.items()
        }

        ranking_ordenado = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"Ranking concluído. {len(ranking_ordenado)} documentos ranqueados.")
        return ranking_ordenado[:limite]
    



