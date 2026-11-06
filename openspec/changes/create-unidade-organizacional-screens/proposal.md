# Proposal: Cadastro de Unidades Organizacionais

## Problem Statement
O sistema precisa de uma estrutura hierárquica para alocar funcionários e organizar as escalas. Atualmente, o sistema carece de um cadastro para a estrutura organizacional da instituição, que é dividida em três níveis hierárquicos: Setor, Unidade e Posto de Serviço.

## Proposed Solution
Desenvolver o CRUD para as estruturas organizacionais, garantindo a seguinte hierarquia:
- **Setor** (Nível mais alto)
- **Unidade** (Pertence a um Setor)
- **Posto de Serviço** (Pertence a uma Unidade)

Isso permitirá que o sistema represente com precisão onde o colaborador atua. Assim como nos demais cadastros, as ações devem registrar os dados de auditoria padrão (`login` e `data_alteracao`).

## Goals
- Criar modelos de dados para Setores, Unidades e Postos de Serviço, refletindo seus relacionamentos (chaves estrangeiras).
- Criar a camada de API (Routers, Controllers, Providers) para as operações CRUD dessas entidades.
- Criar interface no frontend (Vue 3) permitindo visualizar e cadastrar a hierarquia (ex: dropdowns em cascata ao criar uma Unidade ou Posto).
- Incluir `login` e `data_alteracao` em todas as tabelas.

## Non-Goals
- Atribuição direta de colaboradores a essas unidades será feita em uma etapa futura (Lotação).
