# Design: melhorias-app-escala

## System Architecture

As melhorias se concentram predominantemente na interface de usuário (Frontend - Vue 3/Vite). As comunicações com a API (Backend - FastAPI) necessitarão de repasse dos novos campos (Unidade Organizacional e Posto de Serviço) para fins de filtragem e salvamento.

## Database & Models

Caso "Posto de Serviço" e "Unidade" ainda não existam no modelo de Escala (escala e itens da escala), pode ser necessária uma migração:
- Adicionar `unidade_id` e `posto_servico_id` na tabela principal de Escala (ou tabela associativa, dependendo da modelagem atual).

## API & Endpoints

- **GET /api/escalas**: Incluir suporte aos query parameters `unidade_id` e `posto_servico_id`.
- **POST /api/escalas** e **POST /api/escalas/copiar**: O payload deve suportar os campos `unidade_id` e `posto_servico_id`.

## UI Components & Views

### 1. Aba "Criar Nova Escala"
- Mudar a listagem/seleção de dias para um componente visual de Calendário (ex: componente já existente no Vuetify ou PrimeVue se em uso, ou componente customizado).
- Cada dia no calendário deve ter um *checkbox* que permita selecionar múltiplos dias de uma vez para lançar os códigos (plantões/folgas).
- Adicionar no cabeçalho ou barra lateral de informações do colaborador a exibição de sua Unidade.
- Adicionar um `<select>` ou campo de busca para definir o "Posto de Serviço".

### 2. Aba "Copiar Escala"
- Adicionar os campos de seleção para "Unidade" e "Posto de Serviço" (isso ajudará a listar os colaboradores de destino na hora de copiar a escala).
- Adicionar um ícone/botão de ação com label "Concluir" que dispare a ação efetiva de cópia.

### 3. Aba "Gerenciamento de Escala"
- Na área de filtros da tabela de gerenciamento, adicionar:
  - Input/Select para Unidade Organizacional.
  - Input/Select para Categoria.
  - Input/Select para Posto de Serviço.

## Security & Error Handling

- Validar no backend se o usuário logado tem permissão para a Unidade e Posto de Serviço informados na hora da criação ou cópia da escala.
- Validar as regras de negócio de escalas:
  - Códigos iniciados em `d` ou `n` (escala 12x36): permitidos apenas para **profissionais assistenciais**.
  - Códigos iniciados em `dn` (plantão semanal): permitidos apenas para **médicos**.
- Exibir alertas (Toasts) na interface caso falte algum preenchimento obrigatório nos novos campos ou haja quebra nas regras de negócio da escala.
