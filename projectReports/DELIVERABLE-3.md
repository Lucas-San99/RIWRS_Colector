# Funcionalidade de Cálculo de IDF (Inverse Document Frequency)

## Introdução

Como parte fundamental da Etapa 3 (Recuperação), foi implementado o módulo `CalculaIDF.py`, responsável por computar o **Inverse Document Frequency (IDF)** para cada termo do vocabulário. O IDF é uma métrica estatística que mensura a raridade e, consequentemente, a importância de um termo em toda a coleção de documentos. Este cálculo é um pré-requisito para a implementação de modelos de ranking avançados, como o TF-IDF.

## Mudanças Realizadas

1.  **Criação do Módulo `src/CalculaIDF.py`**: Um novo script dedicado exclusivamente ao cálculo dos pesos IDF.
2.  **Leitura de Artefatos**: O script consome dois arquivos gerados na etapa de indexação:
    *   `logs/indice_invertido.json`: Para obter a frequência de documentos (`df`) de cada termo.
    *   `logs/document_map.json`: Para obter o número total de documentos (`N`) na coleção.
3.  **Geração de Saída**: O resultado é persistido no arquivo `logs/idf.json`, que armazena um mapa `{ "termo": idf_value }`.
4.  **Robustez para Escalabilidade**: Implementado um mecanismo de *fallback* que utiliza a biblioteca `ijson` para processamento incremental. Essa abordagem garante que o cálculo possa ser executado mesmo com índices invertidos de grande volume (múltiplos gigabytes), que não caberiam inteiramente na memória RAM.

## Funcionamento e Fórmula

O processo segue uma lógica bem definida:

1.  **Obtenção de N**: O número total de documentos (`N`) é determinado pela contagem de entradas no `document_map.json`.
2.  **Processamento do Índice**: O script tenta carregar o `indice_invertido.json` em memória. Em caso de `MemoryError`, ativa o modo de leitura incremental com `ijson`.
3.  **Cálculo do IDF**: Para cada termo no índice, o script extrai sua frequência nos documentos (`df`) e aplica a fórmula padrão do Inverse Document Frequency:
   
   $$
   \text{IDF}(t) = \log\left(\frac{N}{df_t}\right)
   $$
   Onde `t` é o termo, `N` é o número total de documentos e `df_t` é o número de documentos que contêm o termo `t`. O uso do logaritmo suaviza a escala dos valores.

4.  **Persistência**: Os resultados são salvos em `logs/idf.json`.

## Como Interpretar o Resultado (`idf.json`)

O arquivo `idf.json` é um dicionário que mapeia cada termo ao seu valor de IDF. A interpretação é a seguinte:

### Interpretação dos valores de IDF
- **IDF Alto**: Indica que o termo é raro na coleção de documentos. Termos com IDF alto são excelentes para discriminar o conteúdo e possuem maior peso no cálculo de relevância.
- **IDF Baixo (próximo de 0)**: Indica que o termo é muito comum, aparecendo em uma grande fração dos documentos. Sua capacidade de distinção é baixa.
- **IDF igual a 0**: Ocorre quando um termo está presente em todos os documentos da coleção, tornando-o inútil para o ranking.

### Exemplo de uso
Se o termo "bradesco" possui um IDF alto, uma consulta contendo essa palavra retornará com maior prioridade os documentos que também a contenham. Em contrapartida, um termo como "login" (após stemming), que provavelmente aparece em muitas páginas, terá um IDF baixo e menor influência no score final.

---

**Autor:**
Osvaldo Neto @osvaldoferreiraf
Data da atualização: 08/11/2025

# Implementação do `SearchEngine.py` (Entrega 3)

### Objetivo

Esta tarefa adiciona o módulo de recuperação (Etapa 3) responsável por mapear resultados de DocIDs gerados pelo ranking para as URLs originais dos documentos, além de preparar a base para cálculos de ranking e uso do índice invertido.


### O que foi implementado

- Criação da classe `SearchEngine` em `src/SearchEngine.py`.
- Função de carregamento do mapa de documentos (`document_map.json`) para memória, com conversão das chaves para inteiros.
- Cache interno (`_document_map`) para evitar leituras repetidas do arquivo em disco.
- Método `mapear_resultados_para_urls(doc_ids)` que recebe uma lista de DocIDs (inteiros) e retorna as URLs correspondentes, ignorando DocIDs inexistentes.
- **Busca direta por termo no índice invertido:** método `buscar_postings_por_termo(termo)` que retorna todos os DocIDs e frequências para um termo processado, usando leitura incremental eficiente com `ijson`.
- Logs informativos e tratamento de erro quando o arquivo `document_map.json` ou `indice_invertido.json` não é encontrado ou não pode ser lido.
- Estrutura preparada para extensão com ranking, cálculo de IDF/TF-IDF e outras funcionalidades de recuperação.


### Contrato (entrada / saída / erros)

- **mapear_resultados_para_urls**
    - Entrada: lista de inteiros (DocIDs) — ex: [12, 45, 2]
    - Saída: lista de strings (URLs) correspondentes na mesma ordem dos DocIDs válidos — ex: ["http://...", "https://..."]. DocIDs inválidos são simplesmente ignorados.
    - Modos de erro: se o `document_map.json` não existir ou ocorrer exceção ao carregar, o módulo retorna uma lista vazia e registra mensagem crítica no logger.
- **buscar_postings_por_termo**
    - Entrada: termo processado (string, após stemming/stopwords)
    - Saída: dicionário `{doc_id: tf, ...}` com todos os DocIDs e frequências para o termo, ou `None` se não encontrado.
    - Modos de erro: se o `indice_invertido.json` não existir ou ocorrer exceção ao carregar, retorna `None` e registra mensagem crítica no logger.

### Fluxo interno

1. Ao chamar `mapear_resultados_para_urls`, o método tenta garantir que `_document_map` esteja carregado chamando `carregar_document_map()`.
2. `carregar_document_map()` verifica se o arquivo existe; em caso afirmativo, carrega o JSON em memória e converte as chaves (strings) para inteiros, costruindo um dicionário {DocID: URL}.
3. Com o mapa em memória, `mapear_resultados_para_urls` itera sobre os DocIDs solicitados, faz lookups usando `.get()` (evita KeyError) e agrega apenas URLs encontradas.

### Complexidade e desempenho

- Leitura do `document_map.json`: O(n) em relação ao número de documentos (n = |document_map|) no momento da carga.
- Acesso/lookup por DocID: O(1) por consulta (dicionário em memória).
- Uso de cache (`_document_map`) elimina custo de I/O em chamadas subsequentes.

Observação de escalabilidade: o mapa de documentos é mantido inteiro em memória. Para coleções enormes (milhões de documentos) pode ser necessário um mecanismo alternativo (ex.: banco de chaves, mmap, ou leitura por lote). A versão atual é adequada para coleções de porte moderado (até algumas centenas de milhares de entradas dependendo da memória disponível).

### Casos de borda e decisões de projeto

- DocIDs inexistentes: simplesmente ignorados (sem lançar exceção). Isso facilita pipelines que possam pedir mapeamentos incompletos.
- Arquivo faltando/corrompido: o método registra uma mensagem crítica e retorna lista vazia — cabe ao chamador tratar a situação (p.ex. acionar indexação ou abortar a query).
- Conversão das chaves para inteiros: adotada para consistência com o resto do código que trata DocIDs como inteiros.

### Integração com o restante do sistema

- `Processor` / `Relatorio` / `Indexador` devem garantir que `logs/document_map.json` esteja presente (gerado durante a indexação) antes de utilizar o `SearchEngine`.
- O `SearchEngine` foi escrito como um componente independente e testável (métodos de classe). Futuramente pode-se adicionar instância para manter estado adicional (ex.: índices auxiliares, caches de ranking).


### Como usar / testar

#### Busca direta por termo (menu interativo)

1. Certifique-se de que `logs/indice_invertido.json` existe e foi gerado pela indexação.
2. Execute o launcher principal:

```bash
python Coletor.py
```

3. No menu interativo, escolha a opção:

```
[5] Etapa 3: Busca Direta por Termo no Índice Invertido
```

4. Digite o termo processado (após stemming/stopwords, ex: "log") quando solicitado. O sistema exibirá até 20 resultados de DocIDs e suas frequências para o termo.

#### Mapeamento de DocIDs para URLs (uso programático)

```python
from src.SearchEngine import SearchEngine
urls = SearchEngine.mapear_resultados_para_urls([12, 45, 2])
print(urls)
```

#### Testes unitários recomendados
- Chamar `mapear_resultados_para_urls` e `buscar_postings_por_termo` com entradas válidas, inválidas e mistura.
- Mockar a leitura dos arquivos (ou gerar arquivos temporários) para verificar comportamento de carga, cache e busca incremental.

### Execução das Etapas via Linha de Comando

O `Coletor.py` foi atualizado para permitir a execução de cada etapa do processo de forma independente através de argumentos de linha de comando.

| Comando | Descrição |
| :--- | :--- |

| Comando | Descrição |
| :--- | :--- |
| `python Coletor.py --etapa coleta` | **Etapa 1:** Inicia o processo de download e salvamento das páginas HTML. |
| `python Coletor.py --etapa indexacao` | **Etapa 2:** Constrói o índice invertido e o mapa de documentos a partir dos HTMLs coletados. |
| `python Coletor.py --etapa idf` | **Etapa 3:** Calcula os pesos IDF para cada termo do vocabulário. |
| `python Coletor.py --etapa diagnostico`| Roda um script de verificação para contar os arquivos coletados. |
| `python Coletor.py --etapa todas` | Executa todas as etapas acima em sequência. |
| `python Coletor.py` | Exibe o menu interativo, incluindo a opção de busca direta por termo no índice invertido. |


Se nenhum argumento for fornecido, o programa exibirá um menu interativo, incluindo a opção de busca direta por termo no índice invertido (Etapa 3).

---

**Autor:**
Luana Almeida @Luana-Almeid
Data da atualização: 13/11/2025
