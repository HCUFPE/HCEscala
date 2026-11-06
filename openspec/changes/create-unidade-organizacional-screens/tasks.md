# Tasks: Unidade Organizacional

- `[ ]` Criar modelo `Setor` em `src/models/setor.py`
- `[ ]` Criar modelo `Unidade` em `src/models/unidade.py`
- `[ ]` Criar modelo `Posto` em `src/models/posto.py`
- `[ ]` Atualizar relacionamentos usando SQLAlchemy (`relationship`, `ForeignKey`)
- `[ ]` Criar Providers para as três entidades
- `[ ]` Criar Controllers para as três entidades
- `[ ]` Criar e mapear Rotas (`setor.py`, `unidade.py`, `posto.py`) em `src/routers/`
- `[ ]` Registrar as rotas no `main.py`
- `[x]` Criar view Vue `Organizacao.vue` com abas para gerenciar os três níveis.
- `[x]` Adicionar `Organizacao` ao roteador do Vue (`index.ts`)
- `[x]` Adicionar link no `DefaultLayout.vue` usando `BuildingOfficeIcon`.
- `[x]` Adicionar ordenação dinâmica em todas as colunas de UORGs e Postos de Serviço.
- `[x]` Aplicar validações no backend e frontend:
  - UORG: nome não pode ser vazio e deve ser único globalmente.
  - Posto de Serviço: nome não pode ser vazio e deve ser único dentro da mesma UORG vinculada.
- `[x]` Gerar automaticamente um posto de serviço homônimo para todas as unidades organizacionais cadastradas (tanto existentes via seed quanto em novos cadastros).


