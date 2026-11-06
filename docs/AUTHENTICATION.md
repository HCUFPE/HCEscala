# Sistema de Autenticação e Controle de Acesso (HC Escalas)

Este documento descreve o funcionamento do sistema de autenticação, geração de tokens JWT e controle de acesso baseado em papéis e escopo organizacional do **HC Escalas**.

---

## 1. Modos de Autenticação

O sistema conta com estratégia de autenticação híbrida:

### 1.1. Modo Produção: Active Directory (LDAP)
Conecta-se ao servidor de domínio corporativo da EBSERH/HC-UFPE para validação de credenciais via *Simple Bind* seguro:
- **Variáveis de Ambiente Necessárias:**
  - `AD_URL`: URL do servidor LDAP (ex: `ldap://ad.domain.local` ou `ldaps://ad.domain.local`).
  - `AD_BASEDN`: Base DN para busca de contas e grupos (ex: `DC=ebserhnet,DC=gov,DC=br`).
  - `AD_BIND_USER` e `AD_BIND_PASSWORD`: Credenciais do usuário de serviço (opcional).

### 1.2. Modo Desenvolvimento: Mock Auth
Ativado automaticamente quando a variável `AD_URL` não estiver definida no arquivo `.env`. Permite trabalhar offline com dados e permissões completas de teste.
- **Credenciais de Teste:**
  - **Usuário:** `admin`
  - **Senha:** `admin`
  - **Grupos Injetados:** Concede o grupo de administração de TI (`GLO-SEC-HCPE-SETISD`) e perfil de `DIVGP.`, permitindo acesso total a todas as rotas e funções do sistema.

---

## 2. Fluxo de Sessão e Tokens JWT

1. **Login (`POST /api/auth/login`):**
   - Recebe `username` e `password`.
   - Autentica no AD/LDAP ou via Mock.
   - Em caso de sucesso, gera um **Access Token JWT** assinado com o segredo `JWT_SECRET`.
   - Gera um **Refresh Token** de longa duração gravado com flag `HttpOnly` em cookie seguro.

2. **Autorização nas Requisições:**
   - O cliente frontend envia o cabeçalho `Authorization: Bearer <token>` em todas as chamadas à API via interceptor do Axios (`frontend/src/services/api.ts`).
   - O middleware `auth_handler.decode_token` valida a assinatura e expiração do token.

3. **Renovação Transparente (`POST /api/auth/refresh`):**
   - Caso o Access Token expire, o frontend utiliza o Refresh Token para obter um novo token sem desconectar o usuário.

---

## 3. Matriz de Perfis e Permissões (4 Papéis + Usuário Final)

| Perfil / Papel | Critério de Detecção | Permissões no Sistema |
| :--- | :--- | :--- |
| **1. Supervisor de Posto de Serviço** | Usuário cadastrado no nível `POSTO` | • Elabora manualmente ou copia escalas dos colaboradores do seu posto (ou múltiplos postos).<br>• Status inicial da escala: **⚪ Em Elaboração**.<br>• Submete para a chefia da unidade através da ação **"Aprovar para Unidade"**. |
| **2. Gerente da Unidade** | Usuário cadastrado no nível `UORG` / Unidade | • Valida as escalas de todos os postos de sua unidade.<br>• Se encontrar divergências: **"Devolver para Correção do Chefe do Posto"**.<br>• Estando tudo correto: **"Enviar para DIVGP"** para homologação final. |
| **3. Gerente da DIVGP** | Usuário com nível `DIVGP_ADMIN` ou grupo AD `DIVGP` | • Valida e homologa as escalas recebidas de todas as unidades hospitalares.<br>• Publica a escala (**🟢 Publicada**), oficializando-a para visualização do usuário final e bloqueando edições.<br>• Pode devolver para a unidade caso identifique inconformidades. |
| **4. Administrador do Sistema** | Usuário `admin` ou grupo AD `GLO-SEC-HCPE-SETISD` | • Acesso irrestrito a todas as funcionalidades do sistema (UORGs, postos, funcionários, atribuição de chefias/gerências, legendas, auditoria, cadastros, reabertura de escalas). |
| **Usuário Final / Consulta Geral** | Colaboradores autenticados sem função de gestão | • Visualização das escalas **publicadas** para consulta de seus plantões e horários de trabalho (sem permissão de edição). |

---

## 4. Escopo Hierárquico de Unidades Organizacionais

O endpoint `GET /api/gerencias/meu-escopo` (ou `GET /api/gerencias/me`) retorna dinamicamente a árvore de UORGs e postos permitidos para o usuário conectado:
- **Administrador ou Gerente da DIVGP:** `uorg_ids = null` e `posto_ids = null` (significa acesso global irrestrito a todo o hospital).
- **Gerente de Unidade:** `uorg_ids = [id1, id2, ...]` (inclui a unidade gerenciada e recursivamente todas as suas subordinadas em cascata).
- **Supervisor de Posto:** `posto_ids = [p1, p2, ...]` e `uorg_ids = [u1, ...]` (restrito exclusivamente aos postos de serviço sob sua responsabilidade).
- **Usuário Final / Colaborador:** visualiza apenas escalas já oficializadas e publicadas.
- O dropdown de seleção de unidades na Grade filtra automaticamente para exibir apenas o escopo autorizado ao usuário logado.

---

## 5. Login Obrigatório Global e Persistência de Sessão

- **Obrigatoriedade de Autenticação:**
  - Todas as páginas e recursos da aplicação são protegidos contra acesso anônimo via `router.beforeEach`.
  - Ao entrar em qualquer URL sem credenciais ativas, o sistema redireciona automaticamente para `/login?redirect={url}`, garantindo retorno fluido à página desejada após o login.
- **Persistência de Dados e Sessão:**
  - O token JWT (`accessToken`) e o objeto do usuário logado (`authUser`) são armazenados no `localStorage` do navegador.
  - O usuário permanece autenticado durante toda a navegação, permitindo alternar abas ou atualizar a página (F5) sem interrupções.
  - Ao executar o Logout, todos os dados salvos em cache e cookies de sessão são purgados imediatamente.
