# Specification: Unidade Organizacional

## Overview
As Unidades Organizacionais do sistema possuem três níveis hierárquicos: `Setores`, `Unidades` e `Postos de Serviço`.

## Requirements

### 1. Entidades

**Setor** (Nível Raiz)
- `id` (int, autoincrement, PK)
- `nome` (string, unique)
- `login` (string, auditoria)
- `data_alteracao` (datetime, auditoria)

**Unidade** (Nível 2)
- `id` (int, autoincrement, PK)
- `nome` (string, unique)
- `setor_id` (int, FK para Setor)
- `login` (string, auditoria)
- `data_alteracao` (datetime, auditoria)

**Posto de Serviço** (Nível 3)
- `id` (int, autoincrement, PK)
- `nome` (string) - *Pode não ser único globalmente, mas deve ser único dentro da mesma Unidade.*
- `unidade_id` (int, FK para Unidade)
- `login` (string, auditoria)
- `data_alteracao` (datetime, auditoria)

### 2. API
- `/api/setores` (CRUD completo)
- `/api/unidades` (CRUD completo). O GET deve retornar o `Setor` relacionado para facilidade de exibição.
- `/api/postos` (CRUD completo). O GET deve retornar a `Unidade` e o `Setor` relacionados.

### 3. Interface de Usuário
- Uma tela centralizada `Organizacao.vue` para gerenciar a hierarquia através de abas (UORGs e Postos de Serviço).
- As tabelas exibem `ID`, `Código / Sigla`, `Nome`, `UORG Pai` / `UORG Vinculada`, `Usuário` e `Data Alt.`, com botões de Ações.
- **Ordenação Dinâmica de Colunas**:
  - Na aba **UORGs**, os cabeçalhos (ID, Código / Sigla, Nome da UORG, UORG Pai, Usuário, Data Alt.) são clicáveis para ordenação ascendente/descendente com indicadores visuais (`↕`, `▲`, `▼`).
  - Na aba **Postos de Serviço**, os cabeçalhos (ID, Nome do Posto, UORG Vinculada, Usuário, Data Alt.) são clicáveis para ordenação interativa (`↕`, `▲`, `▼`).
- No formulário de UORG, suporte a hierarquia recursiva (UORG Pai).
- No formulário de Posto, seleção da UORG vinculada.

### 4. Regras de Validação e Unicidade
- **UORG (Unidade Organizacional)**:
  - O campo `nome` é obrigatório, não pode ser vazio ou conter apenas espaços em branco.
  - O `nome` da UORG deve ser estritamente único em todo o sistema (não são permitidas duas UORGs com o mesmo nome, independente da caixa alta/baixa).
- **Posto de Serviço**:
  - O campo `nome` é obrigatório, não pode ser vazio ou conter apenas espaços em branco.
  - O `nome` do Posto de Serviço deve ser único dentro da mesma UORG vinculada (mesma unidade pai). Postos com o mesmo nome são permitidos apenas se pertencerem a UORGs diferentes.
  - **Posto Homônimo Automático**: Toda Unidade Organizacional (UORG) cadastrada no sistema possui automaticamente um Posto de Serviço correspondente com o mesmo nome da unidade, vinculado a ela própria.

### 5. Consistências Cruzadas e Regras de Exclusão
- **Exclusão de Unidade Organizacional (UORG)**:
  - Não é permitida a exclusão se houver UORGs subordinadas (filhas).
  - Não é permitida a exclusão se houver Postos de Serviço vinculados.
  - Não é permitida a exclusão se houver colaboradores com histórico ou lotação ativa (`funcionarios_lotacoes`) vinculada à UORG.
  - Não é permitida a exclusão se houver grades de escala (`grades`) cadastradas para a UORG.
  - Não é permitida a exclusão se houver delegações de chefia/gerência (`usuario_gerencias`) vinculadas à UORG.
  - Caso haja qualquer uma dessas dependências, o sistema rejeita a operação com código HTTP 400 informando a quantidade de registros dependentes.

- **Exclusão de Posto de Serviço**:
  - Não é permitida a exclusão se houver colaboradores com lotação associada ao posto (`funcionarios_lotacoes`).
  - Não é permitida a exclusão se houver grades de escala (`grades`) associadas ao posto.
  - Não é permitida a exclusão se houver delegações de chefia (`usuario_gerencias`) associadas ao posto.
  - Em caso de dependências, o sistema rejeita a operação com código HTTP 400 detalhando os vínculos existentes.


