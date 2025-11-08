# Mudanças e Explicação da Funcionalidade de Cálculo de IDF

## Introdução

Foi implementada uma nova funcionalidade no projeto para calcular o IDF (Inverse Document Frequency) de todos os termos presentes no índice invertido. O cálculo de IDF é fundamental em sistemas de recuperação da informação, pois permite medir a importância de cada termo em relação ao conjunto de documentos.

## Mudanças Realizadas

- Criação do arquivo `src/CalculaIDF.py` responsável por calcular o IDF de todos os termos do índice invertido.
- O script lê o índice invertido (`logs/indice_invertido.json`) e o mapa de documentos (`logs/document_map.json`).
- O resultado do cálculo é salvo em `logs/idf.json`, contendo o IDF de cada termo.
- Implementação de fallback para processar índices muito grandes usando o pacote `ijson` (parser incremental).
- Mensagens de log e tratamento de erros aprimorados para facilitar o diagnóstico.

## Funcionamento do `CalculaIDF.py`

O script executa os seguintes passos:

1. **Carrega o mapa de documentos** para obter o número total de documentos (N).
2. **Tenta carregar o índice invertido inteiro em memória**. Caso não seja possível (por exemplo, se o arquivo for muito grande), utiliza o parser incremental `ijson`.
3. **Para cada termo no índice invertido**, obtém o número de documentos em que o termo aparece (df) e calcula o IDF usando a fórmula:
   
   $$
   	ext{IDF}(t) = \log\left(\frac{N}{df_t}\right)
   $$

4. **Salva o resultado** em `logs/idf.json`, no formato `{ "termo": idf, ... }`.

## Como Interpretar o Resultado (`idf.json`)

O arquivo `idf.json` contém um dicionário onde:
- **Chave**: termo do índice invertido.
- **Valor**: IDF calculado para o termo.

### Interpretação dos valores de IDF
- **IDF alto**: O termo aparece em poucos documentos, sendo mais relevante para diferenciar documentos.
- **IDF baixo**: O termo aparece em muitos documentos, sendo menos útil para diferenciação (ex: palavras muito comuns).
- **IDF = 0**: O termo aparece em todos os documentos, não ajudando a distinguir nenhum documento.

### Exemplo de uso
Se o termo "inteligência" tem IDF alto, ele é raro e pode ser um bom discriminador de documentos. Se o termo "de" tem IDF próximo de zero, ele é comum e pouco informativo.

---

**Autor:**
Osvaldo Neto @osvaldoferreiraf
Data da atualização: 08/11/2025
# Documento Técnico e Análise de Complexidade do Coletor Web Não Modular --> Modular