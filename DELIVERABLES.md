# Trabalho Prático: Sistema de Recuperação da Informação (RI)

Neste trabalho, será desenvolvido um **Sistema de Recuperação da Informação** (RI) contendo as seguintes etapas: coleta de dados, indexação e recuperação. Como visto em aula, o RI pode ser de busca ou navegacional.

O projeto será dividido em 3 grandes etapas:

| Etapa |
| :--- |
| **Coleta** |
| **Representação** |
| **Recuperação** |

Os relatórios serão entregues incrementalmente, ou seja, o segundo será uma extensão/atualização do primeiro.

---

## ENTREGA 1: Coletor

Esta primeira entrega corresponde à **Parte 1 (Coletor)**. Nesta fase, o grupo apresentará a solução que deseja desenvolver e fará a aquisição dos dados que serão usados. O processo de coleta deve ser apresentado conforme feito em sala de aula, descrevendo as suas principais características.

### Critérios de Avaliação

| Critério | Descrição |
| :--- | :--- |
| **Proposta do Sistema de RI** | Apresentação do problema e da solução proposta para a avaliação. |
| **Descrição do Coletor** | Detalhamento do tipo do coletor, propriedades, tolerâncias, critério de parada, políticas abordadas, etc., e a justificativa das decisões de projeto. |
| **Escala (Volume de Dados)** | A nota neste quesito será dada pela quantidade de páginas coletadas. Para alcançar a pontuação máxima neste quesito, espera-se uma **coleta superior a 50 mil páginas**. |

### Observação

A avaliação final desta etapa será baseada na quantidade de itens coletados (Documentos, Perfis, Páginas Web, etc.) e na apresentação do grupo em sala de aula.

---

## ENTREGA 2: Representação e Indexação

Nesta fase, o grupo será responsável por desenvolver a **representação dos dados** que foram coletados na Etapa 1.

**ATENÇÃO:** Está **expressamente proibido** o uso de tecnologias de Banco de Dados ACID (MySQL, PostgreSQL, Oracle, MS SQL Server, etc.). O uso de Banco de Dados NoSQL está liberado desde que a sua utilização seja devidamente justificada ao professor previamente (Exemplo: usar o Neo4J para representar e recuperar *nodes* em uma estrutura de grafo).

Nesta etapa, os alunos entregarão a **primeira versão do relatório**, descrevendo as tarefas desenvolvidas até o momento e quais os próximos passos para efetivamente finalizar o projeto. Todos os códigos-fonte gerados devem ser entregues.

---

### Critérios de Avaliação

| Peso | Critério | Descrição |
| :--- | :--- | :--- |
| **50%** | **Implementação** | Implementação prática da indexação, incluindo: limpeza de dados, transformações (Análise Léxica, remoção de *stopwords*, *stemming*), análise de tempo e espaço para indexação, tamanho do índice e implementação do **Índice Invertido**. |
| **40%** | **Descrição da Representação** | Relatório parcial da solução com a descrição detalhada das tarefas realizadas. **Clareza é o ponto-chave.** |
| **10%** | **Descrição dos Próximos Passos** | Apresentação dos próximos passos no formato de **cronograma de conclusão**, incluindo a divisão explícita das tarefas a serem desenvolvidas entre os membros do grupo. |