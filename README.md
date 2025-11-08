# Coletor e Analisador de Páginas Web (Phishing)

Este é um projeto modular e robusto desenvolvido para baixar páginas HTML a partir de múltiplas fontes de URLs (CSVs). Ele utiliza o processamento paralelo (`ThreadPoolExecutor`) para melhor eficiência, automatiza a desduplicação de URLs e mantém um sistema de logs e relatórios persistente.

-----

## 1\. Autoria e Contexto Acadêmico

Este programa foi desenvolvido como parte das atividades práticas da disciplina de **Recuperação de Informação na Web e Redes Sociais**.

| Detalhe | Informação |
| :--- | :--- |
| **Disciplina** | Recuperação de Informação na Web e Redes Sociais |
| **Professor** | [**Dr. Pedro Felipe**](https://www.linkedin.com/in/pedro-felipe-oliveira-8041ab12/?originalSubdomain=br) |
| **Motivação** | Praticar a criação e aplicação de coletores de páginas web. |

### **Desenvolvedores:**

  * **Ana Clara** (@anacontarini)
  * **Ana Paula** (@apoliveirapuc)
  * **Camille** (@CamilleIrias)
  * **Luana** (@Luana-Almeid)
  * **Lucas Lima** (@Lucas-San99)
  * **Osvaldo Neto** (@osvaldoferreiraf)

-----

## 2\. Configuração Inicial do Ambiente

### 2.1. Instalação do Python 3

| Sistema Operacional | Instruções |
| :--- | :--- |
| **Windows** | 1. Baixe o instalador em [python.org]. 2. **CRÍTICO:** Marque a caixa **"Add Python to PATH"**. |
| **macOS** | Use o Homebrew: `brew install python` |
| **Linux** | Use o gerenciador de pacotes: `sudo apt update && sudo apt install python3 python3-pip` |

### 2.2. Automação da Configuração (Windows com `setup.bat`)

Para usuários de Windows, o projeto inclui um script `setup.bat` que automatiza todo o processo de configuração.

**O que o `setup.bat` faz?**
1.  **Cria um Ambiente Virtual:** Isola as dependências do projeto em uma pasta `venv/`, evitando conflitos com outras instalações Python no seu sistema.
2.  **Ativa o Ambiente:** Prepara o terminal para usar o Python e as bibliotecas contidas no `venv/`.
3.  **Atualiza o `pip`:** Garante que o instalador de pacotes do Python esteja na sua versão mais recente.
4.  **Instala e Atualiza as Dependências:** Instala todas as bibliotecas necessárias para o projeto (`pandas`, `requests`, `tqdm`, `beautifulsoup4`, `nltk`, `ijson`) e as atualiza para as versões mais recentes disponíveis. Isso garante que o projeto sempre rode com as últimas correções e funcionalidades das bibliotecas.

**Como usar:**
1.  Abra um terminal (Prompt de Comando ou PowerShell) na pasta raiz do projeto.
2.  Execute o script:
    ```bash
    .\setup.bat
    ```
3.  Após a execução, o ambiente estará pronto. Para começar a usar, ative o ambiente virtual no seu terminal com o comando:
    ```bash
    .\venv\Scripts\activate
    ```

### 2.3. Criação e Ativação do Ambiente Virtual (Manual para Outros SOs / Pós-Setup)

Se estiver em Linux/macOS ou se o `.bat` não ativou o ambiente em seu terminal:

```bash
# Cria o ambiente virtual (Se não foi feito pelo .bat)
python3 -m venv venv 

# Ativa o ambiente (Windows)
.\venv\Scripts\activate
# Ativa o ambiente (Linux/macOS)
# source venv/bin/activate
```

### 2.4. Instalação Manual das Dependências (Linux/macOS ou Pós-Setup)

Se você não está no Windows ou prefere fazer a instalação manualmente, siga estes passos após criar e ativar o ambiente virtual:

1.  **Atualize o `pip`:**
    ```bash
    pip install --upgrade pip
    ```
2.  **Instale as bibliotecas:**
    ```bash
    pip install --upgrade pandas requests tqdm beautifulsoup4 nltk ijson
    ```
Este comando também pode ser usado para atualizar as dependências para suas versões mais recentes a qualquer momento.
-----

## 3. Estrutura e Modularidade do Projeto

O projeto adota uma estrutura profissional com o código-fonte principal isolado na pasta `src/`.

### 3.1. Estrutura de Diretórios

```
RIWRS_2/
├── Coletor.py           <-- ARQUIVO DE EXECUÇÃO (Launcher)
├── setup.bat            <-- Script de instalação para Windows
├── venv/                # Ignorado no .gitignore
├── datasets/            # Pasta OBRIGATÓRIA com os CSVs de origem
├── logs/                # Pasta de saída para logs e artefatos (índices, IDFs)
├── html_pages_temp/     # Armazenamento temporário de HTMLs baixados
├── coletas_compactadas/ # Arquivos .zip com as coletas finalizadas
├── src/                 # Diretório do código-fonte (pacote)
│   ├── Config.py        <-- Configurações centralizadas (caminhos)
│   ├── Logging.py       <-- Configuração do Logger
│   ├── Verificador.py   <-- Lógica de Download de URL
│   ├── Processor.py     <-- Orquestrador da Coleta (Etapa 1)
│   ├── Indexador.py     <-- Representação e Indexação (Etapa 2)
│   ├── CalculaIDF.py    <-- Cálculo de IDF (Etapa 3)
│   ├── SearchEngine.py  <-- Motor de Busca (Etapa 3)
│   ├── Diagnostico.py   <-- Scripts de verificação e contagem
│   └── Relatorio.py     <-- Geração de relatórios de coleta
└── README.md
```

### 3.2. Funções dos Módulos

| Arquivo/Classe | Responsabilidade Principal |
| :--- | :--- |
| **`Coletor.py`** | Ponto de entrada (Launcher). Orquestra a execução das etapas (Coleta, Indexação, etc.). |
| **`src/Config.py`** | Centraliza todos os caminhos de pastas (`logs`, `datasets`, etc.) para fácil manutenção. |
| **`src/Processor.py`** | **Etapa 1:** Orquestra a leitura de URLs, desduplicação e o processo de coleta paralela. |
| **`src/Verificador.py`** | Lógica de **Download** de URL, tratamento de erros HTTP e salvamento do HTML. |
| **`src/Indexador.py`** | **Etapa 2:** Processa os HTMLs, realiza limpeza (PLN), tokenização e constrói o **índice invertido** e o mapa de documentos. |
| **`src/CalculaIDF.py`** | **Etapa 3.1:** Calcula o **IDF** para cada termo do vocabulário, usando os artefatos da Etapa 2. |
| **`src/SearchEngine.py`**| **Etapa 3.2:** Provê a funcionalidade de busca, incluindo o mapeamento de DocIDs para URLs. |
| **`src/Logging.py`** | Configuração do sistema de log (cria a pasta `logs/` e gera arquivos com *timestamp*). |
| **`src/Relatorio.py`** | Gera relatórios CSV consolidados (sucesso/erro) após a coleta. |
| **`src/Diagnostico.py`**| Ferramenta auxiliar para contagem e verificação dos resultados da coleta. |

-----

## 4. Configuração

As configurações principais foram centralizadas para facilitar a manutenção.

### 4.1. Caminhos de Pastas (`src/Config.py`)

Todas as pastas importantes (logs, datasets, etc.) são definidas em `src/Config.py`. **Não é necessário alterar este arquivo** se você mantiver a estrutura de pastas padrão.

### 4.2. Caminho dos Datasets (`src/Processor.py`)

Você **DEVE** ajustar o caminho absoluto para a sua pasta de datasets no arquivo `src/Processor.py`:

```python
# NO ARQUIVO: src/Processor.py
# ...
# Configurando caminho para os datasets
# >>> AJUSTE O CAMINHO ABSOLUTO AQUI <<<
DATASETS_DIR = r'E:\Documentos\RIWRS_2\datasets' 
# Exemplo Linux: DATASETS_DIR = '/home/usuario/caminho/datasets'
```

### 4.3. Parâmetros de Desempenho (`src/Processor.py`)

Ajuste os parâmetros de desempenho da coleta no mesmo arquivo:

| Variável | Propósito | Dica de Ajuste |
| :--- | :--- | :--- |
| `MAX_WORKERS` | Threads paralelas para download. | **Reduza (ex: 10-15)** se encontrar muitos erros **429** (Too Many Requests). |
| `TIMEOUT_SECONDS` | Tempo máximo de espera por URL. | **Aumente (ex: 30)** se encontrar muitos erros de **Timeout** em servidores lentos. |

-----

## 5. Execução das Etapas

O `Coletor.py` agora orquestra a execução de todas as etapas do projeto.

### 5.1. Etapa 1: Coleta

Executa a coleta de páginas HTML.

```bash
(venv) $ python Coletor.py --etapa coleta
```

### 5.2. Etapa 2: Indexação

Processa os HTMLs baixados, constrói e salva o índice invertido e o mapa de documentos.

```bash
(venv) $ python Coletor.py --etapa indexacao
```

### 5.3. Etapa 3: Cálculo de IDF

Calcula o IDF para todos os termos do vocabulário.

```bash
(venv) $ python Coletor.py --etapa idf
```

### 5.4. Etapa 4: Diagnóstico (Opcional)

Roda um script que conta o total de páginas coletadas com sucesso.

```bash
(venv) $ python Coletor.py --etapa diagnostico
```

### 5.5. Execução Completa (Todas as Etapas em Ordem)

Para executar todas as etapas em sequência (coleta, indexação e cálculo de IDF):

```bash
(venv) $ python Coletor.py --etapa todas
```

-----

## 6. Acompanhamento e Saídas

Todos os arquivos de saída, incluindo logs e artefatos de indexação, são salvos na pasta **`logs/`**.

| Arquivo/Localização | Conteúdo e Natureza | Propósito |
| :--- | :--- | :--- |
| **Console/Terminal** | Mensagens de progresso (INFO) e erros (ERROR/CRITICAL) em tempo real. | Monitoramento imediato da execução. |
| **`logs/coletor_run_*.log`** | **Log de Execução:** Saída completa do console, com *timestamp*. | Auditoria detalhada e diagnóstico de falhas. |
| **`logs/collection_log.csv`** | **Log Mestre de Coleta:** Registro cumulativo de todas as tentativas de download. | Fonte de dados persistente sobre a coleta. |
| **`logs/relatorio_sucesso.csv`** | **Relatório de Sucesso:** CSV filtrado apenas com as URLs baixadas com sucesso. | Análise de resultados positivos. |
| **`logs/relatorio_erros.csv`** | **Relatório de Erros:** CSV filtrado apenas com as URLs que falharam. | Análise da taxa e dos motivos de falha. |
| **`logs/indice_invertido.json`**| **Índice Invertido:** Estrutura de dados principal para a busca. Mapeia termos para os documentos onde ocorrem. | **Artefato da Etapa 2.** Essencial para o motor de busca. |
| **`logs/document_map.json`** | **Mapa de Documentos:** Dicionário que mapeia um `DocID` (int) para a `URL` original. | **Artefato da Etapa 2.** Usado para apresentar os resultados da busca. |
| **`logs/idf.json`** | **Pesos IDF:** Dicionário que mapeia cada termo do vocabulário ao seu valor de IDF. | **Artefato da Etapa 3.** Usado para calcular o ranking de relevância (TF-IDF). |
| **`coletas_compactadas/*.zip`** | **Arquivos HTML Coletados:** Backup compactado dos arquivos HTML baixados. | Arquivamento dos dados brutos. |

-----

## 6\. Agradecimentos e Assistência Técnica

### 6.1. Agradecimentos (Dataset Providers)

Agradecemos aos provedores dos conjuntos de dados utilizados:

  * **Dataset 1:** Phishing Site URLs

      * **Provedor:** Tarun Tiwari (Kaggle)
      * **Fonte:** [Kaggle - Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)

  * **Dataset 2:** Phishing Site URLs

      * **Provedor:** Mohammad A. Jaber (Mendeley)
      * **Fonte:** [Mendeley Data - Phishing Site URLs](https://data.mendeley.com/datasets/vfszbj9b36/1)

### 6.2. Assistência de Inteligência Artificial

O desenvolvimento deste projeto utilizou ferramentas de Inteligência Artificial Generativa (Google Gemini) como assistente de programação.

A IA foi empregada nas seguintes tarefas:

1.  **Refatoração e Padronização:** Otimização da estrutura modular do projeto e adequação do código aos padrões de estilo (PEP 8).
2.  **Debugging e Resolução de Erros:** Análise e sugestão de correções para exceções complexas, como problemas de paralelismo e concorrência no *multithreading*.
3.  **Documentação:** Auxílio na estruturação e formatação de arquivos de documentação técnica (`README.md`, `.gitignore`, `DELIVERABLES.md`).

A autoria e as decisões de arquitetura e implementação de todas as funcionalidades de coleta e indexação são de responsabilidade dos autores.