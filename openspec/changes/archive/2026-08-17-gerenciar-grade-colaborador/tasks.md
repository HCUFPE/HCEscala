# Tasks: Gerenciamento de Grade do Colaborador

## Backend (FastAPI & Banco de Dados)
- [x] **1. Modelos SQLAlchemy**: Criar `src/models/grade.py` contendo as classes `Grade` e `GradeDia`, com relacionamentos para `Funcionario`, `Unidade`, `Posto`, `Escala` e campos de auditoria (`login`, `data_alteracao`).
- [x] **2. Migração do Banco de Dados**: Criar e aplicar script de migração do Alembic gerando as tabelas `grades` e `grade_dias`.
- [x] **3. Provedor de Dados (`GradeProvider`)**: Criar `src/providers/grade_provider.py` com métodos assíncronos para:
  - Consulta da matriz de colaboradores e grades filtrada por unidade, mês, ano, cargo e texto de busca.
  - Cálculo dos indicadores de gestão da unidade no mês (total de colaboradores, total em férias, total com múltiplas lotações).
  - Criação, atualização e exclusão atômica de `Grade` e `GradeDia`.
  - Operação de clonagem/cópia de grade entre colaboradores (`copy_grade`).
- [x] **4. Controlador de Negócio (`GradeController`)**: Criar `src/controllers/grade_controller.py` contendo:
  - Validações de mês, ano e restrições de permissão por unidade.
  - Formatação e estruturação da resposta da matriz mensal (dias 1..N, status de férias em cada dia, legendas aplicadas).
  - Orquestração da cópia de grade com confirmação/substituição.
- [x] **5. Router e Schemas Pydantic (`src/routers/grade.py`)**:
  - Definir schemas Pydantic: `GradeCreate`, `GradeUpdate`, `GradeDiaCreate`, `GradeResponse`, `GradeIndicatorsResponse`, `GradeCopyRequest`.
  - Implementar rotas:
    - `GET /api/grades` (matriz com filtros)
    - `GET /api/grades/indicadores` (3 cards de métricas)
    - `GET /api/grades/{id}` (detalhe)
    - `POST /api/grades` (criação)
    - `PUT /api/grades/{id}` (atualização)
    - `POST /api/grades/copiar` (cópia entre colaboradores)
    - `DELETE /api/grades/{id}` (exclusão)
  - Proteger endpoints com `auth_handler.auth_wrapper`.
- [x] **6. Registro de Rotas**: Registrar o router de `grade` em `src/main.py`.

## Frontend (Vue 3 & TypeScript)
- [x] **7. Serviços de API**: Criar ou atualizar serviços em `frontend/src/services/` para expor as chamadas de API da grade (`getGrades`, `getIndicators`, `createGrade`, `updateGrade`, `copyGrade`, `deleteGrade`).
- [x] **8. Painel Principal e Filtros Reativos (`frontend/src/views/Grade.vue`)**:
  - Implementar seletor dinâmico de Mês e Ano.
  - Implementar filtro de Unidade restrito às permissões do usuário logado.
  - Implementar filtro de Categoria/Cargo e busca textual por Nome ou SIAPE.
  - Implementar botão "Limpar Filtros".
- [x] **9. Cards de Indicadores de Gestão**:
  - Implementar os 3 cards no topo da página exibindo em tempo real:
    - Total de Colaboradores no Setor/Unidade;
    - Quantidade em Férias/Afastamento no Mês;
    - Quantidade com Múltiplas Lotações (mais de um posto/unidade).
- [x] **10. Tabela / Matriz de Grade Mensal**:
  - Renderizar os dias exatos do mês selecionado (1 a 28/29/30/31).
  - Destacar visualmente fins de semana e feriados.
  - Fixar coluna do colaborador à esquerda (*sticky*) durante a rolagem horizontal.
  - Exibir badges coloridos para os turnos/legendas (`M`, `T`, `N`, `D`, `FE`, `F`, etc.).
  - Indicar automaticamente dias de férias com destaque `FE`.
- [x] **11. Modal "Criar Nova Grade"**:
  - Componente modal/drawer para seleção do colaborador, mês/ano e preenchimento da escala (preenchimento padrão ou dia a dia).
  - Validações de integridade e feedback visual ao salvar.
- [x] **12. Modal "Copiar Grade"**:
  - Componente modal para selecionar Colaborador de Origem (e mês de referência) e Colaborador(es) de Destino.
  - Confirmação de sobrescrita caso a grade de destino já exista.
  - Execução e atualização imediata da matriz em tela.

## Verificação e Testes
- [x] **13. Teste dos Endpoints da API**:
  - Testar criação, busca com filtros, indicadores e cópia de grade via FastAPI docs/Swagger ou testes de integração.
- [x] **14. Teste de Interface e Usabilidade**:
  - Testar no navegador a filtragem por unidade, categoria e busca por SIAPE/nome.
  - Testar o fluxo de "Criar Nova Grade" e verificar persistência.
  - Testar o fluxo de "Copiar Grade" de um colaborador para outro e validar o preenchimento dos dias.
  - Verificar os 3 cards de indicadores calculados para diferentes unidades e meses.
