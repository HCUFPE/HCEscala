# Proposal: create-escalas-screen

## Why
Precisamos de um gerenciamento das escalas de trabalho existentes no sistema. O objetivo é permitir que os usuários configurem e armazenem as jornadas (horários de início e fim), associem códigos e siglas, e definam restrições de uso (ex: se aplicável a todas as categorias ou apenas às assistenciais). Isso garantirá que as informações fiquem persistidas no banco de dados para serem utilizadas em outras partes da aplicação.

## What
- Criar uma nova tabela/modelo no banco de dados para armazenar as **Escalas**.
- Os campos necessários para a escala são:
  - **Início Jornada** (Hora/Minuto)
  - **Fim Jornada** (Hora/Minuto)
  - **Código** (Identificador único ou código interno)
  - **Sigla** (Abreviação da escala)
  - **Indicador de Categoria** (Booleano/Enum indicando se pode ser usado por todas as categorias ou apenas assistenciais)
  - **Login** (Usuário que criou ou alterou o registro)
  - **Data de Alteração** (Timestamp da última modificação do registro)
- Criar endpoints na API (FastAPI) para realizar o CRUD (Criar, Ler, Atualizar, Deletar) das escalas.
- Criar uma tela no frontend (Vue 3) permitindo que o usuário visualize e cadastre as escalas através de um formulário.

## Impact
- **Banco de Dados**: Criação de modelo SQLAlchemy e arquivo de migração do Alembic para a nova entidade `escala`.
- **Backend (FastAPI)**: Novos arquivos de `router` e `controller` para as escalas.
- **Frontend (Vue/Vite)**: Nova página/componente Vue e adição de rota no frontend para acessar o gerenciamento de escalas.
