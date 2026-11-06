# Arquitetura do Sistema HC Escalas

Este documento detalha a arquitetura em camadas, o fluxo de dados e os padrões de persistência adotados no **HC Escalas** (Sistema de Gestão de Escalas de Serviço do Hospital das Clínicas da UFPE / EBSERH).

---

## 1. Visão Geral da Arquitetura

O sistema adota uma arquitetura em camadas desacoplada com injeção de dependência assíncrona do FastAPI:

```
[ Frontend: Vue 3 + Vite + Tailwind ]
                  │
                  ▼  (HTTP REST com Bearer JWT)
         [ src/routers/ ] 
        (Validação Pydantic & Dependências)
                  │
                  ▼
       [ src/controllers/ ] 
        (Regras de Negócio & Orquestração)
                  │
                  ▼
        [ src/providers/ ] 
        (Acesso a Dados & Consultas ORM/SQL)
                  │
                  ▼
        [ src/resources/ ] 
        (Gerenciamento de Sessões e Pools Assíncronos)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  [ SQLite: app.db ]   [ PostgreSQL / Oracle: AGHU ]
```

---

## 2. Camadas da Aplicação

### 2.1. Routers (`src/routers/`)
- Ponto de entrada das requisições HTTP REST.
- Validação estrita de contratos de entrada e saída via schemas **Pydantic**.
- Injeção de dependências (`Depends`) para sessões de banco e usuário autenticado (`auth_handler.decode_token` e `auth_handler.auth_wrapper`).
- Extração segura de identidade do usuário autenticado compatível com claims padrão JWT (`sub` e `username`) com fallback para auditoria.
- Tratamento de status codes HTTP (200, 201, 400, 401, 403, 404).

### 2.2. Controllers (`src/controllers/`)
- Camada responsável pelas regras de negócio, cálculos e orquestração.
- Exemplos:
  - Verificação de limites mensais de horas escaladas.
  - Regra de alçada para aprovação e devolução de escalas (Chefia imediata vs Chefia Superior vs DIVGP).
  - Controle de bloqueio e reabertura de escalas publicadas.
  - Formatação de respostas consolidadas e geração de logs de auditoria.
  - Garantia de unicidade de cargos por tupla `(nome, carga_horaria)`.

### 2.3. Providers (`src/providers/`)
- Responsabilidade exclusiva de persistência e consulta.
- Utiliza **SQLAlchemy 2.0** com carregamento otimizado de relacionamentos (`selectinload`).
- Responsável por montar a matriz consolidada da grade mensal unindo colaboradores, turnos diários, feriados e ocorrências de férias.

### 2.4. Resources (`src/resources/`)
- Gerenciamento de conexões assíncronas (`AsyncEngine`, `AsyncSession` com pool `NullPool` ou `QueuePool`).
- Suporte a múltiplos bancos simultâneos:
  - **SQLite Local (`app.db`):** Dados transacionais de escalas, funcionários, lotações, UORGs, feriados e logs de auditoria.
  - **PostgreSQL / Oracle AGHU:** Acesso federado aos dados clínicos e hospitalares institucionais.

---

## 3. Modelo de Dados e Relacionamentos Críticos

```
                  ┌────────────────────────┐
                  │      Uorg (UORGs)      │
                  │ - id, nome, sigla      │
                  │ - uorg_pai_id (Árvore) │
                  └───────────┬────────────┘
                              │ 1:N
                              ▼
┌──────────────┐  1:N   ┌───────────────────────┐   1:N   ┌─────────────┐
│ Funcionarios ├───────►│ FuncionariosLotacoes  │◄────────┤   Postos    │
│              │        │ - data_inicio         │         │             │
│              │        │ - data_fim (aberto)   │         └─────────────┘
└──────┬───────┘        └───────────────────────┘
       │
       │ 1:N
       ├─────────────────────────────────┐
       ▼                                 ▼
┌──────────────┐                 ┌───────────────┐
│    Grades    │                 │     Ferias    │
│ - mes, ano   │                 │ - data_inicio │
│ - status     │                 │ - data_fim    │
└──────┬───────┘                 └───────────────┘
       │ 1:N
       ▼
┌──────────────┐
│  GradeDias   │
│ - dia (1-31) │
│ - escala_id  │
│ - sigla      │
└──────────────┘
```

---

## 4. Matriz de Perfis (4 Papéis) e Sequência de Aprovação da Escala

O sistema opera com **4 papéis formais de acesso e autoridade**, atendendo com precisão à governança de escalas do hospital:

| Papel | Escopo / Nível | Responsabilidades e Ações Permitidas |
| :--- | :--- | :--- |
| **1. Supervisor de Posto de Serviço** | `POSTO` (ou múltiplos postos) | • Elabora manualmente ou copia a escala dos colaboradores lotados nos seus postos de serviço.<br>• A escala permanece com status inicial **⚪ Em Elaboração** (`Rascunho`).<br>• Pode ajustar turnos e plantões respeitando os tetos contratuais.<br>• Ao finalizar, clica no botão **"Aprovar para Unidade"** (ou em lote via **"Aprovar Todas para Unidade"**) para submeter à validação da chefia da unidade. |
| **2. Gerente da Unidade** | `UORG` / Unidade (e subordinadas) | • Valida as escalas de todos os postos de serviço da sua unidade.<br>• **Se houver inconsistência:** Devolve a escala para ajuste do supervisor (**"Devolver para Correção do Chefe do Posto"**), que assume status **🟠 Devolvida para Posto**.<br>• **Se estiverem todas corretas:** Homologa e despacha para a divisão de pessoal acionando **"Enviar para DIVGP"** (ou em lote **"Enviar Todas para DIVGP"**). |
| **3. Gerente da DIVGP** | `DIVGP_ADMIN` / Divisão de Gestão de Pessoas | • Analisa tecnicamente as escalas consolidadas enviadas por todas as unidades do hospital.<br>• Pode **homologar e disponibilizar para visualização pelo usuário externo/final** (**🟢 Publicada**). Uma vez publicada, a escala torna-se oficial e fica bloqueada contra edições de supervisores e chefes de unidade.<br>• Se detectar alguma desconformidade antes da publicação oficial, pode **devolver com apontamentos** para adequação. |
| **4. Administrador do Sistema** | `ADMIN` / TI (Acesso Total) | • Possui acesso irrestrito a todas as funcionalidades do sistema (gestão de UORGs, postos, funcionários, atribuição de chefias/gerências e legendas).<br>• Pode cadastrar, aprovar, devolver, publicar e reabrir escalas em qualquer unidade ou posto a qualquer momento. |

### Fluxo da Esteira de Aprovação

```
┌─────────────────────────────────┐
│ 1. SUPERVISOR DO POSTO          │
│   (Elaboração manual ou cópia)  │
└────────────────┬────────────────┘
                 │ Cadastra / Copia Escala
                 ▼
       [ ⚪ Em Elaboração ] (Rascunho)
                 │
                 │ Ação: "Aprovar para Unidade"
                 ▼
┌─────────────────────────────────┐
│ 2. GERENTE DA UNIDADE           │◄─────────────────────┐
│    (Validação de todos postos)  │                      │
└────────────────┬────────────────┘                      │
                 │                                       │
        ┌────────┴────────┐                              │ Devolver para Correção
        │ Há pendência?   ├───────── Sim ────────────────┘ (Status: 'Devolvida para Posto')
        └────────┬────────┘
                 │ Não (Tudo aprovado)
                 │ Ação: "Enviar para DIVGP"
                 ▼
┌─────────────────────────────────┐
│ 3. GERENTE DA DIVGP             │◄─────────────────────┐
│    (Análise e Homologação)      │                      │
└────────────────┬────────────────┘                      │ Devolver para Ajuste
                 │                                       │ (Retorna para Unidade)
        ┌────────┴────────┐                              │
        │ Em conformidade?├───────── Não ────────────────┘
        └────────┬────────┘
                 │ Sim (Aprovação Final)
                 │ Ação: "Homologar & Publicar"
                 ▼
      [ 🟢 Publicada (DIVGP) ]
(Oficializada, visível para usuário final e bloqueada para alterações)
                 ▲
                 │ Reabertura Excepcional
┌────────────────┴────────────────┐
│ 4. ADMINISTRADOR DO SISTEMA     │ (Permissão irrestrita em todas as telas e fluxos)
└─────────────────────────────────┘
```

1. **Em Elaboração (Rascunho):**
   - Criada pelo Supervisor de Posto de Serviço manualmente ou através da ferramenta de **Cópia de Escala**.
   - Permite edições de plantões e turnos de acordo com a carga horária do colaborador.

2. **Aprovação para a Unidade (`Enviada_Superior`):**
   - Finalizada a elaboração no posto, o Chefe do Posto aciona o botão **"Aprovar para Unidade"** (individual ou em lote via **"Aprovar Todas para Unidade"**).
   - A escala é encaminhada para a alçada do Chefe da Unidade.

3. **Conferência e Devolução / Envio à DIVGP:**
   - O Chefe da Unidade avalia todos os postos de serviço sob sua responsabilidade.
   - **Caso haja erro/divergência:** O gestor utiliza a ação **"Devolver para Correção do Chefe do Posto"** registrando o motivo no histórico. A escala volta ao posto com status **Devolvida para Posto**.
   - **Estando em conformidade:** O gestor aciona **"Enviar para DIVGP"** (individual ou em lote via **"Enviar Todas para DIVGP"**).

4. **Publicação Institucional (`Publicada`):**
   - A escala é homologada, oficializada para todo o hospital e **bloqueada para alterações**, permitindo consulta externa e auditabilidade.
   - **Reabertura (Admin / DIVGP):** Apenas administradores ou a própria DIVGP possuem permissão especial para reabrir escalas publicadas em caso de retificações excepcionais.

---

## 5. Regras de Cópia de Escala

A funcionalidade de replicação mensal de escalas foi projetada para garantir agilidade operacional sem gerar sobreposições indevidas:
- **Origem Dinâmica:** Carrega automaticamente todos os colaboradores filtrados na tela de escala, permitindo selecionar todos ou escolher colaboradores pontualmente.
- **Correspondência 1-para-1:** Cada colaborador tem sua escala replicada diretamente para **ele mesmo** no mês de destino, **preservando o seu posto de serviço de lotação**.
- **Filtro de Férias e Afastamentos:** Plantões da origem marcados como Férias (`FE`), Feriados (`FR`/`FD0`), Licenças/Afastamentos (`LM`, `LP`, `A`, `FJ`, etc.) ou Abonos (`AB`) **não são copiados** como turnos de trabalho.
- **Respeito ao Calendário de Destino:** Se o dia no mês alvo for feriado oficial cadastrado ou se o colaborador possuir férias agendadas no período destino, o sistema não insere plantão de trabalho sobre esses dias.
- **Status Inicial:** As escalas geradas por cópia entram sempre com o status **⚪ Em Elaboração (Rascunho)** para que o chefe do posto realize as conferências necessárias antes de aprovar para a unidade.

---

## 6. Auditoria de Alterações

Todas as operações críticas (inserções, atualizações e exclusões em colaboradores, escalas, lotações e estruturas) são registradas na tabela `audit_logs`, gravando:
- Usuário responsável (login / matrícula).
- Data e hora com fuso horário.
- Tela e entidade afetada.
- Snapshot do estado anterior e do novo estado em JSON.

---

## 7. Arquitetura Frontend & Otimizações de UX

- **Alternância de Visualização (Tabela vs. Calendário):**
  - Seletor de modo posicionado no cabeçalho superior permitindo alternar entre a **Grade Matricial Mensal** e o **Calendário Mensal** detalhado por dia.
- **Matriz de Escala com Rolagem Sincronizada:**
  - Implementação de scrollbar horizontal espelhada no topo (`topScrollContainer`), permitindo navegação rápida em tabelas largas sem necessidade de rolar verticalmente até o rodapé.
  - Sincronização de largura e evento de rolagem via `ResizeObserver` e `requestAnimationFrame`.
- **Coluna Sticky do Colaborador (70 caracteres):**
  - Fixação da primeira coluna (`sticky left-0`) com largura dimensionada para `420px`.
  - Formatação concisa: `{SIAPE} - {Nome} ({Cargo})` limitada a 70 caracteres com tipografia compacta (`text-[10.5px]`).
  - Tooltip acessível (`title`) preservando matrícula, nome e cargo completos.
- **Coluna de Status Dedicada:**
  - Posicionada logo após a coluna de Carga Horária, exibindo com clareza o estado da escala (`Em Elaboração`, `Enviada para Unidade`, `Devolvida para Posto`, `Publicada (DIVGP)`).
- **Filtros Dependentes de Dados Reais:**
  - Selects de UORGs e Postos de Serviço alimentados apenas por entidades com colaboradores lotados.
  - Combo de categorias enriquecido com carga horária semanal e dependente da unidade ativa.

---

## 8. Segurança, Login Forçado e Persistência de Navegação

- **Autenticação Obrigatória Global:**
  - Todas as rotas da aplicação (ex: `/`, `/grade`, `/funcionarios`, `/escalas`, `/gerentes`, `/painel-divgp`, etc.) são estritamente protegidas por guarda de rotas (`router.beforeEach`).
  - Caso um usuário não autenticado tente acessar qualquer endereço, é imediatamente direcionado para a página `/login` com a rota solicitada preservada no parâmetro `?redirect=...`.
  - Ao concluir a autenticação com sucesso, ele é conduzido de volta para a tela de destino solicitada.
- **Persistência Completa da Sessão:**
  - O `accessToken` e o perfil completo do usuário autenticado (`authUser`) são armazenados de forma persistente no `localStorage`.
  - O usuário navega livremente pelo sistema, recarrega a página (F5) ou abre novas abas sem perder a sessão ou o contexto de permissões do hospital.
  - No encerramento da sessão (Logout), todos os tokens e dados de sessão são eliminados e o usuário é redirecionado para a tela de login.
- **Badge do Papel Ativo no Topo da Escala:**
  - O cabeçalho da tela de escala identifica visualmente o papel e o nível do usuário logado:
    - `🛡️ Administrador do Sistema`
    - `🏢 Gerente da DIVGP`
    - `🏛️ Gerente da Unidade`
    - `📋 Supervisor de Posto`
    - `👤 Usuário Externo / Colaborador`
