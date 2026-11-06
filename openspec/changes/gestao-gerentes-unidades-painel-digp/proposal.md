# Proposal: Gestão de Gerentes por Nível Organizacional e Painel de Conformidade da DIVGP.

## Problem Statement
Atualmente, qualquer usuário com permissão geral de acesso consegue visualizar e manipular as unidades do hospital sem uma restrição granular baseada em sua hierarquia de chefia. Além disso:
1. Não existe um cadastro para vincular quais usuários são gerentes de quais **Setores**, **Unidades** ou **Postos de Serviço**.
2. Falta a aplicação do princípio de visibilidade hierárquica em cascata:
   - Gerente de **Setor** deve enxergar todas as unidades e postos subordinados ao seu setor.
   - Gerente de **Unidade** deve enxergar apenas a sua unidade e seus postos.
   - Responsável por **Posto** deve enxergar apenas o seu posto.
3. A **DIVGP.** (Divisão de Gestão de Pessoas / Administrador Geral) precisa de um **Painel de Monitoramento Institucional** para acompanhar quais grades já foram **Publicadas** e quais unidades e colaboradores estão com escalas **Faltando / Pendentes** no mês de referência.

## Proposed Solution
1. **Mapeamento de Gerentes e Perfis Hierárquicos**:
   - Criar o modelo `UsuarioGerencia` para vincular usuários (`username`, `login`, `nome`) ao seu escopo de gestão:
     - Nível `DIVGP._ADMIN` (Acesso irrestrito a todo o hospital).
     - Nível `SETOR` (Acesso ao Setor e todas as Unidades/Postos filhos).
     - Nível `UNIDADE` (Acesso à Unidade e seus Postos filhos).
     - Nível `POSTO` (Acesso exclusivo ao Posto de Serviço).
2. **Mecanismo de Filtro e Escopo Hierárquico no Backend**:
   - Implementar helper e injeção de dependência (`get_user_scope`) que filtra automaticamente as consultas de unidades, colaboradores e grades conforme o escopo de atuação do usuário autenticado.
3. **Tela de Cadastro e Gestão de Gerentes**:
   - Interface administrativa restrita à DIVGP. para cadastrar, editar e revogar delegações de gerência com seleção em cascata (Nível -> Setor -> Unidade -> Posto).
4. **Painel de Conformidade e Acompanhamento da DIVGP.**:
   - Dashboard institucional com visão macro por Setor e Unidade no mês/ano:
     - Indicador de total de colaboradores lotados.
     - Total de grades `Publicadas` (homologadas).
     - Total de grades `Pendentes` / `Em Elaboração`.
     - Identificação nominal dos colaboradores com **Grades Faltando** para envio de notificações/cobranças às chefias.

## Goals
- Criar a tabela `usuario_gerencias` com relacionamentos, auditoria e migração de banco.
- Implementar as rotas da API REST `/api/gerencias` com controle de permissão estrito.
- Adequar os endpoints de listagem de unidades, postos e matriz de grade para respeitar o escopo hierárquico do usuário logado.
- Criar a tela no frontend para **Gerenciamento de Chefias e Usuários**.
- Criar a tela no frontend do **Painel de Monitoramento DIVGP.** com estatísticas de grades publicadas vs faltantes por unidade.

## Non-Goals
- Não substituir o Active Directory (a autenticação por login/senha permanece via LDAP/JWT; o sistema apenas armazena as delegações de gerência interna).
