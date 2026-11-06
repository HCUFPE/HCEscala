# Proposal: Cadastro de Cargos e Vínculos

## Problem Statement
O sistema precisa gerenciar os cargos (com nome e carga horária) e vínculos empregatícios (nome do vínculo) dos colaboradores. Esses dados são fundamentais para o processo de gestão de escalas e lotação de profissionais. Atualmente, não há uma interface ou API para realizar esse cadastro de forma estruturada.

## Proposed Solution
Criar duas novas funcionalidades de cadastro (CRUD):
1. **Cadastro de Cargos**: Permitir registrar o nome do cargo e sua carga horária.
2. **Cadastro de Vínculos**: Permitir registrar o nome do vínculo.

Ambas as entidades devem seguir o padrão de auditoria do sistema, registrando automaticamente o `login` do usuário que fez a alteração e a data da última atualização (`data_alteracao`). 

## Goals
- Criar modelos e tabelas no banco de dados para `Cargos` e `Vinculos`.
- Expor endpoints REST (FastAPI) para as operações de CRUD.
- Desenvolver telas no frontend (Vue 3) para gerenciar essas entidades.
- Garantir a rastreabilidade (auditoria) das alterações.

## Non-Goals
- Não abordaremos a atribuição desses cargos e vínculos a funcionários específicos neste momento (isso será uma funcionalidade de Lotação/Colaborador).
