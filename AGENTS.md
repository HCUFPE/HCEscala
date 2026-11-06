# AGENTS.md — Manifesto de Governança de Agentes de IA (Framework SETISD)

> **Instituição:** Hospital das Clínicas da UFPE (HC-UFPE / EBSERH)  
> **Sistema:** HC Escalas — Sistema de Gestão de Escalas de Serviço  
> **Padrão Arquitetural:** Framework SETISD (Python 3.12+ / FastAPI + Vue 3 / TypeScript)

---

## 1. Diretrizes Gerais para Agentes de IA

Todo agente de IA que inspecionar, criar ou modificar código neste repositório deve obedecer estritamente aos **10 Pilares do Framework SETISD**:

1. **Autenticação Corporativa AD/LDAP (`src/auth/auth.py`):** Autenticação realizada via Active Directory (`EBSERHNET`) e consulta LDAP.
2. **Conectividade Híbrida & Controle de Acesso RBAC:** Autenticação no AD combinada com autorização e perfis locais no banco de dados da aplicação (`UsuarioPerfil`, `UsuarioGerencia`).
3. **Autenticação Persistente & Cookies HttpOnly (`src/routers/auth.py`):** Refresh tokens armazenados exclusivamente em cookies `HttpOnly`.
4. **Proteção de Rotas por Padrão (Default-Private Router Pattern):** Todos os roteadores em `src/routers/` (exceto `auth.py` e `health.py`) devem declarar `dependencies=[Depends(auth_handler.decode_token)]` ou validação equivalente por rota.
5. **Security Headers HTTP (`src/main.py`):** Respostas protegidas com `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection` e `Cache-Control: no-store` para rotas `/api`.
6. **Governança de Segredos (`src/config.py` & `.env.example`):** Nenhum segredo deve ser hardcoded no código-fonte. Toda configuração deve ser centralizada em `src/config.py` e documentada em `.env.example`.
7. **Trilha de Auditoria Imutável (`src/models/audit_log.py` & `src/helpers/audit_helper.py`):** Operações críticas de mutação devem registrar usuário, categoria/entidade, ação, estado anterior (`dados_anteriores`), novo estado (`dados_novos`) e origem (`ip_origem`).
8. **Arquitetura em Camadas:** Respeitar o fluxo `SQL / Model -> Resource -> Provider -> Controller -> Router`.
9. **Padrão Visual Frontend (`frontend/`):** Layout com menu lateral à esquerda (`DefaultLayout.vue` / `SidebarNav`), identificação institucional HC-UFPE / EBSERH no topo e versão semântica (`APP_VERSION`) no rodapé.
10. **Monitoramento & Versionamento Semântico (`/api/health` & SemVer):** Manter o endpoint `/api/health` ativo para o Zabbix e atualizar a versão semântica em `src/version.py` e `frontend/src/config/version.ts`.

---

## 2. Convenções de Código

- **Python (Backend):** Usar `snake_case`, `async/await`, `type hints` e docstrings claras.
- **TypeScript / Vue 3 (Frontend):** Usar `camelCase` para variáveis/funções e `PascalCase` para componentes Vue.
- **Verificação de Conformidade:** Executar `python audit_framework.py` após alterações arquiteturais para garantir 100% de adesão ao Framework SETISD.

