# ==============================================================================
# src/CLI.py - Interface de Linha de Comando (CLI) - Etapa 3
# ==============================================================================
# Responsável: Ana Clara
# 
# Este módulo implementa a interface de linha de comando (CLI) para o sistema
# de Recuperação de Informação. Ele recebe consultas do usuário e exibe
# resultados ranqueados de forma clara e estruturada.
# ==============================================================================

import os
import json
import sys
from logging import getLogger
from Config import LOG_DIR_OUTPUT
from SearchEngine import SearchEngine

logger = getLogger('ColetorLogger')

class CLI:
    """
    Interface de Linha de Comando para o Sistema de Recuperação de Informação.
    
    Responsabilidades:
    1. Receber consultas do usuário
    2. Validar dados e garantir que o sistema esteja pronto
    3. Orquestrar a busca usando SearchEngine
    4. Exibir resultados de forma amigável
    """
    
    # Caminho para o arquivo document_map.json (necessário para exibição)
    DOCUMENT_MAP_FILE = os.path.join(LOG_DIR_OUTPUT, 'document_map.json')
    INDICE_INVERTIDO_FILE = os.path.join(LOG_DIR_OUTPUT, 'indice_invertido.json')
    IDF_FILE = os.path.join(LOG_DIR_OUTPUT, 'idf.json')

    @staticmethod
    def verificar_prerequisitos():
        """
        Verifica se todos os arquivos necessários para a busca existem.
        Retorna True se tudo está pronto, False caso contrário.
        """
        arquivos_necessarios = [
            CLI.INDICE_INVERTIDO_FILE,
            CLI.IDF_FILE,
            CLI.DOCUMENT_MAP_FILE
        ]
        
        faltando = []
        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                faltando.append(arquivo)
        
        if faltando:
            logger.error("Arquivos necessários para a busca não foram encontrados:")
            for arquivo in faltando:
                logger.error(f"  - {arquivo}")
            logger.error("\nExecute as etapas anteriores antes de usar a busca:")
            logger.error("  1. Coleta (--etapa coleta)")
            logger.error("  2. Indexação (--etapa indexacao)")
            logger.error("  3. Cálculo de IDF (--etapa idf)")
            return False
        
        logger.info("[OK] Todos os arquivos necessarios foram encontrados.")
        return True

    @staticmethod
    def carregar_indice_invertido_parcial(termos: list):
        """
        Carrega apenas os termos necessários do índice invertido para economizar memória.
        Útil para evitar carregar o arquivo inteiro (4.6 GB) na memória.
        
        :param termos: Lista de termos processados a buscar
        :return: Dicionário com os termos e suas postings
        """
        try:
            import ijson
            resultado = {}
            
            with open(CLI.INDICE_INVERTIDO_FILE, 'r', encoding='utf-8') as f:
                for termo, termo_info in ijson.kvitems(f, ''):
                    if termo in termos:
                        resultado[termo] = termo_info.get('postings', {})
            
            logger.info(f"Carregados {len(resultado)} termos do índice invertido.")
            return resultado
        except Exception as e:
            logger.error(f"Erro ao carregar índice invertido: {e}")
            return {}

    @staticmethod
    def carregar_document_map():
        """
        Carrega o mapa de documentos (DocID -> URL).
        
        :return: Dicionário {doc_id: url, ...} ou None se falhar
        """
        try:
            with open(CLI.DOCUMENT_MAP_FILE, 'r', encoding='utf-8') as f:
                document_map = json.load(f)
            logger.info(f"Mapa de documentos carregado com {len(document_map)} URLs.")
            return document_map
        except Exception as e:
            logger.error(f"Erro ao carregar document_map.json: {e}")
            return None

    @staticmethod
    def exibir_cabecalho():
        """Exibe o cabeçalho de boas-vindas da CLI."""
        print("\n" + "=" * 80)
        print("  SISTEMA DE RECUPERAÇÃO DE INFORMAÇÃO - PHISHING DETECTOR")
        print("  Etapa 3: Busca e Ranking TF-IDF")
        print("=" * 80)
        print("  Digite sua consulta (ou 'sair' para finalizar)")
        print("-" * 80 + "\n")

    @staticmethod
    def exibir_resultado_busca(query: str, resultados: list, document_map: dict, limit: int = 10):
        """
        Exibe os resultados da busca de forma estruturada e amigável.
        
        :param query: A consulta realizada
        :param resultados: Lista de tuplas (doc_id, score)
        :param document_map: Mapa de DocID -> URL
        :param limit: Número máximo de resultados a exibir
        """
        print("\n" + "-" * 80)
        print(f"RESULTADOS PARA: '{query}'")
        print("-" * 80)
        
        if not resultados:
            print("  [ERRO] Nenhum resultado encontrado para esta consulta.")
            print("  >> Tente com termos diferentes ou menos especificos.")
            return
        
        print(f"  [OK] Encontrados {len(resultados)} documentos relevantes\n")
        
        for rank, (doc_id, score) in enumerate(resultados[:limit], 1):
            # Obtém a URL correspondente
            doc_id_str = str(doc_id)
            url = document_map.get(doc_id_str, f"DocID {doc_id} (URL não encontrada)")
            
            # Formata o score como percentual de relevância
            percentual = min(100, round(score * 100, 2))
            
            print(f"  {rank}. [Relevância: {percentual}%]")
            print(f"     URL: {url}")
            print()
        
        print("-" * 80 + "\n")

    @staticmethod
    def executar_busca(query: str, document_map: dict, limite_resultados: int = 10):
        """
        Executa uma busca completa (do recebimento da query até exibição de resultados).
        
        :param query: String de consulta do usuário
        :param document_map: Mapa de DocID -> URL
        :param limite_resultados: Número máximo de resultados a retornar
        """
        if not query or not query.strip():
            print("  [ERRO] Consulta vazia. Digite algo e tente novamente.")
            return
        
        logger.info(f"Iniciando busca para a consulta: '{query}'")
        
        try:
            # 1. Gerar o vetor TF-IDF da consulta (Camille Irias)
            logger.info("Etapa 1/4: Processando consulta (limpeza, stemming, stopwords)...")
            vetor_consulta = SearchEngine.gerar_vetor_consulta_tfidf(query)
            
            if not vetor_consulta:
                print("  [ERRO] A consulta nao contem termos relevantes apos o processamento.")
                print("  >> Tente com palavras-chave mais significativas.")
                logger.warning(f"Consulta '{query}' resultou em vetor vazio após processamento.")
                return
            
            print(f"  [OK] Consulta processada com {len(vetor_consulta)} termos unicos.")
            
            # 2. Carregar os termos necessários do índice invertido (Luana Mateus)
            logger.info("Etapa 2/4: Carregando índice invertido para os termos encontrados...")
            termos_query = list(vetor_consulta.keys())
            indice_parcial = CLI.carregar_indice_invertido_parcial(termos_query)
            
            if not indice_parcial:
                print("  [ERRO] Nenhum termo da consulta foi encontrado no indice.")
                print("  >> Os termos podem estar muito especificos ou raros.")
                logger.warning(f"Nenhum termo de '{query}' encontrado no índice invertido.")
                return
            
            print(f"  [OK] Indice carregado para {len(indice_parcial)} termos.")
            
            # 3. Carregar o mapa IDF (Osvaldo Neto já calculou)
            logger.info("Etapa 3/4: Carregando pesos IDF...")
            try:
                with open(CLI.IDF_FILE, 'r', encoding='utf-8') as f:
                    idf_map = json.load(f)
                print(f"  [OK] Mapa IDF carregado.")
            except Exception as e:
                logger.error(f"Erro ao carregar IDF: {e}")
                print("  [ERRO] Nao foi possivel carregar os pesos IDF.")
                return
            
            # 4. Ranquear documentos usando Similaridade do Cosseno (Ana Paula)
            logger.info("Etapa 4/4: Ranqueando documentos por relevância...")
            resultados_ranqueados = SearchEngine.ranquear_documentos(
                vetor_consulta, 
                indice_parcial, 
                idf_map, 
                limite=limite_resultados
            )
            
            # 5. Mapear DocIDs para URLs (Lucas Lima)
            logger.info("Mapeando resultados para URLs originais...")
            
            # 6. Exibir resultados (Ana Clara)
            CLI.exibir_resultado_busca(query, resultados_ranqueados, document_map, limit=limite_resultados)
            logger.info(f"Busca concluída com sucesso. {len(resultados_ranqueados)} resultados exibidos.")
            
        except Exception as e:
            logger.error(f"Erro durante a busca: {e}")
            print(f"  [ERRO] Erro ao processar a busca: {str(e)}")
            print("  >> Verifique os logs para mais informacoes.")

    @staticmethod
    def modo_interativo():
        """
        Executa o modo interativo da CLI, onde o usuário pode fazer múltiplas buscas.
        """
        # Verificar se tudo está pronto
        if not CLI.verificar_prerequisitos():
            logger.error("Impossível iniciar o modo de busca. Verifique os pré-requisitos.")
            return
        
        # Carregar o mapa de documentos (usado para exibição)
        document_map = CLI.carregar_document_map()
        if document_map is None:
            logger.error("Impossível carregar o mapa de documentos.")
            return
        
        # Exibir cabeçalho
        CLI.exibir_cabecalho()
        
        # Loop interativo
        while True:
            try:
                # Receber entrada do usuário
                query = input("Busca > ").strip()
                
                # Verificar se quer sair
                if query.lower() in ['sair', 'exit', 'quit', 'q']:
                    print("\n" + "=" * 80)
                    print("  Encerrando o sistema de busca. Obrigado por usar!")
                    print("=" * 80 + "\n")
                    logger.info("Modo interativo encerrado pelo usuário.")
                    break
                
                # Executar busca
                CLI.executar_busca(query, document_map, limite_resultados=10)
                
            except KeyboardInterrupt:
                # Tratamento para Ctrl+C
                print("\n\n" + "=" * 80)
                print("  Sistema interrompido pelo usuário.")
                print("=" * 80 + "\n")
                logger.info("Modo interativo interrompido (Ctrl+C).")
                break
            except Exception as e:
                logger.error(f"Erro no modo interativo: {e}")
                print(f"  [ERRO] Erro inesperado: {str(e)}")
                continue

    @staticmethod
    def busca_unica(query: str, limite_resultados: int = 10):
        """
        Executa uma busca única (non-interativa) e exibe os resultados.
        Útil para integração com scripts ou argumentos de linha de comando.
        
        :param query: String de consulta
        :param limite_resultados: Número máximo de resultados a exibir
        """
        # Verificar pré-requisitos
        if not CLI.verificar_prerequisitos():
            logger.error("Impossível executar a busca. Verifique os pré-requisitos.")
            return
        
        # Carregar mapa de documentos
        document_map = CLI.carregar_document_map()
        if document_map is None:
            logger.error("Impossível carregar o mapa de documentos.")
            return
        
        # Executar busca
        CLI.executar_busca(query, document_map, limite_resultados)


# ==============================================================================
# FUNÇÃO DE ENTRADA PRINCIPAL
# ==============================================================================

def main():
    """
    Ponto de entrada para o modo de busca interativo.
    Chamado pelo launcher Coletor.py quando --etapa busca
    """
    try:
        CLI.modo_interativo()
    except Exception as e:
        logger.critical(f"Erro critico no modo interativo: {e}")
        print(f"\n[ERRO CRITICO] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Configurar logging se executado diretamente
    from Logging import setup_logging
    setup_logging()
    
    # Se houver argumento de linha de comando, usar busca única
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        CLI.busca_unica(query)
    else:
        # Caso contrário, modo interativo
        main()
