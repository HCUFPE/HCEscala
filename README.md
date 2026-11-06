# HC Escalas — Sistema de Gestão de Escalas de Serviço (HC-UFPE / EBSERH)

Sistema corporativo Full-Stack para elaboração, homologação, publicação e auditoria das escalas de serviço dos colaboradores do **Hospital das Clínicas da UFPE / EBSERH**.

O sistema é construído sobre uma arquitetura monolítica moderna em **Python (FastAPI)** no backend e **Vue 3 (Vite + TypeScript + Tailwind CSS)** no frontend, integrando dados organizacionais de RH e sistemas hospitalares (AGHU/PostgreSQL e Oracle).

---

## 🌟 Principais Funcionalidades

- **Matriz de Escalas Mensal (`/grade`):**
  - Calendário interativo diário para escala de turnos (M, T, N, D, 12x36, etc.).
  - Controle e validação de carga horária em tempo real (limite mensal de 20h, 30h, 40h).
  - Regimes especiais: detecção automática de Diaristas (segunda a sexta com folgas automáticas em feriados oficiais).
  - Identificação de múltiplos vínculos e divisão de carga entre unidades hospitalares.
  - Alocação e controle de períodos de Férias Regulamentares.

- **Fluxo de Aprovação e Publicação Hierárquico:**
  - `Em Elaboração` (Chefe do Posto) ➔ `Enviada para Unidade` (Chefe da Unidade) ➔ `Publicada` (DIVGP).
  - Alçada com suporte a devolução: Chefe da Unidade pode devolver para correção do Chefe do Posto com justificativa.
  - Escala publicada na DIVGP fica homologada, oficializada e bloqueada para alterações.
  - Painel consolidado da Divisão de Gestão de Pessoas (`/painel-divgp`).

- **Gestão de Pessoas e Lotações (`/funcionarios`):**
  - Cadastro completo de colaboradores (EBSERH, RJU, Cedidos, Temporários).
  - Histórico de lotações ativas por Unidade Organizacional (UORG) e Posto de Serviço.
  - Gestão de períodos aquisitivos e usufruto de férias.

- **Estrutura Organizacional Hierárquica (`/organizacao`):**
  - Árvore hierárquica das Unidades Organizacionais (UORGs) com importação direta de planilhas oficiais de estrutura.
  - Gerenciamento de Postos de Serviço vinculados ou independentes.
  - Permissões por escopo de lotação e perfis administrativos.

- **Cadastros de Apoio e Parâmetros:**
  - **Escalas e Turnos (`/escalas`):** Definição de horários de início e término de plantões.
  - **Legendas de Plantão (`/legendas`):** Siglas padronizadas para grade.
  - **Cargos e Cargas Horárias (`/cargos`):** Configuração de cargos com jornada semanal (permitindo mesma descrição com diferentes cargas horárias através de restrição composta `nome + carga_horaria`).
  - **Vínculos Jurídicos (`/vinculos`):** Tipos de contrato com a instituição.
  - **Feriados Oficiais (`/feriados`):** Calendário anual de feriados nacionais, estaduais e municipais.
  - **Logs de Auditoria (`/audit-logs`):** Registro de alterações com autor, data/hora e valores anteriores/novos.

---

## 📌 Últimos Ajustes e Melhorias Implementadas

1. **Grade Mensal (`/grade`):**
   - **Sequência de Aprovação Hierárquica:**
     - **Chefe do Posto:** Cria/copia escalas (status inicial: `Em Elaboração`) e aprova individualmente ou em lote via botão **"Aprovar para Unidade"**.
     - **Chefe da Unidade:** Analisa todos os postos. Se encontrar divergências, utiliza **"Devolver para Correção do Chefe do Posto"**; se estiver tudo correto, envia via **"Enviar para DIVGP"**.
     - **DIVGP:** Homologa e publica a escala institucionalmente (`Publicada (DIVGP)`), ficando **bloqueada para alterações**.
   - **Cópia de Escala Inteligente:**
     - Replica escalas dos colaboradores filtrados na tela de origem mantendo a correspondência de **colaborador para ele mesmo** e **preservando o posto de serviço**.
     - **Não copia Férias (`FE`), Feriados (`FR`), Licenças/Afastamentos (`LM`, `LP`, `A`, etc.) ou Abonos (`AB`)**.
     - Respeita feriados e férias já programados no mês de destino, deixando esses dias livres.
     - Permite copiar todos os colaboradores da unidade/posto ou selecionar manualmente um a um.
   - **Alternância de Visualização (Tabela vs. Calendário):** Seletor integrado no cabeçalho superior permitindo visualizar em grade tradicional ou em formato de calendário mensal detalhado por dia.
   - **Primeira Coluna Compacta (70 caracteres):** Formatação padronizada exibindo `{SIAPE} - {Nome} ({Cargo})` limitada a 70 caracteres com tipografia otimizada e mais legível (`text-[10.5px]`), largura de `420px` e tooltip integral.
   - **Coluna de Status Dedicada:** Badges claros indicando o estágio atual: `Em Elaboração`, `Enviada para Unidade`, `Devolvida para Posto` e `Publicada (DIVGP)`.
   - **Barra de Rolagem Horizontal Superior Sincronizada:** Adicionada barra de rolagem horizontal espelhada no topo da matriz de escalas, conectada bidirecionalmente à tabela via `ResizeObserver` e `scroll synchronization`.
   - **Filtros Contextuais Refinados:**
     - Selects de **Unidade** e **Posto de Serviço** listam apenas registros que possuem colaboradores efetivamente lotados.
     - Select de **Categoria / Cargo** exibe o nome acompanhado da carga horária semanal (ex: `Enfermeiro (40h)`) e é filtrado dinamicamente com base na Unidade selecionada.
     - Indicadores de topo (Colaboradores, Férias, Múltiplas Lotações) recalculados dinamicamente em conformidade com todos os filtros aplicados.
   - **Ordenação Inteligente:** Priorização automática no topo para colaboradores que possuem escalas/plantões informados no mês, seguida de ordenação alfabética por Cargo e Nome.

2. **Gestão de Cargos (`/cargos` e `src/routers/cargo.py`):**
   - Correção na extração de identidade de usuário autenticado (`current_user.get("username") or current_user.get("sub") or "sistema"`) eliminando erro HTTP 500 (`KeyError: 'username'`) ao cadastrar ou atualizar cargos.
   - Garantia de valor padrão para campo de auditoria `login` evitando violação de constraint `NOT NULL`.
   - Tratamento detalhado de erros e mensagens de validação no formulário Vue (`Cargos.vue`).

3. **Lotações e Postos (`/funcionarios` e `/organizacao`):**
   - Lotação em lote e individual com suporte a datas retroativas/futuras (ex: Oncologia / Ambulatório).
   - Remoção de duplicidades e consistência na hierarquia de UORGs e subordinadas.

---

## 🏛️ Arquitetura do Sistema

```
                  ┌──────────────────────────────────────────────┐
                  │          Navegador Web (Usuário)             │
                  └──────────────────────┬───────────────────────┘
                                         │ HTTP / REST / WebSocket
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │        FastAPI (Backend Monolítico)          │
                  │  - /api/*        (Rotas REST Pydantic)       │
                  │  - /*            (Serve SPA Vue 3 estático)  │
                  └──────┬───────────────────────┬───────────────┘
                         │                       │
         ┌───────────────▼──────────────┐ ┌──────▼─────────────────────┐
         │     SQLite (app.db)          │ │  PostgreSQL / Oracle AGHU  │
         │ - Colaboradores & Lotações   │ │  (Acesso a dados clínicos  │
         │ - Grades, Dias e Legendas    │ │   e registros hospitalares)│
         │ - UORGs & Postos de Serviço  │ └────────────────────────────┘
         │ - Feriados e Auditoria       │
         └──────────────────────────────┘
```

### Estrutura de Pastas

```
.
├── src/                          # Backend FastAPI
│   ├── main.py                   # Ponto de entrada, lifespan e middlewares
│   ├── routers/                  # Endpoints REST (grade, funcionario, uorg, etc.)
│   ├── controllers/              # Regras de negócio e validações
│   ├── providers/                # Camada de persistência e consultas SQL
│   ├── models/                   # Modelos ORM SQLAlchemy 2.0
│   ├── resources/                # Conexões com banco de dados (SQLite, Postgres, Oracle)
│   ├── auth/                     # Autenticação LDAP/AD e tokens JWT
│   └── static/dist/              # Build estático do frontend Vue empacotado
│
├── frontend/                     # Frontend Vue 3 + TypeScript
│   ├── src/
│   │   ├── views/                # Telas (Grade, Funcionarios, Organizacao, etc.)
│   │   ├── components/           # Componentes reutilizáveis
│   │   ├── stores/               # Gerenciamento de estado (Pinia: auth, etc.)
│   │   ├── services/             # Cliente HTTP Axios configurado
│   │   └── router/               # Roteamento Vue Router com Navigation Guards
│   ├── package.json
│   └── vite.config.ts
│
├── data/                         # Arquivos de dados de carga e templates
├── docs/                         # Documentações detalhadas de arquitetura e setup
├── dados_rh.tsv                  # Dados consolidados de RH do hospital
└── app.db                        # Banco de dados local da aplicação (SQLite)
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10+
- Node.js 18+ e npm
- Gerenciador de pacotes `uv` (recomendado) ou `pip`

### 2. Configuração Inicial
Copie o arquivo de exemplo de variáveis de ambiente:
```bash
cp .env.example .env
```

### 3. Modo de Desenvolvimento (Hot Reload)
Inicie o backend e o frontend simultaneamente:
```bash
# Terminal 1 - Backend FastAPI (Porta 8080 ou 8000)
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload

# Terminal 2 - Frontend Vite (Porta 5173)
cd frontend
npm install
npm run dev
```
Acesse: **`http://localhost:5173`**

### 4. Modo Produção Local (Servidor Único)
Compila o frontend e serve tudo diretamente pela porta do FastAPI:
```bash
# Executa build do frontend e inicia o FastAPI
cd frontend && npm run build && cd ..
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080
```
Acesse: **`http://localhost:8080`**

---

## 🔐 Autenticação e Perfis

O sistema oferece autenticação híbrida:
- **Produção:** Active Directory (LDAP EBSERH / HC-UFPE).
- **Desenvolvimento Local:** Provedor Mock habilitado quando `AD_URL` não estiver configurado.
  - **Usuário padrão:** `admin` | **Senha:** `admin` (concede permissões completas de Administrador).

### Os 4 Papéis de Acesso e Governança:
1. **Supervisor de Posto de Serviço (`POSTO`):** Elabora ou copia as escalas dos colaboradores de seu posto (ou múltiplos postos). As escalas iniciam em `⚪ Em Elaboração`. Ao finalizar, aprova individualmente ou em lote via **"Aprovar para Unidade"**.
2. **Gerente da Unidade (`UORG`):** Valida as escalas de todos os postos subordinados de sua unidade. Se houver divergências, utiliza **"Devolver para Correção do Chefe do Posto"**; se estiver tudo correto, homologa e envia via **"Enviar para DIVGP"**.
3. **Gerente da DIVGP (`DIVGP_ADMIN`):** Analisa tecnicamente as escalas de todas as unidades, homologa e disponibiliza a publicação institucional (**`🟢 Publicada`**), tornando-a visível para o usuário final e bloqueando edições posteriores.
4. **Administrador do Sistema (`ADMIN`):** Alçada total sobre todas as funcionalidades, unidades, postos, usuários, auditoria, configurações e desbloqueio/reabertura de escalas.
5. **Usuário Final / Colaborador:** Acesso para visualização das escalas oficiais publicadas de seus postos.

### Autenticação Obrigatória Global e Sessão Persistente:
- **Login Forçado:** Todas as rotas da aplicação requerem login ativo. Acesso anônimo a qualquer rota redireciona compulsoriamente para `/login?redirect=...`.
- **Sessão Persistente:** O token de acesso e os dados do usuário autenticado são mantidos em `localStorage`, permitindo navegação fluida, atualização de página (F5) e abertura de abas sem deslogar.
- **Badge do Papel no Cabeçalho:** A tela de escalas identifica dinamicamente o papel de governança do usuário conectado.

---

## 📖 Documentação Detalhada

- **[Arquitetura do Sistema (docs/ARCHITECTURE.md)](./docs/ARCHITECTURE.md)**
- **[Sistema de Autenticação e Permissões (docs/AUTHENTICATION.md)](./docs/AUTHENTICATION.md)**
- **[Guia de Instalação e Execução (docs/SETUP.md)](./docs/SETUP.md)**
- **[Guia de Desenvolvimento de Módulos (docs/GUIA_DESENVOLVIMENTO.md)](./docs/GUIA_DESENVOLVIMENTO.md)**
