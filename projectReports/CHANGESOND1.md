# Documento Técnico e Análise de Complexidade do Coletor Web Não Modular --> Modular

## 1\. Justificativa da Arquitetura e Decisão do Ambiente

O projeto Coletor Web foi desenvolvido como um trabalho prático para a disciplina de Recuperação de Informação na Web e Redes Sociais para aplicar conhecimentos teóricos adquiridos em sala de aula. A mudança do ambiente Google Colab para uma solução local e modularizada é justificada pela necessidade de estabilidade, rastreabilidade e escalabilidade.

### 1.1. Justificativa para Migração do Google Colab

| Problema Encontrado no Colab/Drive | Impacto no Projeto |
| :--- | :--- |
| **Erros de Timeout na Conexão do Drive (I/O)** | Ao tentar salvar logs (`.csv`) ou arquivos HTML grandes no Google Drive, a latência da API do Drive frequentemente causava **erros de I/O e *timeouts*** dentro das *threads*. Isso corrompia o processo de coleta e levava à perda de dados. |
| **Limitações do Processo de Coleta** | O Colab tem limites de tempo de execução e memória que são restritivos para coletas em larga escala. A máquina virtual do Colab é volátil; encerrada a sessão, o *state* se perde. |
| **Latência Inesperada** | A velocidade de rede do Colab é compartilhada. Flutuações na latência de rede introduziram *timeouts* aleatórios nas requisições, tornando os logs de erro inconsistentes. |

**Vantagem da Solução Local (VM/VS Code):** O ambiente local é um pouco mais estável e permite controle total sobre o I/O do disco, eliminando *timeouts* induzidos pela API de nuvem e garantindo a persistência imediata de logs e dados.

### 1.2. Benefícios da Modularização e Arquitetura `src/`

A adoção da arquitetura modular (`src/`) e de classes distintas é uma aplicação direta do **Princípio da Responsabilidade Única (SRP)**.

| Benefício | Módulos Envolvidos | Justificativa Técnica |
| :--- | :--- | :--- |
| **Organização Profissional** | Todos | Separa o código-fonte (`src/`) dos artefatos de saída (`logs/`, `datasets/`), seguindo a convenção moderna de Python. |
| **Testabilidade** | `Verificador.py` | A lógica de download pode ser testada isoladamente (Testes Unitários) sem a necessidade de inicializar o *executor* de *threads* principal. |
| **Manutenibilidade** | `Verificador.py`, `Logging.py` | Alterar o tratamento de erros HTTP (no `Verificador.py`) ou o formato do log (no `Logging.py`) não exige modificações no orquestrador principal (`Processor.py`). |
| **Clareza (SRP)** | `Processor.py` | Este arquivo agora foca apenas na lógica de negócio (desduplicação, orquestração de *threads* e geração de logs) e não no *como* fazer o download ou o log. |

## 2\. Análise Detalhada dos Componentes e Imports

| Módulo/Biblioteca | Importação | Função no Código |
| :--- | :--- | :--- |
| **`pandas`** | `import pandas as pd` | Gerenciamento de dados estruturados (CSV). Usado para concatenar as múltiplas listas de URLs, desduplicar e ler/gerar relatórios de logs. |
| **`requests`** | `import requests` (usado em `Verificador.py`) | Realiza todas as requisições HTTP (`GET`). É a biblioteca central para a coleta de dados de rede. |
| **`concurrent.futures`** | `from concurrent.futures import ThreadPoolExecutor, as_completed` | Gerencia o *pool* de *threads* para paralelismo. Essencial para sobrepor o tempo de espera da rede. |
| **`tqdm`** | `from tqdm import tqdm` | Fornece barras de progresso elegantes e informativas no console, acompanhando o trabalho das *threads*. |
| **`logging`** | `import logging` (em `Logging.py` e `Verificador.py`) | Sistema modular de rastreamento de eventos. Permite registrar o sucesso (`INFO`) e a falha (`ERROR`, `CRITICAL`) em tempo real no console e em arquivos persistentes. |
| **`shutil`, `os`** | `import shutil, import os` | Funções do sistema operacional: criação de pastas, manipulação de caminhos, e compactação de arquivos (`shutil.make_archive`). |

## 3\. Estrutura do Programa e Fluxo de Execução

O fluxo do programa é rigidamente controlado pela hierarquia de arquivos e pela separação de tarefas:

  * **`Coletor.py` (Launcher/Ponto de Entrada):** Configura o `sys.path`, inicializa o *logger* e chama `main()` e `run_post_processing()` do `src/processador.py`.
  * **`src/processador.py` (`main()`):** Responsável por concatenar os DataFrames, aplicar `df.drop_duplicates()` para eliminação de redundâncias, filtrar URLs já coletadas e iniciar o `ThreadPoolExecutor` para o trabalho de coleta.
  * **`src/Verificador.py` (`download_url`):** Executa o `requests.get()`. Registra o *status* detalhado (código HTTP) em tempo real no `coletor_run_*.log` e retorna o resultado para registro no `collection_log.csv`.
  * **`src/Processor.py` (`run_post_processing`):** Executa a fase de geração de relatórios, compactação e limpeza, garantindo que todas as tarefas finais sejam completadas.

## 4\. Análise de Paralelismo (Threads) e Complexidade

### 4.1. Processo de Paralelismo: Threads (I/O Bound)

  * **Ferramenta:** `concurrent.futures.ThreadPoolExecutor`.
  * **Decisão:** Escolhemos *threads* em vez de *multiprocessamento* porque a tarefa é **I/O Bound** (limitada por I/O, ou seja, tempo de espera pela rede). O **Efeito do GIL** é neutralizado, pois a *thread* libera o GIL enquanto espera a resposta do servidor, permitindo que outra *thread* trabalhe. Isso maximiza o uso da largura de banda.

### 4.2. Complexidade Assintótica do Código

A complexidade é dominada pelas operações de I/O e de DataFrame.

| Operação | Complexidade (O) | Observação |
| :--- | :--- | :--- |
| **Coleta de URLs (Tempo Total)** | $O(N \cdot T_{avg})$ | $N$ é o número de URLs. $T_{avg}$ é o tempo médio de uma requisição. |
| **Coleta Paralela** | $O((N/W) \cdot T_{avg} + T_{wait})$ | $W$ é `MAX_WORKERS`. O tempo total é drasticamente reduzido, sendo limitado pelo *overhead* e pela requisição mais lenta ($T_{wait}$). |
| **Desduplicação (Pandas)** | $O(N \cdot log(N))$ | Onde $N$ é o número total de URLs nas fontes. A desduplicação é eficiente devido às otimizações do Pandas. |

### 4.3. Impacto de Aumentar MAX\_WORKERS (Ex: 30)

  * **Vantagem:** Reduz o tempo de execução.
  * **Perigo:** Aumentar demais resulta em *overhead* de gerenciamento de *threads* e pode causar bloqueios por parte dos servidores alvo, levando a erros **429 (Too Many Requests)**.

## 5\. Funcionamento Macro do Sistema (Excluindo Entrega 2)

O diagrama de fluxo de trabalho mostra o caminho dos dados, desde a entrada em CSV até a persistência do *log* e a compactação final dos HTMLs.

### 5.1. Desenho do Fluxo

```mermaid
graph TD
    subgraph Fase 1: Inicialização
        A[Coletor.py (Launcher)] --> B(Inicializa Logger e sys.path);
        B --> C[processador.py: main()];
    end

    subgraph Fase 2: Preparação de Dados (Processador)
        C --> D[Leitura CSVs & Concatenação];
        D --> E[Desduplicação (URLs Únicas)];
        E --> F[Filtro: Ignora URLs já Coletadas];
        F --> G{Lista Final de URLs};
    end

    subgraph Fase 3: Coleta Paralela (I/O Bound)
        G --> H[ThreadPoolExecutor (MAX_WORKERS)];
        H --> I(Worker N: Verificador.download_url);
        I -- Sucesso (Status 2xx) --> J[Salva Arquivo em html_pages_temp/];
        I -- Falha (Status 4xx/Timeout) --> K[Não Salva Arquivo];
        K --> L[Loga ERROR/CRITICAL em coletor_run_*.log];
        J --> L;
        J --> M[Registra Linha no logs/collection_log.csv];
        K --> M;
    end
    
    subgraph Fase 4: Pós-Processamento e Finalização
        M --> N[GeradorRelatorio];
        N --> O[Cria relatorio_erros.csv];
        O --> P[finalize_collection];
        P --> Q[Compacta html_pages_temp/ para coletas_compactadas/*.zip];
        Q --> R[Limpa Pasta Temporária (shutil.rmtree)];
    end
```

### 5.2. Espaço para Inserção de Imagem

![Fluxograma técnico detalhando o processo do Coletor Web Modular, apresentando quatro fases distintas: inicialização do sistema, preparação dos dados, coleta paralela com threads, e pós-processamento. O diagrama usa conectores e caixas em tons neutros para mostrar a sequência lógica das operações, desde a entrada dos dados até a compactação final dos arquivos HTML coletados](./images/fluxo_previsto.png)
