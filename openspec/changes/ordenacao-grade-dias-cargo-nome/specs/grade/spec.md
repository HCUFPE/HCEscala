# Delta Specification: Ordenação Hierárquica por Dia / Dias Alocados com Desempate por Cargo e Nome

## User flows & requirements

### 1. Ordenação por Coluna de Dia Específico (Dias 1 a 31)
- **Ação**: O usuário clica no cabeçalho da coluna de um dia específico (dia 1 a 31) na matriz da grade.
- **Comportamento Esperado**:
  1. A ordenação deve destacar o dia selecionado (`selectedDiaHighlight = dia`) e definir a ordenação por esse dia (`sortColumn = 'dia_' + dia`).
  2. A ordenação primária agrupa no topo os colaboradores que possuem escala/plantão cadastrado no dia (ou com turno alocado), separando-os dos que não estão escalados (ou folgas/vazio).
  3. Dentro do mesmo status ou sigla de turno do dia, o desempate hierárquico **obrigatoriamente** ordena por:
     - **Cargo** (ordem alfabética A-Z).
     - **Nome do Colaborador** (ordem alfabética A-Z).

### 2. Ordenação por Botão "Dias Alocados"
- **Ação**: O usuário clica no botão `📅 Dias Alocados` na barra superior da tabela.
- **Comportamento Esperado**:
  1. Ordena primariamente pelo total de dias escalados no mês (ordem decrescente por padrão, alternando para crescente no segundo clique).
  2. Para colaboradores com o mesmo número de dias alocados, o desempate **obrigatoriamente** ordena por:
     - **Cargo** (ordem alfabética A-Z).
     - **Nome do Colaborador** (ordem alfabética A-Z).

### 3. Ordenação por Botão "Escala"
- **Ação**: O usuário clica no botão `⏱️ Escala` na barra superior da tabela.
- **Comportamento Esperado**:
  1. Ordena primariamente pelo código/sigla de escala de cadastro do funcionário.
  2. Para colaboradores com a mesma escala de trabalho, o desempate **obrigatoriamente** ordena por:
     - **Cargo** (ordem alfabética A-Z).
     - **Nome do Colaborador** (ordem alfabética A-Z).

### 4. Ordenação por Botão "Cargo"
- **Ação**: O usuário clica no botão `🏷️ Cargo` na barra superior da tabela.
- **Comportamento Esperado**:
  1. Agrupa os colaboradores pela denominação do seu cargo (ordem alfabética A-Z).
  2. Para colaboradores que possuem o mesmo cargo, ordena alfabeticamente por **Nome**.

## Acceptance Criteria
- [ ] Clicar no cabeçalho de qualquer dia (1..31) posiciona colaboradores com escala naquele dia no topo, mantendo-os agrupados por Cargo e depois por Nome.
- [ ] Clicar no botão `📅 Dias Alocados` coloca no topo colaboradores com mais dias de plantão e desempata quem tem a mesma quantidade de dias por Cargo e Nome.
- [ ] Clicar no botão `⏱️ Escala` agrupa pela escala padrão e desempata por Cargo e Nome.
- [ ] Em nenhuma situação a ordenação produz lista desordenada ou com inversão aleatória de nomes/cargos idênticos.
