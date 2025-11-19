# ==============================================================================
# src/SearchEngine.py
# Módulo principal da Etapa 3, responsável pela busca, ranking e mapeamento.
# ==============================================================================
import os
import json
import ijson
import re
import math
from logging import getLogger
from Config import LOG_DIR_OUTPUT
from collections import defaultdict

try:
    from Indexador import STOPWORDS, STEMMER
except ImportError:
    # Fallback caso o NLTK não esteja instalado
    print("Aviso: Não foi possível carregar STOPWORDS/STEMMER do Indexador.")
    STOPWORDS = set()
    STEMMER = lambda x: x

logger = getLogger('ColetorLogger')

# Caminho para o arquivo document_map.json (na pasta de logs da raiz do projeto)
DOCUMENT_MAP_FILE = os.path.join(LOG_DIR_OUTPUT, 'document_map.json')

class SearchEngine:
    # Caminho para o arquivo indice_invertido.json (na pasta de logs da raiz do projeto)
    INDICE_INVERTIDO_FILE = os.path.join(LOG_DIR_OUTPUT, 'indice_invertido.json')

    IDF_FILE = os.path.join(LOG_DIR_OUTPUT, 'idf.json')
    _idf_map = None

    @classmethod
    def _carregar_idf_map(cls):
        """
        Carrega o mapa de IDF (gerado pelo CalculaIDF.py) em memória.
        Usa um cache simples para evitar recarregar o arquivo.
        """
        if cls._idf_map:
            return cls._idf_map
        
        if not os.path.exists(cls.IDF_FILE):
            logger.critical(f"Arquivo IDF não encontrado: {cls.IDF_FILE}.")
            logger.critical("Execute o script 'CalculaIDF.py' primeiro.")
            return None

        try:
            with open(cls.IDF_FILE, 'r', encoding='utf-8') as f:
                cls._idf_map = json.load(f)
            logger.info(f"Mapa IDF carregado com {len(cls._idf_map)} termos.")
            return cls._idf_map
        except Exception as e:
            logger.critical(f"Falha ao carregar ou processar {cls.IDF_FILE}: {e}")
            return None

    @staticmethod
    def _processar_texto_query(texto_query: str):
        """
        Aplica O MESMO pipeline de processamento do Indexador (Etapa 2.1)
        a uma string de consulta (que não contém HTML).
        
        Esta é uma cópia da lógica de Indexador.limpar_e_tokenizar,
        mas pulando a etapa de extração de HTML (BeautifulSoup).
        """
        
        # 1. Normalização (copiado de Indexador.py)
        # Mantém letras e acentos, remove pontuação/números, e .lower()
        limpo = re.sub(r'[^a-zA-ZáéíóúàèìòùãõâêîôûçÁÉÍÓÚÀÈÌÒÙÃÕÂÊÎÔÛÇ\s]', '', texto_query).lower()
        
        # 2. Tokenização (copiado de Indexador.py)
        tokens = limpo.split()
        
        tokens_processados = []
        for token in tokens:
            # 3. Filtra stopwords e tokens curtos (copiado de Indexador.py)
            if token not in STOPWORDS and len(token) > 2:
                # 4. Stemming (copiado de Indexador.py)
                tokens_processados.append(STEMMER.stem(token))
        
        return tokens_processados

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

    @classmethod
    def gerar_vetor_consulta_tfidf(cls, query_string: str):
        """
        Módulo que recebe a string de consulta do usuário, 
        aplica o mesmo pipeline de Limpeza/Stemming/Stopwords e 
        gera o vetor de features TF-IDF para a busca.

        :param query_string: A busca do usuário
        :return: Dicionário com o vetor de pesos.
        """
        
        # 1. Carregar o mapa IDF (usa cache)
        idf_map = cls._carregar_idf_map()
        if idf_map is None:
            logger.error("Não é possível gerar o vetor da consulta, o mapa IDF não está disponível.")
            return {}

        # 2. Aplicar o pipeline de processamento
        tokens_processados = cls._processar_texto_query(query_string)
        
        if not tokens_processados:
            logger.warning(f"Consulta '{query_string}' resultou em zero tokens após processamento.")
            return {}

        # 3. Calcular o TF (Term Frequency) da consulta
        tf_consulta = defaultdict(int)
        for token in tokens_processados:
            tf_consulta[token] += 1
        
        # 4. Calcular o peso TF-IDF para cada termo na consulta
        vetor_tfidf = {}
        
        for termo, tf in tf_consulta.items():
            
            # Pega o IDF pré-calculado do mapa
            idf = idf_map.get(termo, 0)
            
            # Se idf == 0, o termo não está em nenhum documento
            # (ou não estava no índice), então seu peso na busca é 0.
            if idf > 0:
                # W_t,q = TF_t,q * IDF_t
                # (Estamos usando TF bruto * IDF)
                peso = tf * idf
                vetor_tfidf[termo] = peso
        
        logger.info(f"Consulta '{query_string}' -> Vetor TF-IDF: {vetor_tfidf}")
        return vetor_tfidf
