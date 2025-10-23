# ==============================================================================
# Coletor.py (NOVO - Launcher Interativo e Modular - CORRIGIDO)
# ==============================================================================
import sys
import os

# --- 1. CONFIGURAÇÃO DE PATH ---
# Adiciona o diretório 'src' ao Python Path para encontrar os módulos
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.append(SRC_DIR)

# --- 2. CONFIGURAÇÃO DE LOGGING E MÓDULOS ---
try:
    from Logging import setup_logging
    # Renomeando de 'Processor' para 'processor' (boa prática)
    from Processor import main as processor_main 
    from Processor import run_post_processing
    
    # Importação da classe Indexador, Diagnostico e Relatorio
    from Indexador import Indexador  
    from Diagnostico import contar_paginas_coletadas
    from Relatorio import GeradorRelatorio
    
    # Importa constantes de caminho do processor para uso interno
    from Processor import BASE_PATH, LOG_FILE, OUTPUT_DIR_TEMP, LOG_DIR_OUTPUT

except ImportError as e:
    # Este bloco pega erros de módulo (como 'No module named Indexador' ou
    # erros de dependência como 'No module named nltk' que estouram no Indexador)
    print("-" * 50)
    print("ERRO CRÍTICO DE IMPORTAÇÃO!")
    print("Detalhe do Erro: Este erro geralmente indica uma biblioteca faltando.")
    print("Verifique se as dependências (nltk, beautifulsoup4, etc.) estão instaladas no VENV.")
    print(f"Erro original: {e}")
    sys.exit(1)

# Inicializa o logger
logger = setup_logging()

# ==============================================================================
# FUNÇÕES DE EXECUÇÃO
# ==============================================================================

def rodar_coletor_principal():
    """Executa a coleta e o pós-processamento completo (Fases 1, 2 e 3)."""
    print("Opção selecionada: INICIAR COLETA E PÓS-PROCESSAMENTO COMPLETO.")
    
    collection_successful, attempted_urls = processor_main()
    run_post_processing(collection_successful, attempted_urls)
    print("COLETA COMPLETA E PÓS-PROCESSAMENTO FINALIZADOS.")

def rodar_diagnostico_contagem():
    """Executa apenas a contagem e diagnóstico do log."""
    print("Opção selecionada: RODAR DIAGNÓSTICO E CONTAGEM DE LOGS.")
    contar_paginas_coletadas()
    print("DIAGNÓSTICO CONCLUÍDO.")

def rodar_pos_processamento_simulado():
    """Roda relatórios e compactação simulando o fim de uma coleta."""
    logger.warning("-" * 50)
    logger.warning("MODO SIMULADO: Pulando a coleta. Executando apenas Pós-Processamento.")
    logger.warning("Este modo requer que o collection_log.csv e arquivos HTML já existam.")
    logger.warning("-" * 50)
    
    collection_successful_mock = True
    attempted_urls_mock = [] 
    
    run_post_processing(collection_successful_mock, attempted_urls_mock)
    print("PÓS-PROCESSAMENTO SIMULADO FINALIZADO.")

def gerar_relatorios_manualmente():
    """Chama a lógica de GeradorRelatorio para criar os CSVs de Sucesso e Erro."""
    print("Opção selecionada: GERAR RELATÓRIOS CONSOLIDADOS.")
    
    # Obter caminhos de entrada e saída (já definidos no processor)
    LOG_DIR_OUTPUT_CALC = os.path.join(PROJECT_ROOT, 'logs')
    LOG_FILE_CALC = os.path.join(LOG_DIR_OUTPUT_CALC, 'collection_log.csv')
    
    print(f"Analisando log mestre em: {LOG_FILE_CALC}")
    
    # Chama o método estático da classe GeradorRelatorio
    relatorio_status = GeradorRelatorio.gerar_relatorios_consolidados(LOG_FILE_CALC, LOG_DIR_OUTPUT_CALC)
    
    if relatorio_status["success_path"]:
        print(f"Relatório de Sucesso (Total: {relatorio_status['success_count']}) salvo em: {relatorio_status['success_path']}")
    if relatorio_status["error_path"]:
        print(f"Relatório de Erros (Total: {relatorio_status['error_count']}) salvo em: {relatorio_status['error_path']}")
    
    if relatorio_status["total"] == 0:
        logger.warning("Nenhuma entrada processada. Verifique se o collection_log.csv existe e contém dados.")

def rodar_indexacao_manual():
    """Executa a indexação (Entrega 2) a partir dos arquivos HTML existentes."""
    print("Opção selecionada: INICIAR INDEXAÇÃO MANUAL (ENTREGA 2).")
    logger.warning("-" * 50)
    logger.warning("NOTA: Esta operação utiliza arquivos da pasta temporária e o log mestre.")
    logger.warning("Verifique se a coleta já foi executada.")
    logger.warning("-" * 50)
    
    # A indexação deve salvar os índices (JSON) na pasta LOG_DIR_OUTPUT (logs/)
    indice_invertido, document_map = Indexador.construir_indice_invertido(
        LOG_FILE, 
        OUTPUT_DIR_TEMP
    )
    
    if indice_invertido:
        Indexador.salvar_indice(indice_invertido, document_map, LOG_DIR_OUTPUT)
        print("INDEXAÇÃO MANUAL CONCLUÍDA COM SUCESSO.")
    else:
        logger.error("INDEXAÇÃO MANUAL FALHOU. Verifique os logs de erro.")


def exibir_menu():
    """Exibe o menu interativo no console."""
    menu_opcoes = {
        '1': ("Iniciar Coleta Principal", rodar_coletor_principal),
        '2': ("Rodar Diagnóstico e Contagem de Logs", rodar_diagnostico_contagem),
        '3': ("Rodar Pós-Processamento (Simulado/Teste)", rodar_pos_processamento_simulado),
        '4': ("Gerar Relatórios de Sucesso/Erro (Manual)", gerar_relatorios_manualmente), 
        '5': ("Rodar Indexação e Representação (Entrega 2)", rodar_indexacao_manual), 
        '6': ("Sair", sys.exit)
    }

    while True:
        print("\n" + "="*50)
        print("MENU DE EXECUÇÃO DO COLETOR WEB RIWRS")
        print("="*50)
        for chave, (descricao, _) in menu_opcoes.items():
            print(f"[{chave}] {descricao}")
        print("-" * 50)
        
        escolha = input("Selecione uma opção (1-6): ")
        
        if escolha in menu_opcoes:
            descricao, funcao = menu_opcoes[escolha]
            if escolha == '6': 
                print("Saindo do programa.")
                funcao() 
            else:
                funcao()
                print("\nProcesso concluído. Voltando ao menu principal...")
        else:
            logger.warning("Opção inválida. Por favor, tente novamente.")


# ==============================================================================
# 4. PONTO DE ENTRADA
# ==============================================================================
if __name__ == '__main__':
    print("Ambiente configurado com sucesso.")
    exibir_menu()