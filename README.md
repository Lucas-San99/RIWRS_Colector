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
| **Windows** | 1. Baixe o instalador em [python.org](https://www.python.org/). 2. **CRÍTICO:** Marque a caixa **"Add Python to PATH"**. |
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

### 2.4. Instalação das Dependências

*(Esta seção se torna redundante no Windows se o .bat for usado, mas é mantida para Linux/macOS ou se o usuário quiser verificar)*

Com o ambiente ativado, instale as bibliotecas necessárias:

```bash
# Use este comando apenas se o setup.bat não foi executado ou falhou:
pip install pandas requests tqdm nltk beautifulsoup4
```
-----

## 3\. Estrutura e Modularidade do Projeto

O projeto adota uma estrutura profissional com o código-fonte principal isolado na pasta `src/`.

### 3.1. Estrutura de Diretórios

```diff
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
│   ├── SearchEngine.py  <-- Motor de Busca (Etapa 4)
│   ├── Diagnostico.py   <-- Ferramenta de "Health Check" do sistema
│   └── Relatorio.py     <-- Geração de relatórios de coleta
└── README.md
```

### 3.2. Funções dos Módulos

| Arquivo/Classe | Responsabilidade Principal |
| :--- | :--- |
| **`Coletor.py`** | Ponto de entrada (Launcher). Orquestra a execução das etapas através de um menu interativo ou argumentos de linha de comando. |
| **`src/Config.py`** | Centraliza todos os caminhos de pastas (`logs`, `datasets`, etc.) para fácil manutenção. |
| **`src/Processor.py`** | **Etapa 1:** Orquestra a leitura de URLs, desduplicação e o processo de coleta paralela. |
| **`src/Verificador.py`** | Lógica de **Download** de URL, tratamento de erros HTTP e salvamento do HTML. |
| **`src/Indexador.py`** | **Etapa 2:** Processa os HTMLs, realiza limpeza (PLN), tokenização e constrói o **índice invertido** e o mapa de documentos. |
| **`src/CalculaIDF.py`** | **Etapa 3:** Calcula o **IDF** para cada termo do vocabulário, usando os artefatos da Etapa 2. |
| **`src/SearchEngine.py`**| **Etapa 4:** Provê a funcionalidade de busca TF-IDF, utilizando todos os artefatos gerados. |
| **`src/Logging.py`** | Configuração do sistema de log (cria a pasta `logs/` e gera arquivos com *timestamp*). |
| **`src/Relatorio.py`** | Gera relatórios CSV consolidados (sucesso/erro) após a coleta. |
| **`src/Diagnostico.py`**| Ferramenta de "Health Check" que verifica a saúde e consistência de todos os artefatos gerados. |

-----

## 4\. Configuração Necessária

As configurações são definidas no arquivo **`src/processador.py`**.

### 4.1. Ajuste de Caminhos (`DATASETS_DIR`)

Você **DEVE** ajustar o caminho absoluto para sua pasta de dados:

```python
# NO ARQUIVO: src/processador.py
# ...
# Configurando caminho para os datasets 
# >>> AJUSTE O CAMINHO ABSOLUTO AQUI <<<
DATASETS_DIR = r'E:\Documentos\RIWRS_2\RIWRS\TP-Coletor\datasets' 
# Exemplo Linux: DATASETS_DIR = '/home/usuario/caminho/datasets'

# ... (restante dos arquivos em URL_FILES)
```

### 4.2. Ajuste de Parâmetros de Desempenho (Processor.py)

| Variável | Propósito | Dica de Ajuste |
| :--- | :--- | :--- |
| `MAX_WORKERS` | Threads paralelas para download. | **Reduza (ex: 10-15)** se encontrar muitos erros **429** (Too Many Requests). |
| `TIMEOUT_SECONDS` | Tempo máximo de espera por URL. | **Aumente (ex: 30)** se encontrar muitos erros de **Timeout** em servidores lentos. |

-----

## 5\. Execução e Acompanhamento de Logs

### 5.1. Execução

Rode o script principal a partir da **raiz** do projeto (`TP-Coletor/`):

```bash
(venv) $ python Coletor.py
```

### 5.2. Acompanhamento e Saídas

Todos os arquivos de saída (logs de execução e relatórios de resultados) são salvos na pasta **`logs/`**.

| Arquivo/Localização | Conteúdo e Natureza | Propósito |
| :--- | :--- | :--- |
| **Console/Terminal** | Mensagens INFO (progresso), e **ERROR/CRITICAL** (falhas) em tempo real. | Monitoramento imediato. |
| **`logs/coletor_run_*.log`** | **Log de Execução com Timestamp.** Contém a saída completa do console, incluindo o **Status Code** e a URL exata da falha. | Auditoria de execução e diagnóstico de erros de rede. |
| **`logs/collection_log.csv`** | **Log Mestre de Resultados (Cumulativo).** Registro estruturado de todas as tentativas feitas até hoje. **Local de Armazenamento Final**. | Fonte de dados persistente. |
| **`logs/relatorio_erros.csv`** | **Relatório Final Filtrado.** Contém apenas as URLs que resultaram em erro (`ERROR` ou `FATAL_ERROR`). | Análise estatística da taxa de falhas. |
| **`logs/error_log.txt`** | **Lista de Erros da Sessão.** Simples lista de URLs que falharam na última execução. | Entrada para uma nova tentativa de coleta (retry). |
| **`coletas_compactadas/*.zip`** | **Arquivos HTML Coletados.** | Artefato final da coleta bem-sucedida. |

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