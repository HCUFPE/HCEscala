# Tasks: create-escalas-screen

## Backend (FastAPI)
- [x] Criar o arquivo `src/models/escala.py` com o modelo SQLAlchemy `Escala` (campos: id auto-increment, inicio_jornada, fim_jornada, codigo, sigla, descricao, apenas_assistenciais, login, data_alteracao).
- [x] Criar um script de migração do Alembic para adicionar a tabela `escalas` e coluna `descricao` ao banco de dados.
- [x] Implementar restrição de unicidade para a coluna `sigla` garantindo integridade e validação de duplicidade.
- [x] Criar o provedor `src/providers/escala_provider.py` para as operações de banco de dados da escala.
- [x] Criar o controlador `src/controllers/escala_controller.py` contendo as regras de negócio e validação dos modelos Pydantic.
- [x] Criar o router `src/routers/escala.py` implementando os endpoints GET, POST, PUT, DELETE para `/api/escalas`.
- [x] Registrar o novo router `escala` no arquivo `src/main.py`.

## Frontend (Vue 3)
- [x] Criar a página/view `frontend/src/views/Escalas.vue` (Tabela de listagem e botão para adicionar).
- [x] Criar o componente de formulário para cadastro/edição (Modal ou inline), com campos e validações adequadas (código, sigla, descrição, horários).
- [x] Integrar ordenação clicável por qualquer cabeçalho de coluna na tabela (`sortBy`, indicadores `↕`, `▲`, `▼`).
- [x] Integrar a página `Escalas.vue` com as chamadas da API criadas no backend.
- [x] Adicionar a rota `/escalas` no roteador do Vue (`frontend/src/router/index.ts` ou similar).
- [x] Aplicar estilos modernos, harmoniosos e animações suaves, seguindo as diretrizes de design do projeto.

## Review e Testes
- [x] Testar a persistência no banco de dados criando uma nova escala via interface.
- [x] Verificar validação de sigla única e exibição correta da descrição.
- [x] Verificar se a ordenação ascendente/descendente funciona em todas as colunas da tabela.
