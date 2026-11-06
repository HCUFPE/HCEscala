# Specification: Auditoria e Logs de Alterações no Banco de Dados

## Overview
Esta especificação define os requisitos, arquitetura e comportamento do módulo de **Auditoria e Logs de Alterações no Banco de Dados**, projetado para registrar de maneira imutável todas as inclusões, edições, exclusões e reversões de dados efetuadas na aplicação, assegurando controle de acesso restrito ao Administrador, capacidade de pesquisa refinada e recuperação de dados por reversão assistida.

---

## Requirements

### 1. Modelo de Dados e Persistência (`AuditLog`)

1.1. **Entidade `AuditLog` (Tabela `audit_logs`)**:
- `id`: Inteiro, Chave Primária (Auto-incremento).
- `usuario`: String (até 100 caracteres), armazenando o login/matrícula/username da rede do operador autenticado no momento da operação (ex: `admin`, `m.silva`). Não nulo.
- `tela`: String (até 100 caracteres), identificação amigável do módulo ou tela de interface de onde a alteração se originou (ex: `'Cargos'`, `'Funcionários'`, `'Códigos de Escala'`, `'Feriados'`, `'Unidades Organizacionais'`, `'Gerentes & Chefias'`, `'Grade de Escala'`). Não nulo.
- `tabela`: String (até 100 caracteres), nome da tabela física no banco de dados afetada (ex: `'cargos'`, `'funcionarios'`, `'escalas'`, `'feriados'`, `'uorgs'`, `'usuario_gerencias'`). Não nulo.
- `operacao`: String (até 20 caracteres), tipo de operação executada:
  - `INSERT`: Criação de novo registro.
  - `UPDATE`: Modificação de campos em registro existente.
  - `DELETE`: Exclusão de registro.
  - `REVERT`: Operação de reversão de um log anterior realizada pelo administrador.
- `registro_id`: String (até 100 caracteres), valor da chave primária (ID) do registro afetado. Não nulo.
- `dados_anteriores`: Texto longo (JSON stringificado), contendo o snapshot das colunas e valores do registro antes da modificação (nulo para operações de `INSERT`).
- `dados_posteriores`: Texto longo (JSON stringificado), contendo o snapshot das colunas e valores do registro após a modificação (nulo para operações de `DELETE`).
- `data_hora`: Timestamp com fuso horário, gerado automaticamente no momento da persistência.
- `revertido`: Booleano, padrão `False`. Indica se a alteração registrada por este log já foi desfeita.
- `revertido_por`: String (até 100 caracteres), login do administrador que disparou a reversão. Nulo se ainda não revertido.
- `revertido_em`: Timestamp com fuso horário da execução da reversão. Nulo se ainda não revertido.

---

### 2. Controle de Acesso e Permissões

2.1. **Acesso Exclusivo para Administrador**:
- **Backend**: Todos os endpoints sob o prefixo `/api/audit-logs` devem exigir validação do grupo de administradores (dependência `verify_admin_group` / grupo `GLO-SEC-HCPE-SETISD` ou papel de admin do sistema).
  - Tentativas de acesso por usuários comuns sem o privilégio de administrador resultam em resposta `HTTP 403 Forbidden`.
- **Frontend**:
  - O item de navegação **"Logs & Auditoria"** na barra lateral (`DefaultLayout.vue`) só é renderizado quando `authStore.isAdmin` for verdadeiro (`v-if="authStore.isAdmin"`).
  - A rota `/audit-logs` no Vue Router possui metadado `requiresAdmin: true`. Caso um usuário sem privilégios tente acessar diretamente a URL, o `router.beforeEach` intercepta a navegação e o redireciona imediatamente para a rota raiz (`/`).

---

### 3. Filtros e Pesquisa na Interface

3.1. A interface de visualização de auditoria deve fornecer os seguintes critérios de filtragem combináveis:
1. **Filtro por Tela / Módulo**: Seletor dinâmico carregando as telas que possuem histórico de alteração registrado (`GET /api/audit-logs/telas`).
2. **Filtro por Usuário**: Campo de busca textual por login de rede (ex: `admin`, `joao.silva`).
3. **Filtro por Operação**: Seleção entre `Todas`, `INSERT`, `UPDATE`, `DELETE` ou `REVERT`.
4. **Filtro por Período**:
   - **Data Inicial**: Limite inferior de data para o evento.
   - **Data Final**: Limite superior de data para o evento.
3.2. Ação de **Limpar Filtros**: Restaura os parâmetros de busca para os valores padrão.
3.3. **Paginação**: Suporte a paginação com contagem de total de itens encontrados e itens exibidos.

---

### 4. Visualização de Detalhes (Antes / Depois)

4.1. Ao clicar na ação **"Detalhes"** de uma linha da tabela, a interface deve exibir um modal com comparativo estruturado:
- **Estado Anterior**: Exibição dos dados antes da alteração, formatados em JSON com realce visual.
- **Estado Posterior**: Exibição dos dados resultantes da alteração, formatados em JSON com realce visual.
- Identificação clara de quem alterou, quando e qual a operação realizada.

---

### 5. Mecanismo de Reversão de Alterações

5.1. O administrador poderá reverter uma alteração não revertida via endpoint `POST /api/audit-logs/{id}/revert`.
5.2. O comportamento da reversão é determinado pelo tipo original da operação:
- **Reversão de `UPDATE`**: Os campos do registro no banco são restaurados para os valores salvos em `dados_anteriores`.
- **Reversão de `INSERT`**: O registro inserido é excluído fisicamente do banco de dados (`DELETE FROM tabela WHERE id = :pk`).
- **Reversão de `DELETE`**: O registro é recriado na tabela correspondente com os dados persistidos em `dados_anteriores`.
5.3. **Imutabilidade e Rastreabilidade da Reversão**:
- Ao concluir a reversão, o log original tem seu campo `revertido` alterado para `True`, registrando o autor (`revertido_por`) e data/hora (`revertido_em`).
- Um novo log de auditoria com `operacao = 'REVERT'` é gerado no banco de dados para documentar a própria ação de reversão.
- Logs com status `revertido == True` ou com operação `REVERT` não permitem nova reversão direta, prevenindo ciclos inconsistentes.

---

### 6. Endpoints da API REST (FastAPI)

- `GET /api/audit-logs`: Listagem paginada de logs com filtros (`tela`, `usuario`, `operacao`, `data_inicio`, `data_fim`, `limit`, `offset`). Restrito a Admin.
- `GET /api/audit-logs/telas`: Retorna a lista distinta de telas registradas para preenchimento de filtros. Restrito a Admin.
- `GET /api/audit-logs/{id}`: Retorna os detalhes de um log específico pelo ID. Restrito a Admin.
- `POST /api/audit-logs/{id}/revert`: Executa a reversão da alteração especificada e registra a ação. Restrito a Admin.
