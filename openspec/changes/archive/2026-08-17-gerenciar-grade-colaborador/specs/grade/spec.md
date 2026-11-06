# Specification: Gerenciamento de Grade do Colaborador

## Overview
Esta especificação estabelece os requisitos e o comportamento esperado para o gerenciamento de escalas e grades mensais de colaboradores no sistema, integrando dados de funcionários, unidades, cargos, férias e lotações em uma visão matricial interativa.

## Requirements

### 1. Modelo de Dados e Persistência
1.1. **Entidade `Grade` (Cabeçalho da Grade Mensal)**:
- `id`: Inteiro, Chave Primária (Auto-incremento).
- `funcionario_id`: Inteiro, Chave Estrangeira para `funcionarios.id` (Obrigatório).
- `unidade_id`: Inteiro, Chave Estrangeira para `unidades.id` (Obrigatório).
- `posto_id`: Inteiro, Chave Estrangeira para `postos.id` (Opcional).
- `mes`: Inteiro (1 a 12) (Obrigatório).
- `ano`: Inteiro (ex: 2026) (Obrigatório).
- `status`: String (ex: `'Rascunho'`, `'Publicada'`, `'Aprovada'`, padrão: `'Rascunho'`).
- `observacao`: String/Texto opcional.
- `login`: String contendo o identificador do usuário que realizou a última alteração (Auditoria).
- `data_alteracao`: Timestamp da última modificação.
- **Restrição de Unicidade**: Combinação única de (`funcionario_id`, `unidade_id`, `mes`, `ano`).

1.2. **Entidade `GradeDia` (Itens Diários da Grade)**:
- `id`: Inteiro, Chave Primária (Auto-incremento).
- `grade_id`: Inteiro, Chave Estrangeira para `grades.id` com cascade delete (Obrigatório).
- `dia`: Inteiro (1 a 31) representando o dia do mês (Obrigatório).
- `escala_id`: Inteiro, Chave Estrangeira para `escalas.id` (Opcional).
- `legenda_sigla`: String correspondente à sigla da Legenda (ex: `'M'`, `'T'`, `'N'`, `'FE'`, `'F'`, `'SN'`) (Opcional).
- `descricao`: String opcional para detalhamento específico daquele dia.
- **Restrição de Unicidade**: Combinação única de (`grade_id`, `dia`).

---

### 2. Controle de Permissões e Seleção de Unidade
2.1. O usuário autenticado poderá selecionar e visualizar apenas as unidades organizacionais para as quais possui permissão de acesso:
- **Administrador** (pertencente ao grupo `GLO-SEC-HCPE-SETISD` ou flag admin): Acesso irrestrito a todas as unidades e setores.
- **Gestores / Chefias de Setor**: Acesso restrito às unidades sob sua gerência/departamento.
- Se o usuário não possuir privilégio administrativo ou gerencial explícito, ele visualiza as unidades onde atua ou a lista filtrada de acordo com o contexto do seu usuário.

---

### 3. Filtros e Consulta
3.1. **Filtro de Período**: Seleção de Mês (1-12) e Ano (ex: 2026). Padrão inicial: Mês e Ano correntes.
3.2. **Filtro de Unidade**: Seletor com as unidades autorizadas para o usuário.
3.3. **Filtro de Categoria**: Dropdown listando os cargos cadastrados no sistema (`Cargo`), permitindo filtrar por categoria (ex: Médico, Enfermeiro, Fisioterapeuta, Técnico de Enfermagem).
3.4. **Busca Textual**: Campo de pesquisa que filtra em tempo real ou por submissão pelo **Nome** ou **Matrícula/SIAPE** do colaborador.
3.5. **Ação de Limpar Filtros**: Restaura os filtros para os padrões da unidade inicial do usuário.

---

### 4. Indicadores de Gestão (Cards de Resumo)
A tela deve exibir no topo do painel 3 cards de métricas sintetizadas para a unidade e mês selecionados:
1. **Total de Colaboradores no Setor/Unidade**:
   - Quantidade total de funcionários ativos com lotação vigente na unidade selecionada.
2. **Colaboradores em Férias/Afastamento no Mês**:
   - Quantidade de colaboradores daquela unidade que possuem registro em `FuncionarioFerias` com período sobrepondo o mês/ano selecionado.
3. **Colaboradores em Múltiplos Postos/Unidades**:
   - Quantidade de colaboradores daquela unidade que possuem mais de uma lotação ativa (`FuncionarioLotacao`) em postos ou unidades distintos no período.

---

### 5. Matriz / Tabela da Grade Mensal
5.1. A tabela deve listar todos os colaboradores da unidade (ou os filtrados).
5.2. O cabeçalho da tabela deve conter:
   - Coluna de identificação do colaborador (Nome, Cargo, Carga Horária semanal/contratual, Posto principal).
   - Colunas numéricas de 1 a N (onde N é o total de dias do mês selecionado: 28, 29, 30 ou 31).
   - Indicação visual de fins de semana (sábado e domingo) e feriados cadastrados (`Feriado`).
5.3. Cada célula de dia exibirá:
   - Sigla do turno/escala alocada (ex: `M`, `T`, `N`, `D`, `FE`, `F`) com cores contextuais (ex: Azul para Manhã, Amarelo/Laranja para Tarde, Roxo/Índigo para Noite, Vermelho/Rosa para Férias).
   - Caso o colaborador esteja em férias no dia, a sigla `FE` ou tag de férias deve ser destacada automaticamente.
5.4. A coluna do colaborador deve ser fixada (*sticky*) à esquerda durante a rolagem horizontal dos dias do mês.

---

### 6. Ações Operacionais: Criar e Copiar Grade
6.1. **Criar Nova Grade**:
   - Modal ou Drawer permitindo ao gestor selecionar o Colaborador (dentre os lotados na unidade que ainda não possuem grade para o mês).
   - Permite selecionar a Unidade/Posto, Mês/Ano e preencher os dias do mês:
     - Preenchimento rápido por padrão de escala (ex: escala base associada ao funcionário, preenchendo os dias úteis ou dias de plantão 12x36).
     - Edição manual dia a dia selecionando as siglas cadastradas em `Legenda` ou `Escala`.
   - Valida se o colaborador já possui grade para o mesmo mês/unidade.
   - Salva o registro e atualiza imediatamente a matriz da grade na tela.

6.2. **Copiar Grade**:
   - Modal de clonagem que permite:
     - Selecionar o **Colaborador de Origem** (de quem copiar a grade) e o **Mês/Ano de Origem**.
     - Selecionar o **Colaborador de Destino** (para quem aplicar) e o **Mês/Ano de Destino**.
     - Opção de selecionar múltiplos colaboradores de destino caso deseje aplicar a mesma escala padrão.
   - Realiza a cópia de todos os registros de `GradeDia` correspondentes ao mês, adaptando a quantidade de dias caso o mês de destino tenha quantidade de dias diferente do mês de origem.
   - Fornece aviso caso o colaborador de destino já possua grade preenchida, solicitando confirmação para sobrescrever.

---

### 7. Endpoints da API REST (FastAPI)
- `GET /api/grades`: Consulta a lista de grades por filtros (`unidade_id`, `mes`, `ano`, `cargo_id`, `search`).
- `GET /api/grades/indicadores`: Retorna o resumo consolidado de métricas para a unidade e mês (`total_colaboradores`, `total_ferias`, `total_multiplas_lotacoes`).
- `GET /api/grades/{id}`: Retorna a grade completa de um colaborador com todos os seus dias (`GradeDia`).
- `POST /api/grades`: Cria uma nova grade mensal para um colaborador com seus dias.
- `PUT /api/grades/{id}`: Atualiza os dias e observações de uma grade existente.
- `POST /api/grades/copiar`: Clona a grade de um colaborador de origem para um ou mais colaboradores de destino.
- `DELETE /api/grades/{id}`: Remove uma grade cadastrada.
