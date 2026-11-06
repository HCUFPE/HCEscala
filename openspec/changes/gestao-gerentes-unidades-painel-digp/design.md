# Design: Gestão de Gerentes por Nível Organizacional e Painel DIVGP.

## Architecture

### 1. Camada de Dados (Backend)
- **Novo Modelo**: `UsuarioGerencia` em `src/models/usuario_gerencia.py`
  - Relacionamentos com `Setor`, `Unidade` e `Posto`.
  - Herda de `Base` do SQLAlchemy com colunas de auditoria padrão (`login`, `data_alteracao`).
- **Provider & Controller**:
  - `src/providers/gerencia_provider.py`: Consultas para busca por usuário, listagem com `selectinload` das entidades organizacionais e cálculo de escopo de IDs de unidades autorizadas.
  - `src/controllers/gerencia_controller.py`: Validação de regras de negócio (consistência de IDs obrigatórios para cada nível e unicidade de gerência ativa).
- **Provedor e Controller DIVGP.**:
  - `src/providers/DIVGP._provider.py`: Executa agregações assíncronas calculando para cada unidade:
    $$\text{Percentual} = \frac{\text{Grades Publicadas}}{\text{Total Colaboradores Ativos}} \times 100$$
    E busca colaboradores que não possuem grade publicada no mês/ano.
  - `src/controllers/DIVGP._controller.py`: Formata métricas e listas nominais de faltantes.

### 2. Algoritmo de Resolução de Escopo (`UserScopeHelper`)
Quando qualquer requisição chega à API:
1. O token JWT identifica o `username` e seus grupos AD.
2. Se o usuário for membro do grupo `GLO-SEC-HCPE-SETISD`, `admin` ou possuir registro com `nivel == 'DIVGP._ADMIN'`:
   - Escopo: `is_admin = True`, acesso irrestrito a todas as unidades (`unidade_ids = None`).
3. Se o usuário possuir registro `UsuarioGerencia` ativo com:
   - `nivel == 'SETOR'`:
     - Consulta todas as unidades onde `unidade.setor_id == usuario_gerencia.setor_id`.
     - Escopo: `unidade_ids = [u.id for u in unidades_do_setor]`.
   - `nivel == 'UNIDADE'`:
     - Escopo: `unidade_ids = [usuario_gerencia.unidade_id]`.
   - `nivel == 'POSTO'`:
     - Escopo: `unidade_ids = [usuario_gerencia.posto.unidade_id]`, `posto_ids = [usuario_gerencia.posto_id]`.
4. Os routers de Unidades e Grades filtram suas consultas por `unidade_id.in_(unidade_ids)` garantindo isolamento total de dados.

### 3. Camada de Frontend (Vue 3 / TypeScript)
- **Serviços**:
  - `frontend/src/services/gerenciaService.ts`: CRUD de gerências e consulta de `/api/gerencias/me`.
  - `frontend/src/services/DIVGP.Service.ts`: Chamadas para `/api/DIVGP./status-unidades` e `/api/DIVGP./faltantes`.
- **Views**:
  - `frontend/src/views/Gerentes.vue`: Gestão de usuários e delegação de níveis organizacionais.
  - `frontend/src/views/PainelDIVGP..vue`: Dashboard institucional com gráficos/barras de conformidade e modal de faltantes.
  - `frontend/src/views/Grade.vue`: Atualização para carregar apenas as unidades permitidas pelo escopo do usuário.
- **Roteador & Navegação**:
  - Adição das rotas `/gerentes` e `/painel-DIVGP.` em `frontend/src/router/index.ts`.
  - Inclusão dos links no menu lateral de `DefaultLayout.vue` visíveis conforme o nível do usuário.
