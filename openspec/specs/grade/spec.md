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
   - Sigla do turno/escala alocada (ex: `M`, `T`, `N`, `D`, `FE`, `F`, `D6`) com cores contextuais (ex: Azul para Manhã, Amarelo/Laranja para Tarde, Roxo/Índigo para Noite, Vermelho/Rosa para Férias).
   - **Tooltip Descritivo com Jornada e Horários**: Ao posicionar o cursor sobre a célula/sigla do dia, o sistema exibe um tooltip com a descrição detalhada da escala cadastrada e seus horários oficiais de início e término (ex: `D6 - PLANTÃO DIÚRNO (07:00 ÀS 19:00)`), enriquecido com as legendas e regras institucionais.
   - Caso o colaborador esteja em férias no dia, a sigla `FE` ou tag de férias deve ser destacada automaticamente.
5.4. A coluna do colaborador deve ser fixada (*sticky*) à esquerda durante a rolagem horizontal dos dias do mês:
   - **Exibição Destacada do Cargo**: Cada linha do colaborador deve exibir com destaque visual seu **Cargo** (com badge contrastante `bg-blue-50 text-blue-800 border-blue-200` e ícone `💼`), informando a carga horária semanal (ex: `(40h)`) e com fallback seguro (`"Sem Cargo"`) para evitar omissão de dados.
   - **Largura Mínima da Coluna Fixa**: A coluna do profissional possui largura mínima de 250px a 280px para comportar nome, cargo destacado, matrícula SIAPE e badges de status/posto sem quebras inadequadas.
5.5. **Vínculo Estrito Empregado, Lotação e Período**:
   - Cada registro de `Grade` está obrigatoriamente associado a um colaborador (`funcionario_id`), uma lotação (`uorg_id`) e um período (`mes` e `ano`).
   - A unicidade no banco (`UniqueConstraint("funcionario_id", "uorg_id", "mes", "ano")`) impede duplicações para a mesma unidade e mês, garantindo histórico consistente.
5.6. **Divisão de Carga Horária e Múltiplas Unidades**:
   - Quando o colaborador estiver vinculado a mais de uma unidade/posto de serviço (`FuncionarioLotacao`), a sua carga horária contratual pode ser dividida entre as unidades.
   - Na visualização da grade da unidade selecionada, os dias em que o colaborador já possui escala/plantão cadastrado na **outra unidade vinculada** devem ser destacados visualmente com badge pontilhado e identificação da unidade correspondente, evitando conflitos de agendamento e permitindo ao gestor acompanhar a integralização da jornada semanal/mensal dividida.
5.7. **Ciclo de Vida de Status, Visibilidade e Bloqueio Imutável para a DIVGP.**:
   - As grades podem transitar pelos status: `Rascunho`, `Enviada`, `Aprovada` e `Publicada`. Todos os status são registrados e persistidos no banco.
   - **Regra de Negócio DIVGP.**: A DIVGP. (Divisão de Gestão de Pessoas / RH) e os relatórios de consolidação institucional têm acesso apenas às grades com status **`Publicada`**.
   - **Bloqueio de Edição (Imutabilidade pós-publicação)**:
     - Assim que a grade é publicada para a DIVGP. (`status = 'Publicada'`), ela é **bloqueada** para edição, exclusão e sobrescrita pelo gerente da área.
     - Na interface do usuário, a grade publicada é apresentada em modo somente leitura (com badge `Publicada (Bloqueada 🔒)` e ícone de visualização 👁️), desativando formulários e o botão de salvar.
     - Caso sejam necessárias correções em uma grade já publicada, apenas a DIVGP. ou administradores do sistema podem reabri-la através da ação de **Reabertura de Grade** (`POST /api/grades/{id}/reabrir`), retornando o status para `Rascunho` e liberando novas edições pelo gerente.
5.8. **Tratamento de Colaboradores Diaristas e Calendário de Feriados**:
   - **Identificação de Diarista**: Colaboradores em regime diarista (escala 5x2, 40h/30h/20h semanais, jornadas administrativas ou não-assistenciais exclusivas de plantão) são identificados com o badge `📅 Diarista`.
   - **Integração com o Calendário de Feriados**:
     - Feriados cadastrados no sistema (`Feriado`) para o mês/ano selecionado são automaticamente refletidos na matriz da grade mensal.
     - As colunas dos dias de feriado são destacadas visualmente no cabeçalho da tabela com badge `FER` 🔴 e tooltip com o nome do feriado (Nacional, Estadual, Municipal ou Institucional).
     - Para colaboradores **Diaristas**, os dias de feriado são automaticamente considerados **Folga por Feriado** (`FR` / Feriado) nos dias sem plantão extraordinário registrado.
     - No **Assistente de Preenchimento Rápido** (*Preencher Dias Úteis Seg-Sex*), o sistema respeita o calendário de feriados do mês, não alocando turno de trabalho em feriados para diaristas e aplicando a sigla de folga de feriado (`FR`).
5.9. **Ordenação Inteligente e Priorização de Escalas com Dados (Matriz Unificada)**:
   - **Interface Unificada (Sem Abas Separadas)**: Toda a gestão, consulta e disparo de edição ocorrem diretamente sobre a matriz de escala da unidade.
   - **Prioridade Absoluta para Escalas com Dados/Plantões**: Os colaboradores que já possuem grade preenchida com dados (plantões ou afastamentos alocados no mês, ou horas escaladas > 0) devem ser listados no topo da visualização antes dos colaboradores com grade pendente ou sem dados no período.
   - **Critério Determinístico de Agrupamento e Desempate**:
     - Ao ordenar por qualquer critério principal (como `Dias Alocados`, `Cargo` ou `Escala`), o sistema aplica internamente a ordenação secundária hierárquica por **Cargo** e **Nome do Colaborador**, garantindo estabilidade e previsibilidade visual dos dados.
   - **Botões de Ordenação Rápida na Barra Superior da Tabela**:
     - `📅 Dias Alocados`: Ordena diretamente pelo número de dias trabalhados/escalados no mês (com desempate por Cargo e Nome).
     - `🏷️ Cargo`: Agrupa alfabeticamente pela denominação do cargo (com desempate por Nome).
     - `⏱️ Escala`: Ordena pelo código de escala padrão de cadastro (com desempate por Cargo e Nome).
     - Cabeçalho `Profissional`: Ordena pelo Nome do Colaborador.

---

### 6. Ações Operacionais: Criar, Editar e Copiar Grade
6.1. **Criar Nova Grade**:
   - Modal ou Drawer permitindo ao gestor selecionar o Colaborador (dentre os lotados na unidade que ainda não possuem grade para o mês).
   - Permite selecionar a Unidade/Posto, Mês/Ano e preencher os dias do mês:
     - **Preenchimento Rápido com Códigos Cadastrados**: Combo carregando todos os códigos de escala cadastrados (`Escala`), com suas respectivas siglas, horários de início e fim, indicação de aplicabilidade assistencial e descrições, além das legendas gerais de turno.
     - **Modal "Selecionar Dias..."**: Ferramenta interativa de calendário com caixas de seleção (checkboxes) para marcação direta de múltiplos dias (com filtros de seleção rápida como todos, dias úteis, fins de semana e limpar). Ao confirmar, aplica de imediato o código de escala selecionado aos dias marcados.
     - **Restrição de Códigos**: Os lançamentos diários manuais e automatizados são restritos aos códigos de escala cadastrados, garantindo padronização e consistência.
     - Edição manual dia a dia selecionando as siglas cadastradas em `Legenda` ou `Escala`.
   - Valida se o colaborador já possui grade para o mesmo mês/unidade (e impede modificações se já estiver `Publicada`).
   - Salva o registro e atualiza imediatamente a matriz da grade na tela.

6.2. **Editar Escala do Colaborador (Modo Protegido)**:
   - Acionado através do botão de ação **Editar** na linha da tabela da grade.
   - **Identificação Protegida (Somente Leitura)**:
     - Os dados cadastrais de identificação do colaborador (**Nome**, **SIAPE / Matrícula**, **Vínculo**, **Escala Padrão**, **Cargo Efetivo**, **Unidade / Lotação - UORG** e **Posto de Serviço**) são exibidos em formato de card informativo protegido, impedindo alterações acidentais de lotação ou identificação pessoal durante a manutenção da escala.
   - **Carregamento Automático dos Códigos Diários Cadastrados**:
     - A grade de dias do mês (dias 1 a 28/29/30/31) dentro do formulário modal é automaticamente pré-carregada com as siglas/códigos de escala já salvos ou vinculados na linha (`row.dias`).
     - O gestor pode alterar livremente qualquer código diário individualmente ou utilizar o assistente de preenchimento rápido para sobrescrever múltiplos dias.
   - **Validação de Bloqueio**: Se a escala estiver com status `Publicada`, a edição permanece bloqueada contra salvamento para usuários comuns da unidade.

6.3. **Copiar Grade**:
   - Modal de clonagem que permite:
     - Selecionar o **Colaborador de Origem** (de quem copiar a grade) e o **Mês/Ano de Origem**.
     - Selecionar o **Colaborador de Destino** (para quem aplicar) e o **Mês/Ano de Destino**.
     - Opção de selecionar múltiplos colaboradores de destino caso deseje aplicar a mesma escala padrão.
   - Realiza a cópia de todos os registros de `GradeDia` correspondentes ao mês, adaptando a quantidade de dias caso o mês de destino tenha quantidade de dias diferente do mês de origem.
   - Fornece aviso caso o colaborador de destino já possua grade preenchida e bloqueia a sobrescrita caso a grade do destino já esteja `Publicada` (exceto para administradores).

---

### 7. Endpoints da API REST (FastAPI)
- `GET /api/grades`: Consulta a lista de grades por filtros (`unidade_id`, `mes`, `ano`, `cargo_id`, `search`, `status`, `apenas_publicadas`).
- `GET /api/grades/indicadores`: Retorna o resumo consolidado de métricas para a unidade e mês (`total_colaboradores`, `total_ferias`, `total_multiplas_lotacoes`).
- `GET /api/grades/{id}`: Retorna a grade completa de um colaborador com todos os seus dias (`GradeDia`).
- `POST /api/grades`: Cria uma nova grade mensal para um colaborador com seus dias.
- `PUT /api/grades/{id}`: Atualiza os dias e observações de uma grade existente (bloqueado com 403 se `status == 'Publicada'` e usuário não for admin).
- `POST /api/grades/{id}/publicar`: Publica uma grade individual tornando-a visível para a DIVGP. e bloqueando edições para o gerente da área.
- `POST /api/grades/{id}/reabrir`: Reabre uma grade publicada, retornando-a para `Rascunho` (restrito a DIVGP. e administradores).
- `POST /api/grades/publicar-lote`: Publica em lote todas as grades da unidade no mês/ano para a DIVGP..
- `POST /api/grades/copiar`: Clona a grade de um colaborador de origem para um ou mais colaboradores de destino (bloqueia destinos publicados para não-admins).
- `DELETE /api/grades/{id}`: Remove uma grade cadastrada (bloqueado com 403 se `status == 'Publicada'` e usuário não for admin).

---

### 8. Consistências Cruzadas e Integridade Referencial na Exclusão

Para prevenir órfãos e garantir a integridade dos dados operacionais e históricos do sistema de escalas, são aplicadas validações prévias restritivas (HTTP 400 Bad Request) antes de qualquer exclusão:

1. **Unidade Organizacional (UORG)**:
   - Não pode ser excluída se possuir UORGs subordinadas (filhas).
   - Não pode ser excluída se possuir Postos de Serviço vinculados.
   - Não pode ser excluída se possuir histórico ou lotação de colaboradores (`funcionarios_lotacoes`) associada.
   - Não pode ser excluída se possuir grades de escala (`grades`) cadastradas no sistema.
   - Não pode ser excluída se possuir delegações de chefia/gerência (`usuario_gerencias`) vinculadas.

2. **Posto de Serviço**:
   - Não pode ser excluído se possuir colaboradores vinculados por lotação (`funcionarios_lotacoes`).
   - Não pode ser excluído se possuir grades de escala (`grades`) associadas a ele.
   - Não pode ser excluído se possuir delegação de chefia (`usuario_gerencias`) vinculada.

3. **Colaborador (Funcionário)**:
   - Não pode ser excluído se possuir grades de escala (`grades`) geradas no sistema.
   - Não pode ser excluído se possuir registros de férias cadastrados (`funcionarios_ferias`).

4. **Cargo**:
   - Não pode ser excluído se houver colaboradores ativos ou cadastrados vinculados ao cargo.

5. **Vínculo**:
   - Não pode ser excluído se houver colaboradores vinculados ao tipo de vínculo.

6. **Escala**:
   - Não pode ser excluída se estiver configurada como a escala padrão de colaboradores.
   - Não pode ser excluída se tiver sido utilizada em lançamentos diários (`grade_dias`) em qualquer grade de escala.
