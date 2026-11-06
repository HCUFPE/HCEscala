# Tasks: Gestão de Gerentes por Nível Organizacional e Painel DIVGP.

## 1. Backend & Banco de Dados
- [x] Criar modelo SQLAlchemy `UsuarioGerencia` em `src/models/usuario_gerencia.py` com relacionamentos (`Setor`, `Unidade`, `Posto`).
- [x] Exportar `UsuarioGerencia` em `src/models/__init__.py`.
- [x] Criar `src/providers/gerencia_provider.py` com operações de CRUD e método de resolução de escopo (`get_user_scope_units`).
- [x] Criar `src/controllers/gerencia_controller.py` com validações de regras de negócio por nível.
- [x] Criar `src/routers/gerencia.py` com endpoints `/api/gerencias` e injeção de permissões administrativas.
- [x] Criar `src/providers/DIVGP._provider.py` com consultas de agregação de status de grades por unidade e busca de colaboradores faltantes.
- [x] Criar `src/controllers/DIVGP._controller.py` e `src/routers/DIVGP..py` com endpoints `/api/DIVGP./status-unidades` e `/api/DIVGP./faltantes`.
- [x] Registrar os novos routers (`gerencia` e `DIVGP.`) em `src/main.py`.
- [x] Integrar a resolução de escopo hierárquico nos endpoints de `/api/unidades` e `/api/grades`.

## 2. Frontend (Vue 3 / TypeScript)
- [x] Criar serviço `frontend/src/services/gerenciaService.ts` para comunicação com `/api/gerencias`.
- [x] Criar serviço `frontend/src/services/DIVGP.Service.ts` para comunicação com `/api/DIVGP.`.
- [x] Criar view `frontend/src/views/Gerentes.vue` para cadastro e gestão de usuários/chefias com seleção em cascata (Setor -> Unidade -> Posto).
- [x] Criar view `frontend/src/views/PainelDIVGP..vue` com indicadores institucionais, tabela de conformidade por unidade e modal de colaboradores faltantes.
- [x] Atualizar `frontend/src/views/Grade.vue` para restringir a seleção de unidades ao escopo do gestor autenticado.
- [x] Registrar as rotas `/gerentes` e `/painel-DIVGP.` em `frontend/src/router/index.ts`.
- [x] Adicionar os links de navegação com ícones dedicados em `frontend/src/layouts/DefaultLayout.vue`.

## 3. Testes & Homologação
- [x] Criar script de testes automatizados `scripts/test_http_gerencias_DIVGP..py` validando:
  - Cadastro de gerência nos 4 níveis (DIVGP., Setor, Unidade, Posto).
  - Isolamento de acesso e visibilidade em cascata para Gerente de Setor vs Gerente de Unidade.
  - Relatório de conformidade da DIVGP. listando grades publicadas e pendentes/faltantes.
- [x] Compilar pacote de produção do frontend (`npm run build`) e validar integridade.
