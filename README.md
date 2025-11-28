# Sistema de Recuperação de Informação para URLs de Phishing (RIWRS)

Este projeto é uma implementação completa de um sistema de Recuperação de Informação (RI) focado no domínio de segurança (URLs de *phishing*). O sistema opera de ponta a ponta, desde a coleta distribuída de páginas web até a disponibilização de um motor de busca com ranqueamento semântico.

O núcleo do sistema baseia-se no **Modelo Vetorial**, utilizando o esquema de ponderação **TF-IDF** e a métrica de **Similaridade do Cosseno** para ordenar os resultados por relevância em relação a consultas em linguagem natural.

Uma característica arquitetural chave é o **armazenamento híbrido do índice invertido**. Para lidar com o grande volume de dados textuais extraídos, o índice é particionado entre memória RAM (para metadados de acesso rápido) e armazenamento em SSD (para o corpo volumoso das listas de postagens em formato binário), garantindo buscas de baixa latência.

-----

## 1\. Contexto Acadêmico e Equipe

Projeto desenvolvido como requisito prático da disciplina de **Recuperação de Informação na Web e Redes Sociais**, ministrada pelo [**Dr. Pedro Felipe**](https://www.linkedin.com/in/pedro-felipe-oliveira-8041ab12/?originalSubdomain=br). O objetivo pedagógico é a aplicação prática dos conceitos teóricos de RI em um cenário de *Big Data*.

### **Desenvolvedores e Módulos:**

* **Ana Clara** (@anacontarini): Desenvolvimento da Interface Gráfica (Tkinter), Desenvolvimento de busca por linha de comando (CLI) e integração do fluxo de busca visual.
* **Ana Paula** (@apoliveirapuc): Implementação do núcleo de ranqueamento (Modelo Vetorial e Similaridade do Cosseno).
* **Camille** (@CamilleIrias): Processamento de Linguagem Natural (PLN) da consulta e geração de vetores de busca.
* **Luana** (@Luana-Almeid): Arquitetura de indexação.
* **Lucas Lima** (@Lucas-San99): Sistema de mapeamento eficiente de resultados (DocID $\leftrightarrow$ URL), apoio no Desenvolvimento da Interface Gráfica (Tkinter), otimização de armazenamento (SSD binário) e mecanismos de busca de baixo nível.
* **Osvaldo Neto** (@osvaldoferreiraf): Cálculo estatístico global do corpus (Inverse Document Frequency - IDF).

-----

## 2\. Instalação e Configuração do Ambiente

O projeto foi desenhado para ambientes Windows, com um script de automação que prepara todo o ecossistema necessário.

### 2.1. Pré-requisitos do Sistema

  * **Sistema Operacional:** Windows 10 ou Superior (recomendado para uso do `setup.bat`).
  * **Python:** Versão 3.8 ou superior instalada e corretamente adicionada às variáveis de ambiente (PATH).
  * **Espaço em Disco:** Mínimo de 15 GB livres (caso execute a coleta completa) ou 2 GB (caso utilize apenas os índices pré-processados).

### 2.2. Processo de Instalação Automatizada

O script `setup.bat` na raiz do projeto automatiza a configuração. Ele realiza as seguintes ações sequenciais:

1.  **Verificação do Python:** Confirma se o interpretador está acessível.
2.  **Criação do Ambiente Virtual:** Gera um diretório `venv/` para isolar as bibliotecas do projeto.
3.  **Atualização de Ferramentas:** Atualiza o `pip` e o `setuptools` para as versões mais recentes.
4.  **Instalação de Dependências:** Instala as bibliotecas listadas em `requirements.txt` (ex: `nltk`, `beautifulsoup4`, `tqdm`, `numpy`, `requests`).
5.  **Download de Recursos de PLN:** Baixa automaticamente os corpora necessários do NLTK (tokenizadores `punkt` e lista de `stopwords`).
6.  **Verificação de Migração:** Se os índices brutos já existirem, sugere ou executa a migração para o formato otimizado.

**Para executar:**

1.  Abra o terminal na pasta raiz do projeto.
2.  Execute: `.\setup.bat`
3.  Após a conclusão, ative o ambiente: `.\venv\Scripts\activate`

-----

## 3\. Arquitetura de Arquivos e Artefatos de Dados

A estrutura do projeto separa logicamente o código-fonte, as ferramentas utilitárias e, crucialmente, os dados gerados.

```bash
RIWRS_2/
│
├── Coletor.py                  # Ponto de entrada (Launcher) da aplicação.
├── setup.bat                   # Automação de ambiente Windows.
├── requirements.txt            # Dependências do Python.
│
├── logs/                       # DIRETÓRIO CRÍTICO: Contém todos os dados do sistema.
│   │   # --- Artefatos da Camada Quente (RAM) ---
│   ├── document_map.json       # Hashmap que traduz DocIDs inteiros para URLs originais.
│   ├── idf.json                # Dicionário com o peso IDF pré-calculado para cada termo.
│   ├── vocabulario.json        # Metadados críticos: mapeia cada termo para seu offset (posição) e tamanho no arquivo binário.
│   │
│   │   # --- Artefatos da Camada Fria (SSD) ---
│   ├── postings.bin            # Arquivo binário denso contendo as listas de postagens compactadas.
│   │
│   │   # --- Artefatos de Construção/Legado ---
│   ├── indice_invertido.json   # Índice monolítico original (JSON gigante). Usado apenas como fonte para migração.
│   ├── collection_log.csv      # Registro mestre do status de coleta de cada URL.
│   └── temp_html/              # (Opcional) Armazenamento temporário dos arquivos HTML brutos.
│
├── src/                        # Código-fonte principal (Core).
│   ├── CalculaIDF.py           # Módulo para cálculo estatístico do IDF global.
│   ├── CLI.py                  # Interface de Linha de Comando.
│   ├── Config.py               # Centralização de caminhos e constantes.
│   ├── GUI.py                  # Interface Gráfica (Tkinter) com gestão de estado e paginação.
│   ├── Indexador.py            # Pipeline de processamento de HTML e geração do índice bruto.
│   ├── Processor.py            # Motor de coleta multithreaded.
│   ├── SearchEngine.py         # Backend do motor de busca (orquestrador de ranking e I/O).
│   └── ...
│
└── tools/                      # Ferramentas auxiliares.
    └── MigrarIndice.py         # Script crítico que converte o índice JSON monolítico para o formato híbrido RAM/SSD.
```

-----

## 4\. Pipeline de Dados e Execução

O sistema opera em um fluxo de dados estrito. A execução fora de ordem resultará em falhas por falta de artefatos.

### 4.1. O Pipeline de Processamento (ETAPAS 1-4)

Para construir o motor de busca do zero, as seguintes etapas devem ser executadas sequencialmente através do menu principal (`python Coletor.py` -\> Opção 1).

#### **ETAPA 1: Coleta e Pós-processamento**

  * **Entrada:** Listas de URLs (CSVs em `datasets/`).
  * **Processo:** Utiliza `ThreadPoolExecutor` para baixar páginas HTML em paralelo, respeitando *timeouts*.
  * **Saída:** Arquivos HTML brutos em `logs/temp_html/` e atualização do log mestre `collection_log.csv`.

#### **ETAPA 2: Indexação (Geração do Índice Monolítico)**

  * **Entrada:** Arquivos HTML em `logs/temp_html/`.
  * **Processo:**
    1.  *Parsing* do HTML (BeautifulSoup) para extrair apenas texto visível.
    2.  *Pipeline de PLN:* Tokenização, normalização (lowercase), remoção de *stopwords* (NLTK) e *stemming* (SnowballStemmer português).
    3.  Construção do índice invertido em memória.
  * **Saída:** Um arquivo JSON monolítico gigante (`indice_invertido.json`) e o mapa de documentos (`document_map.json`).

#### **ETAPA 3: Cálculo de IDF Global**

  * **Entrada:** O índice gigante (`indice_invertido.json`).
  * **Processo:** Leitura incremental (streaming via `ijson`) do índice para calcular a frequência de documento ($df$) de cada termo e aplicar a fórmula do IDF: $\log(N / df_t)$.
  * **Saída:** O arquivo `idf.json` contendo os pesos globais dos termos.

#### **ETAPA 4: Migração e Otimização (Arquitetura RAM/SSD)**

  * **Motivação:** O índice JSON da Etapa 2 é grande demais (ex: 4.6 GB) para ser carregado na RAM para buscas.
  * **Processo (Script `tools/MigrarIndice.py`):**
    1.  Lê o `indice_invertido.json` via streaming.
    2.  Serializa as listas de postagens em formato binário compacto e as escreve sequencialmente em `postings.bin` (SSD).
    3.  Registra a posição exata (offset em bytes) e o tamanho de cada lista no arquivo `vocabulario.json` (RAM).
  * **Saída:** Os artefatos finais otimizados para o motor de busca: `postings.bin` e `vocabulario.json`.

-----

## 5\. Utilização do Motor de Busca

Após a conclusão do pipeline de dados (ou a extração do `logs.zip`), o sistema oferece duas interfaces de interação. Ambas utilizam o mesmo backend (`src/SearchEngine.py`), que gerencia o carregamento dos metadados na RAM e o acesso cirúrgico ao SSD.

### 5.1. Interface Gráfica (GUI - Recomendada)

Acessível via **Opção [7]** do menu principal.

  * **Funcionalidades:**
      * Barra de busca central para consultas em linguagem natural.
      * **Paginação Real:** Permite navegar por todo o conjunto de resultados recuperados, não apenas os top-10.
      * **Links Interativos:** As URLs nos resultados são clicáveis e abrem no navegador padrão do sistema.
      * **Métricas:** Exibe o tempo total da consulta (backend + renderização) e o número total de documentos encontrados.
  * **Gestão de Recursos:** Implementa um protocolo de fechamento (`WM_DELETE_WINDOW`) que força a liberação explícita da memória RAM (via `gc.collect()`) e o fechamento de descritores de arquivo ao sair da aplicação.

### 5.2. Interface de Linha de Comando (CLI)

Acessível via **Opção [6]** do menu principal.

  * Oferece um loop de busca interativo no terminal, ideal para testes rápidos ou ambientes sem interface gráfica. Exibe resultados ranqueados com score de relevância e URL.

-----

## 6\. Dados Pré-processados (`logs.zip`)

Para viabilizar a avaliação imediata do sistema sem a necessidade de executar o longo processo de coleta e indexação (que pode levar horas e consumir dezenas de gigabytes), fornecemos um arquivo compactado com os artefatos finais.

### Instruções Críticas de Uso:

1.  Obtenha o arquivo `logs.zip`.
2.  Extraia o conteúdo deste arquivo **diretamente na raiz** do projeto `RIWRS_2/`.
3.  **Verificação:** Após a extração, você **NÃO** deve ter uma pasta `logs` dentro de outra pasta `logs` (ex: `RIWRS_2/logs/logs/`). A estrutura correta deve ser:
      * `RIWRS_2/logs/document_map.json`
      * `RIWRS_2/logs/postings.bin`
      * etc.

Se os arquivos estiverem na estrutura correta, as interfaces de busca (Opções 6 e 7) funcionarão imediatamente.

-----

## 7\. Créditos e Atribuições

### Provedores das tabelas analisadas
 Agradecemos aos provedores dos conjuntos de dados utilizados:
  * **Dataset 1:** Phishing Site URLs
      * **Provedor:** Tarun Tiwari (Kaggle)
      * **Fonte:** [Kaggle - Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)
  * **Dataset 2:** Phishing Site URLs
      * **Provedor:** Mohammad A. Jaber (Mendeley)
      * **Fonte:** [Mendeley Data - Phishing Site URLs](https://data.mendeley.com/datasets/vfszbj9b36/1)
### Assistência de Inteligência Artificial
O desenvolvimento deste projeto utilizou ferramentas de Inteligência Artificial Generativa (Google Gemini) como assistente de programação.
A IA foi empregada nas seguintes tarefas:
1.  **Refatoração e Padronização:** Otimização da estrutura modular do projeto e adequação do código aos padrões de estilo (PEP 8).
2.  **Debugging e Resolução de Erros:** Análise e sugestão de correções para exceções complexas, como problemas de paralelismo e concorrência no *multithreading*.
3.  **Documentação:** Auxílio na estruturação e formatação de arquivos de documentação técnica (`README.md`, `.gitignore`, `DELIVERABLES.md`).
A autoria e as decisões de arquitetura e implementação de todas as funcionalidades de coleta e indexação são de responsabilidade dos autores.