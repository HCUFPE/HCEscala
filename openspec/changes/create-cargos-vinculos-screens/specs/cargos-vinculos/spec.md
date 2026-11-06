# Specification: Cargos e Vínculos

## Overview
Este documento detalha o comportamento esperado para o cadastro de Cargos e Vínculos no sistema.

## Requirements

### 1. Entidade Cargo
- **Campos Obrigatórios**:
  - `id`: Identificador único (auto incremento).
  - `nome`: Nome do cargo (ex: Enfermeiro, Médico, Técnico de Enfermagem).
  - `carga_horaria`: Carga horária semanal associada ao cargo (ex: 30, 36, 40 horas). Numérico.
  - `login`: Usuário que realizou a última modificação (Auditoria).
  - `data_alteracao`: Data e hora da última modificação (Auditoria).
- **Regras de Negócio**:
  - O `nome` deve ser único.

### 2. Entidade Vínculo
- **Campos Obrigatórios**:
  - `id`: Identificador único (auto incremento).
  - `nome`: Nome do vínculo (ex: CLT, Estatutário, PJ).
  - `login`: Usuário que realizou a última modificação (Auditoria).
  - `data_alteracao`: Data e hora da última modificação (Auditoria).
- **Regras de Negócio**:
  - O `nome` deve ser único.

### 3. API
- Devem existir as seguintes rotas base:
  - `/api/cargos` (GET, GET /{id}, POST, PUT /{id}, DELETE /{id})
  - `/api/vinculos` (GET, GET /{id}, POST, PUT /{id}, DELETE /{id})
- O preenchimento do campo `login` deve ser automático com base no JWT do usuário logado (via FastAPI Depends).
- O campo `data_alteracao` é controlado pelo banco de dados (`onupdate=func.now()`).

### 4. Interface (Frontend)
- Novas views: `Cargos.vue` e `Vinculos.vue`.
- Layout padronizado com as outras telas, utilizando tabela para listar registros, e botões de ação (ícones Heroicons: Lápis para editar, Lixeira para excluir).
- **Ordenação Dinâmica de Colunas**: Os cabeçalhos de coluna de ambas as tabelas (ID, Nome, Carga Horária, Usuário, Data de Alteração) são clicáveis e permitem ordenação ascendente/descendente interativa com indicadores visuais (`↕`, `▲`, `▼`).
- Modais embutidos para Criação e Edição.
- Adicionar atalhos para essas telas na navegação lateral (Menu).

### 5. Consistências Cruzadas e Regras de Exclusão
- **Exclusão de Cargo**:
  - Não é permitida a exclusão caso existam colaboradores vinculados a ele (`Funcionario.cargo_id`). O sistema responde com código HTTP 400 informando o total de colaboradores vinculados.
- **Exclusão de Vínculo**:
  - Não é permitida a exclusão caso existam colaboradores associados ao vínculo (`Funcionario.vinculo_id`). O sistema responde com código HTTP 400 informando o total de colaboradores vinculados.
