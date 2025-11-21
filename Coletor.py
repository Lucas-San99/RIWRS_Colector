import sys
import os
import argparse

# --- 1. CONFIGURAÇÃO DE PATH ---
# Adiciona o diretório 'src' ao Python Path para encontrar os módulos
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.append(SRC_DIR)

# --- 2. CONFIGURAÇÃO DE LOGGING E MÓDULOS ---
try:
    from Logging import setup_logging, get_log_file
    logger = setup_logging()

    from Processor import main as processor_main, run_post_processing
    from Indexador import Indexador
    from Diagnostico import health_check_sistema
    from Relatorio import GeradorRelatorio
    from CalculaIDF import calcula_idf
    from Config import OUTPUT_DIR_TEMP, LOG_DIR_OUTPUT
    from SearchEngine import SearchEngine
    from CLI import CLI

except ImportError as e:
    print("-" * 50)
    print("ERRO CRÍTICO DE IMPORTAÇÃO!")
    print("Detalhe do Erro: Este erro geralmente indica uma biblioteca faltando.")
    print("Verifique se as dependências (nltk, beautifulsoup4, etc.) estão instaladas no VENV.")
    print(f"Erro original: {e}")
    sys.exit(1)

# ==============================================================================
# FUNÇÕES DE EXECUÇÃO DAS ETAPAS
# ==============================================================================

def rodar_coleta():
    logger.info("ETAPA 1: Iniciando Coleta e Pós-processamento.")
    collection_successful, attempted_urls = processor_main()
    run_post_processing(collection_successful, attempted_urls)
    logger.info("ETAPA 1: Finalizada.")

def rodar_indexacao():
    logger.info("ETAPA 2: Iniciando Indexação.")
    log_file_path = get_log_file()  # Obter o path do log dinamicamente
    # A função agora retorna uma tupla de 3 elementos (indice, mapa, erro)
    indice_invertido, document_map, msg_erro = Indexador.construir_indice_invertido(log_file_path, OUTPUT_DIR_TEMP)
    if indice_invertido and document_map:
        Indexador.salvar_indice(indice_invertido, document_map, LOG_DIR_OUTPUT)
        logger.info("ETAPA 2: Indexação concluída com sucesso.")
    else:
        logger.error(f"ETAPA 2: Falha na indexação. Motivo: {msg_erro}")

def rodar_calculo_idf():
    logger.info("ETAPA 3: Iniciando cálculo de IDF.")
    calcula_idf()
    logger.info("ETAPA 3: Cálculo de IDF finalizado.")

def rodar_diagnostico():
    logger.info("DIAGNÓSTICO: Iniciando verificação de saúde do sistema.")
    health_check_sistema()
    logger.info("DIAGNÓSTICO: Verificação finalizada.")

def rodar_busca_interativa():
    logger.info("MODO INTERATIVO DE BUSCA: Iniciando interface CLI.")
    CLI.modo_interativo()
    logger.info("MODO INTERATIVO DE BUSCA: Finalizado.")


def main():
    parser = argparse.ArgumentParser(description="Coletor e Processador de Páginas Web para RIWRS.")
    parser.add_argument(
        '--etapa',
        type=str,
        choices=['coleta', 'indexacao', 'idf', 'diagnostico', 'busca', 'todas'],
        help="Especifica a etapa a ser executada: 'coleta', 'indexacao', 'idf', 'diagnostico', 'busca' ou 'todas'."
    )

    args = parser.parse_args()

    if args.etapa:
        if args.etapa == 'coleta':
            rodar_coleta()
        elif args.etapa == 'indexacao':
            rodar_indexacao()
        elif args.etapa == 'idf':
            rodar_calculo_idf()
        elif args.etapa == 'diagnostico':
            rodar_diagnostico()
        elif args.etapa == 'busca':
            rodar_busca_interativa()
        elif args.etapa == 'todas':
            logger.info("Executando todas as etapas em sequência...")
            rodar_coleta()
            rodar_indexacao()
            rodar_calculo_idf()
            logger.info("Todas as etapas foram concluídas.")
    else:
        # Se nenhum argumento for fornecido, exibe o menu interativo
        exibir_menu_interativo()

def exibir_menu_interativo():
    def busca_direta_menu():
        termo = input("Digite o termo processado para busca direta: ").strip()
        postings = SearchEngine.buscar_postings_por_termo(termo)
        if postings:
            print(f"\nPostings encontrados para '{termo}': (mostrando até 20 resultados)")
            for i, (doc_id, tf) in enumerate(postings.items()):
                print(f"DocID: {doc_id} | TF: {tf}")
                if i >= 19:
                    print("... (resultados truncados)")
                    break
        else:
            print(f"Termo '{termo}' não encontrado no índice invertido.")

    def busca_com_ranking_menu():
        termo = input("Digite sua consulta (texto livre): ").strip()
        if not termo:
            print("Consulta vazia. Tente novamente.")
            return
        try:
            from src.Config import LOG_DIR_OUTPUT
            import json, os

            with open(os.path.join(LOG_DIR_OUTPUT, 'indice_invertido.json'), 'r', encoding='utf-8') as f:
                indice_invertido = json.load(f)
            with open(os.path.join(LOG_DIR_OUTPUT, 'idf.json'), 'r', encoding='utf-8') as f:
                idf_map = json.load(f)

            termos = termo.lower().split()
            consulta_tf = {}
            for t in termos:
                consulta_tf[t] = consulta_tf.get(t, 0) + 1

            ranking = SearchEngine.ranquear_documentos(consulta_tf, indice_invertido, idf_map)
            doc_ids_ordenados = [doc_id for doc_id, _ in ranking]
            urls = SearchEngine.mapear_resultados_para_urls(doc_ids_ordenados)

            print("\nTop 10 Resultados Ranqueados (TF-IDF + Similaridade do Cosseno):")
            for i, (doc_id, score) in enumerate(ranking[:10]):
                url = urls[i] if i < len(urls) else "(URL não encontrada)"
                print(f"[{i+1}] DocID: {doc_id} | Score: {score:.4f}")
                print(f"     → {url}")
            print("\nBusca concluída.\n")

        except Exception as e:
            print(f"Erro ao executar a busca ranqueada: {e}")

    menu_opcoes = {
        '1': ("Executar Todas as Etapas (Coleta -> Indexação -> IDF -> Busca Direta)", lambda: (rodar_coleta(), rodar_indexacao(), rodar_calculo_idf(), busca_direta_menu())),
        '2': ("Etapa 1: Apenas Coleta e Pós-processamento", rodar_coleta),
        '3': ("Etapa 2: Apenas Indexação", rodar_indexacao),
        '4': ("Etapa 3: Apenas Cálculo de IDF", rodar_calculo_idf),
        '5': ("Etapa 3: Busca Direta por Termo no Índice Invertido", busca_direta_menu),
        '6': ("Etapa 3: Busca com Ranking TF-IDF (Similaridade do Cosseno)", busca_com_ranking_menu),
        '7': ("Etapa 3: Modo Interativo de Busca (CLI)", rodar_busca_interativa),
        '8': ("Verificar Saúde do Sistema (Diagnóstico)", rodar_diagnostico),
        '9': ("Sair", sys.exit)
    }

    while True:
        print("\n" + "="*50)
        print("MENU DE EXECUÇÃO INTERATIVO")
        print("="*50)
        for chave, (descricao, _) in menu_opcoes.items():
            print(f"[{chave}] {descricao}")
        print("-" * 50)
        escolha = input(f"Selecione uma opção (1-{len(menu_opcoes)}): ")
        if escolha in menu_opcoes:
            _, funcao = menu_opcoes[escolha]
            logger.info(f"Opção de menu selecionada: [{escolha}] {menu_opcoes[escolha][0]}")
            funcao()
            if escolha != str(len(menu_opcoes)):
                print("\nProcesso concluído. Voltando ao menu principal...")
        else:
            logger.warning("Opção inválida. Por favor, tente novamente.")

if __name__ == '__main__':
    logger.info("Ambiente configurado. Iniciando o launcher.")
    main()
