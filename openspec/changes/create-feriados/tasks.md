# Tasks: Feriados

## Backend
- [ ] Criar arquivo `src/models/feriado.py` com a definição da classe SQLAlchemy.
- [ ] Importar `Feriado` em `alembic/env.py`.
- [ ] Gerar script de migração do banco (Alembic) para criar a tabela.
- [ ] Criar arquivo `src/providers/feriado_provider.py` para acesso ao banco.
- [ ] Criar arquivo `src/controllers/feriado_controller.py` com as regras e formatações.
- [ ] Criar arquivo `src/routers/feriado.py` com endpoints do FastAPI (`GET`, `POST`, `PUT`, `DELETE`).
- [ ] Registrar o novo router no `src/main.py`.

## Frontend
- [ ] Criar tela Vue.js em `frontend/src/views/Feriados.vue`.
  - [ ] Montar tabela com cabeçalhos Data, Nome, Tipo e Ações.
  - [ ] Adicionar Modal com o formulário padrão.
- [ ] Configurar a rota `/feriados` em `frontend/src/router/index.ts`.
- [ ] Inserir link no menu de navegação em `frontend/src/layouts/DefaultLayout.vue`.
