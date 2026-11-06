# Proposal: Ordenação da Grade por Dias Alocados / Dia Específico com Desempate por Cargo e Nome

## Why
Ao analisar a matriz da grade de escala mensal, os gestores necessitam inspecionar a escala tanto de forma global quanto dia a dia. Ao clicar nos botões de ordenação do topo (ex: `Dias Alocados`, `Cargo`, `Escala`) ou ao clicar no cabeçalho de uma coluna de dia específico (dias 1 a 31):
- A tabela deve priorizar o critério selecionado ou colocar no topo os colaboradores escalados naquele dia específico.
- **Desempate e Agrupamento Padronizado**: Em seguida, os colaboradores com a mesma situação no critério devem ser agrupados estritamente por **Cargo** (ordem alfabética) e, para colaboradores do mesmo cargo, ordenados alfabeticamente por **Nome**.

Isso elimina ordens imprevisíveis na tabela, mantendo os profissionais do mesmo cargo juntos e facilitando a visualização e checagem de cobertura da equipe por turno.

## What
- Ao clicar no cabeçalho de um dia específico (dia 1..31):
  1. Agrupar no topo quem tem escala/plantão alocado naquele dia (ou ordenar pela sigla do turno).
  2. Em caso de empate ou mesmo turno, ordenar por `Cargo` (A-Z).
  3. Em caso de mesmo cargo, ordenar por `Nome` (A-Z).
- Ao clicar no botão `📅 Dias Alocados`:
  1. Ordenar pela quantidade de dias/plantões alocados no mês.
  2. Em caso de empate na quantidade de dias, ordenar por `Cargo` (A-Z).
  3. Em caso de mesmo cargo, ordenar por `Nome` (A-Z).
- Ao clicar no botão `⏱️ Escala`:
  1. Ordenar pela sigla/código de escala padrão do cadastro.
  2. Em caso de empate na escala, ordenar por `Cargo` (A-Z).
  3. Em caso de mesmo cargo, ordenar por `Nome` (A-Z).
- Ao clicar no botão `🏷️ Cargo`:
  1. Ordenar alfabeticamente por `Cargo` (A-Z).
  2. Em caso de mesmo cargo, ordenar por `Nome` (A-Z).

## Impact
- **Frontend (`frontend/src/views/Grade.vue`)**:
  - Ajuste e garantia determinística nas regras da função `sortedMatrixData` e comparadores auxiliares.
  - Atualização visual dos indicadores de clique nos cabeçalhos de dias e botões da barra superior.
