# Design: Feriados

## Backend
1. **Model `src/models/feriado.py`**:
   - Criação da classe SQLAlchemy `Feriado` herdando de `Base`.
   - Adicionar ao `alembic/env.py` para gerar migrações.
   
2. **Provider `src/providers/feriado_provider.py`**:
   - Métodos estáticos: `get_all(session, ano)`, `get_by_id`, `create`, `update`, `delete`.
   - `get_all` deve receber parâmetros opcionais para filtrar por datas/ano.

3. **Controller `src/controllers/feriado_controller.py`**:
   - Camada de validação de negócios (ex: não permitir criar sem data, validar se nome não está vazio).

4. **Router `src/routers/feriado.py`**:
   - Exposição dos endpoints REST usando FastAPI. 
   - Validações via Pydantic (`FeriadoCreate`, `FeriadoUpdate`, `FeriadoResponse`).
   - Injetar dependência de Autenticação (`auth_handler`).
   - Registrar router no `src/main.py`.

## Frontend
1. **Componente `frontend/src/views/Feriados.vue`**:
   - Tabela de dados semelhante à de Funcionários/Escalas, mas exibindo a Data formatada (DD/MM/YYYY), Nome e Tipo.
   - Filtro de Ano na barra de busca (um select com o ano atual, ano passado e próximo ano).
   - Modal para criar e editar, contendo os campos `Data` (input type date), `Nome` (input text) e `Tipo` (select).

2. **Rotas e Navegação**:
   - Adicionar o menu "Feriados" no arquivo `frontend/src/layouts/DefaultLayout.vue` sob um agrupamento "Configurações" ou no mesmo nível de Escalas.
   - Registrar a rota no `frontend/src/router/index.ts`.
