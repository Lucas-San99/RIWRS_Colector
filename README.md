# Coletor e Analisador de Páginas Web (Phishing)

Este é um projeto modular e robusto desenvolvido para baixar páginas HTML a partir de múltiplas fontes de URLs (CSVs). Ele utiliza o processamento paralelo (`ThreadPoolExecutor`) para alta eficiência, automatiza a desduplicação de URLs e mantém um sistema de logs e relatórios persistente.

-----

## 1. Autoria e Contexto Acadêmico

Este programa foi desenvolvido como parte das atividades práticas da disciplina de **Recuperação de Informação na Web e Redes Sociais**.

| Detalhe | Informação |
| :--- | :--- |
| **Disciplina** | Recuperação de Informação na Web e Redes Sociais |
| **Professor** | [**Dr. Pedro Felipe**](https://www.linkedin.com/in/pedro-felipe-oliveira-8041ab12/?originalSubdomain=br) |
| **Motivação** | Praticar a criação e aplicação de coletores de páginas web.  |

### **Desenvolvedores:**

* **Ana Clara** (@anacontarini)
* **Ana Paula** (@)
* **Camille** (@CamilleIrias)
* **Luana** (@Luana-Almeid)
* **Lucas Lima** (@Lucas-San99)
* **Osvaldo Neto** (@osvaldoferreiraf)

-----

## 2. Configuração Inicial do Ambiente

### 2.1. Instalação do Python 3

| Sistema Operacional | Instruções |
| :--- | :--- |
| **Windows** | 1. Baixe o instalador em [python.org]. 2. **CRÍTICO:** Marque a caixa **"Add Python to PATH"**. |
| **macOS** | Use o Homebrew: `brew install python` |
| **Linux** | Use o gerenciador de pacotes: `sudo apt update && sudo apt install python3 python3-pip` |

### 2.2. Criação e Ativação do Ambiente Virtual (Obrigatório)

Execute estes comandos na pasta raiz do projeto (`TP-Coletor/`):

```bash
# 1. Cria o ambiente virtual
python3 -m venv venv 

# 2. Ativa o ambiente (Windows)
.\venv\Scripts\activate
# 2. Ativa o ambiente (Linux/macOS)
# source venv/bin/activate
```

### 2.3. Instalação das Dependências

Com o ambiente ativado, instale as bibliotecas necessárias:

```bash
pip install pandas requests tqdm
```

-----

## 3. Estrutura e Modularidade do Projeto

O projeto adota uma estrutura profissional com o código-fonte principal isolado na pasta `src/`.

### 3.1. Estrutura de Diretórios

```
TP-Coletor/
├── Coletor.py           <-- ARQUIVO DE EXECUÇÃO (Launcher)
├── venv/
├── datasets/            # Pasta OBRIGATÓRIA com os CSVs de origem
├── logs/                # Pasta de saída para logs e relatórios CSV
├── src/                 # Diretório do código-fonte (pacote)
│   ├── __init__.py
│   ├── processador.py   <-- Lógica principal (onde a orquestração ocorre)
│   ├── Verificador.py   <-- Classe de Download
│   ├── Relatorio.py     <-- Classe de Geração de Relatórios
│   └── Logging.py       <-- Configuração do Logger
└── README.md
```

### 3.2. Funções dos Módulos

| Arquivo/Classe | Responsabilidade Principal |
| :--- | :--- |
| **`Coletor.py`** | Ponto de entrada (Launcher). Inicializa o ambiente e chama a lógica de `src/`. |
| **`src/processador.py`** | Orquestração, leitura de dados, desduplicação e controle do ciclo de coleta. |
| **`src/Verificador.py`** | Lógica de **Download** de URL e registro de erros de Status HTTP (4xx, 5xx) em tempo real. |
| **`src/Logging.py`** | Configuração do sistema de log (cria a pasta `logs/` e gera arquivos com *timestamp*). |

-----

## 4. Configuração Necessária

As configurações são definidas no arquivo **`src/processador.py`**.

### 4.1. Ajuste de Caminhos (`DATASETS_DIR`)

O módulo `processador.py` calcula automaticamente a raiz do projeto. No entanto, você deve garantir que o caminho absoluto para a pasta `datasets` esteja correto.

```python
# NO ARQUIVO: src/processador.py
# ...
# Configurando caminho para os datasets 
# >>> AJUSTE O CAMINHO ABSOLUTO AQUI <<<
DATASETS_DIR = r'E:\Documentos\RIWRS_2\RIWRS\TP-Coletor\datasets' 
# Exemplo Linux: DATASETS_DIR = '/home/usuario/caminho/datasets'

# ... (restante dos arquivos em URL_FILES)
```

### 4.2. Ajuste de Parâmetros de Desempenho

| Variável | Propósito | Dica de Ajuste |
| :--- | :--- | :--- |
| `MAX_WORKERS` | Threads paralelas para download. | **Reduza (ex: 10-15)** se encontrar muitos erros **429** (Too Many Requests). |
| `TIMEOUT_SECONDS` | Tempo máximo de espera por URL. | **Aumente (ex: 30)** se encontrar muitos erros de **Timeout** em servidores lentos. |

-----

## 5. Execução e Acompanhamento de Logs

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

## 6\. Agradecimentos (Dataset Providers)

Agradecemos aos provedores dos conjuntos de dados utilizados:

  * **Dataset 1:** Phishing Site URLs

      * **Provedor:** Tarun Tiwari (Kaggle)
      * **Fonte:** [Kaggle - Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)

  * **Dataset 2:** Phishing Site URLs

      * **Provedor:** Mohammad A. Jaber (Mendeley)
      * **Fonte:** [Mendeley Data - Phishing Site URLs](https://data.mendeley.com/datasets/vfszbj9b36/1)

<!-- end list -->

```
```