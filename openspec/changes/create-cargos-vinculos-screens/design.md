# Design: Cargos e Vínculos

## Architecture
- **Model Layer**: Criar arquivos `cargo.py` e `vinculo.py` no diretório `src/models/`, estendendo `database.Base`.
- **Provider Layer**: Criar `cargo_provider.py` e `vinculo_provider.py` no diretório `src/providers/` contendo métodos para buscar, inserir, atualizar e excluir, utilizando `AsyncSession`.
- **Controller Layer**: Criar `cargo_controller.py` e `vinculo_controller.py` no diretório `src/controllers/` para abstrair as validações.
- **Router Layer**: Definir Pydantic schemas para requisições e retornos. Criar `cargo.py` e `vinculo.py` em `src/routers/` para injetar o `db_session` e o `current_user`. Registrar esses routers em `main.py`.

## Data Model
**Tabela `cargos`**
- `id` (Integer, Primary Key)
- `nome` (String(100), Unique)
- `carga_horaria` (Integer)
- `login` (String(100))
- `data_alteracao` (DateTime, onupdate=now())

**Tabela `vinculos`**
- `id` (Integer, Primary Key)
- `nome` (String(100), Unique)
- `login` (String(100))
- `data_alteracao` (DateTime, onupdate=now())

## Frontend Architecture
- **Views**:
  - `frontend/src/views/Cargos.vue`
  - `frontend/src/views/Vinculos.vue`
- Ambos usarão a lógica `reactive` para gerenciar formulários e `ref` para a listagem da API.
- Navegação atualizada em `frontend/src/layouts/DefaultLayout.vue` usando ícones `BriefcaseIcon` (Cargos) e `IdentificationIcon` (Vínculos) do `@heroicons/vue`.
