# Design: create-escalas-screen

## Architecture
A funcionalidade de Escalas seguirá a arquitetura monolítica padrão do projeto (FastAPI + Vue 3). O fluxo de dados será:
**Vue Component -> FastAPI Router -> Controller -> Provider -> SQLAlchemy (DB)**

## Implementation Details

### Banco de Dados (SQLAlchemy)
**`src/models/escala.py`**:
- Modelo `Escala` estendendo a Base do SQLAlchemy.
- Campos:
  - `id` (Integer, Primary Key, Auto-increment)
  - `inicio_jornada` (Time)
  - `fim_jornada` (Time)
  - `codigo` (String, unique)
  - `sigla` (String)
  - `apenas_assistenciais` (Boolean, default False)
  - `login` (String, nullable=False)
  - `data_alteracao` (DateTime, onupdate, server_default)

### Backend (FastAPI)
- **`src/providers/escala_provider.py`**: Classe responsável por executar as queries no banco de dados via SQLAlchemy para a tabela `escalas`.
- **`src/controllers/escala_controller.py`**: Lógica de negócio, recebendo Pydantic models de input, chamando o provider e formatando a saída.
- **`src/routers/escala.py`**: Definição das rotas `/api/escalas` (GET, POST, PUT, DELETE), com injeção de dependências (Depends) e proteção por JWT se aplicável.
- **`src/main.py`**: Adicionar a inclusão do router de `escala`.

### Frontend (Vue 3)
- **`frontend/src/views/Escalas.vue`**: Nova página contendo a tabela de listagem de escalas e botão para criar/editar.
- O componente de formulário poderá ser um modal ou estar na mesma tela.
- **`frontend/src/router/index.ts`** (ou equivalente): Adição da rota `/escalas` mapeando para a view `Escalas.vue`.
- Estilização premium seguindo as diretrizes do projeto (Vanilla CSS ou classes utilitárias já existentes, dark mode se aplicável, animações suaves nos botões e linhas da tabela).
