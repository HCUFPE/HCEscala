# Tasks: melhorias-app-escala

- [ ] **Backend (API)**
  - [ ] Validar e adicionar as colunas/relacionamentos de `unidade_id` e `posto_servico_id` nos models de Escala (se ainda não existirem).
  - [ ] Gerar migration Alembic para a adição dos novos campos, caso necessário.
  - [ ] Atualizar os schemas Pydantic de criação e retorno (DTOs) para suportar os novos campos.
  - [ ] Implementar validação nas rotas de criação/atualização de escala para bloquear códigos iniciados em `d` ou `n` se o profissional não for assistencial.
  - [ ] Implementar validação nas rotas para bloquear códigos iniciados em `dn` se o profissional não for médico.
  - [ ] Atualizar o método `GET /api/escalas` (ou equivalente no controller) para processar os filtros de Unidade Organizacional, Categoria e Posto de Serviço.
  - [ ] Garantir que o endpoint de Cópia e de Criação recebam e gravem o `posto_servico_id` corretamente.

- [ ] **Frontend (Vue/Vite) - Aba "Criar Nova Escala"**
  - [x] Adaptar o combo de preenchimento rápido para carregar e listar os códigos de escala cadastrados no banco com horários e sigla.
  - [x] Criar o botão e modal interativo "Selecionar Dias..." com calendário/checkboxes para seleção múltipla e aplicação em lote.
  - [x] Restringir os campos diários manuais e de preenchimento rápido aos códigos de escala cadastrados.
  - [x] Adicionar validação visual (preventiva) para impedir ou avisar ao usuário quando tentar lançar escalas `d`, `n` (apenas assistencial) ou `dn` (apenas médico) incorretamente.
  - [x] Exibir de forma visual a Unidade atual do colaborador na tela de nova escala.
  - [x] Adicionar um campo tipo Select para o usuário informar o Posto de Serviço.

- [ ] **Frontend (Vue/Vite) - Aba "Copiar Escala"**
  - [x] Adicionar inputs/selects para Unidade e Posto de Serviço.
  - [x] Integrar os inputs à lógica que busca a lista de colaboradores alvo (destinatários da cópia).
  - [x] Atualizar o botão final da operação para exibir o ícone "Concluir" (ex: `mdi-check`, `mdi-content-save` ou equivalente no Vue/Vuetify).

- [ ] **Frontend (Vue/Vite) - Aba "Gerenciamento de Escala"**
  - [x] Adicionar os inputs para Unidade, Categoria e Posto de Serviço na seção superior (filtros) da tabela.
  - [x] Vincular as variáveis reativas (Vue Refs) dos filtros à chamada da API que lista as escalas (`GET`).
