# Specification: Gestão de Gerentes por Nível Organizacional e Painel DIVGP.

## Overview
Esta especificação define o controle de acesso hierárquico baseado na estrutura organizacional do hospital (Setor -> Unidade -> Posto de Serviço), o cadastro e atribuição de gerentes aos respectivos níveis, e o Painel de Monitoramento da DIVGP. para acompanhamento institucional de grades publicadas e pendentes.

---

## 1. Hierarquia de Escopo e Níveis de Gestão

O sistema reconhece 4 níveis de autoridade operacional:

1. **DIVGP. / Administrador Geral (`DIVGP._ADMIN`)**:
   - Possui visão global irrestrita sobre toda a instituição.
   - Pode cadastrar e gerenciar atribuições de gerência para qualquer usuário.
   - Acessa o **Painel DIVGP.**, visualizando todas as grades publicadas e auditando quais unidades/colaboradores estão com escalas pendentes ou faltantes.

2. **Gerente de Setor (`SETOR`)**:
   - Vinculado a um registro específico de `Setor`.
   - **Regra de Visibilidade em Cascata**:
     - Visualiza o seu Setor.
     - Visualiza todas as Unidades pertencentes a este Setor (`Unidade.setor_id == setor_id`).
     - Visualiza todos os Postos de Serviço pertencentes a essas Unidades.
     - Visualiza e gerencia a grade de todos os colaboradores lotados em qualquer unidade do seu setor.

3. **Gerente de Unidade (`UNIDADE`)**:
   - Vinculado a uma `Unidade` específica.
   - **Regra de Visibilidade**:
     - Visualiza apenas a sua Unidade.
     - Visualiza os Postos de Serviço subordinados à sua Unidade (`Posto.unidade_id == unidade_id`).
     - Não visualiza outras unidades do mesmo setor nem de outros setores.
     - Visualiza e gerencia apenas a grade dos colaboradores lotados na sua unidade.

4. **Responsável por Posto de Serviço (`POSTO`)**:
   - Vinculado a um `Posto` específico.
   - Visualiza apenas a sua Unidade pai e o seu Posto de Serviço.
   - Visualiza e gerencia a grade dos colaboradores alocados naquele posto.

---

## 2. Modelo de Dados

### Entidade `UsuarioGerencia` (`usuario_gerencias`)
Armazena as delegações de chefia concedidas aos usuários do sistema:

- `id` (int, PK, autoincrement)
- `usuario` (string, index, nullable=False): Login de rede/AD do usuário (ex: `joao.silva`, `maria.enfermeira`).
- `nome` (string, nullable=False): Nome de exibição do gestor.
- `nivel` (string, nullable=False): Enum ou String (`DIVGP._ADMIN`, `SETOR`, `UNIDADE`, `POSTO`).
- `setor_id` (int, FK `setores.id`, nullable=True): Obrigatório se `nivel == 'SETOR'`.
- `unidade_id` (int, FK `unidades.id`, nullable=True): Obrigatório se `nivel == 'UNIDADE'`.
- `posto_id` (int, FK `postos.id`, nullable=True): Obrigatório se `nivel == 'POSTO'`.
- `ativo` (bool, default=True): Permite ativar ou inativar o acesso de gestão sem excluir o histórico.
- `login` (string, auditoria): Quem concedeu/alterou a permissão.
- `data_alteracao` (datetime, auditoria): Data/hora da última alteração.

---

## 3. Endpoints da API REST (FastAPI)

### 3.1. Gestão de Gerentes (`/api/gerencias`) - Restrito a DIVGP./Admin
- `GET /api/gerencias`: Lista todos os usuários cadastrados como gerentes, com filtros por nível, setor e unidade.
- `GET /api/gerencias/me`: Retorna o escopo e as unidades/setores acessíveis pelo usuário autenticado no token atual.
- `POST /api/gerencias`: Cadastra uma nova atribuição de gerência para um usuário.
- `PUT /api/gerencias/{id}`: Atualiza nível, escopo ou status ativo do gerente.
- `DELETE /api/gerencias/{id}`: Remove uma atribuição de gerência.

### 3.2. Painel e Relatório de Conformidade da DIVGP. (`/api/DIVGP.`)
- `GET /api/DIVGP./status-unidades`: Retorna o status de homologação de grades de todas as unidades no mês/ano:
  - `setor_id`, `setor_nome`.
  - `unidade_id`, `unidade_nome`.
  - `total_colaboradores`: Total de funcionários com lotação ativa.
  - `total_publicadas`: Quantidade de grades publicadas.
  - `total_pendentes`: Quantidade de grades em Rascunho/Enviada/Aprovada.
  - `total_sem_grade`: Quantidade de colaboradores sem nenhuma grade cadastrada.
  - `percentual_conclusao`: Percentual de grades publicadas em relação ao total.
  - `status_geral`: `100% Homologada`, `Em Andamento`, `Pendente`.
- `GET /api/DIVGP./faltantes`: Retorna a lista detalhada e nominal de colaboradores que ainda estão sem grade ou com grade não publicada na unidade/mês selecionado (com SIAPE, Cargo, Lotação e Contato da Chefia).

---

## 4. Interfaces do Usuário (Frontend Vue 3)

### 4.1. Tela de Cadastro de Gerentes (`/gerentes`)
- Acessível no menu lateral por administradores e membros da DIVGP..
- Modal de cadastro com seleção em cascata:
  - Campo de Login/Usuário de rede e Nome do Gestor.
  - Seleção do Nível (`Administrador Geral DIVGP.`, `Gerente de Setor`, `Gerente de Unidade`, `Responsável por Posto`).
  - Dropdown em cascata (Se escolher Setor -> lista setores; Se escolher Unidade -> filtra unidades pelo setor selecionado; Se escolher Posto -> filtra postos pela unidade).
- Tabela com listagem dos gerentes, seus níveis, unidades associadas, status (ativo/inativo) e ações de edição/exclusão.
- **Ordenação Dinâmica de Colunas**: Cabeçalhos clicáveis com indicadores visuais (`↕`, `▲`, `▼`) permitindo ordenar por Gestor/Usuário, Nível de Gestão, Escopo Atribuído (Hierarquia), Status (Ativo/Inativo) e Auditoria (Data de Alteração).

### 4.2. Painel de Monitoramento da DIVGP. (`/painel-DIVGP.`)
- Visualização executiva para a DIVGP. com seletores de **Mês** e **Ano**.
- Cards com indicadores consolidados:
  - Total de Unidades no Hospital.
  - Unidades 100% Publicadas.
  - Unidades com Pendências.
  - Total Geral de Colaboradores vs Grades Publicadas.
- Tabela analítica agrupada por Setor com barra de progresso visual de homologação para cada Unidade.
- Modal detalhado: Ao clicar em uma unidade com pendências, abre a lista nominal dos colaboradores com grades **Faltando**, facilitando a cobrança pontual às chefias.

### 4.3. Aplicação do Escopo na Tela Principal de Grades (`/grade`)
- Quando um **Gerente de Setor** acessa a tela de Grade:
  - O dropdown de unidades exibe apenas as unidades que compõem o seu setor.
- Quando um **Gerente de Unidade** acessa:
  - O dropdown fica fixado na sua unidade de responsabilidade.
- Quando a **DIVGP. / Admin** acessa:
  - Tem acesso irrestrito ao dropdown com todas as unidades do hospital.
