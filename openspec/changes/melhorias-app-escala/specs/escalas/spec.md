# Spec: Melhorias no App de Escalas

## User flows & requirements

### 1. Criação de Escalas
- **Contexto**: O usuário (gestor) acessa o modal ou aba "Criar nova escala" para definir os plantões do mês para um colaborador.
- **Mudança**:
  - A interface deve exibir a **Unidade** do colaborador e permitir associar o **Posto de Serviço** (ComboBox/Select).
  - No assistente de **Preenchimento Rápido**, o combo de seleção de códigos deve carregar e exibir os **códigos de escala cadastrados** (com sigla, horários e indicação assistencial) além de legendas gerais.
  - Deve existir um botão dedicado **"Selecionar Dias..."** que abre um modal interativo em formato de calendário/grid com checkboxes para todos os dias do mês:
    - O usuário seleciona visualmente os dias desejados (com botões de atalho como "Todos", "Dias Úteis", "Fins de Semana" e "Limpar").
    - Ao confirmar, o código selecionado no combo de preenchimento rápido é aplicado de imediato a todos os dias marcados.
  - O preenchimento diário manual e rápido deve ser restrito e validado conforme os códigos de escala cadastrados e regras de negócio:
    - Códigos iniciados com `d` ou `n`: representam plantão 12x36. Apenas para **profissionais assistenciais**.
    - Códigos iniciados com `dn`: representam um plantão por semana. Apenas para **médicos**.

### 2. Cópia de Escalas
- **Contexto**: O usuário deseja replicar uma escala pronta para outros colaboradores que têm a mesma jornada.
- **Mudança**:
  - Inclusão dos filtros **Unidade** e **Posto de Serviço** na aba.
  - O sistema usará esses filtros para listar corretamente os colaboradores elegíveis para receber a cópia da escala.
  - Adição visual de um ícone de "Concluir" no botão de ação da cópia, reforçando o sucesso da operação ou indicando o fim do fluxo.

### 3. Gerenciamento de Escalas
- **Contexto**: O usuário visualiza a lista geral de escalas na aba "Gerenciamento de escala".
- **Mudança**:
  - A barra de pesquisa/filtros desta tela deve ser expandida.
  - O usuário deve poder filtrar a listagem selecionando uma **Unidade Organizacional**, uma **Categoria** (ex: Assistencial, Administrativo) e um **Posto de Serviço**.

## Acceptance Criteria
- [ ] Na aba "Criar nova escala", os dias do mês aparecem em layout de calendário com checkboxes, mostrando as escalas possíveis para o dia ou branco.
- [ ] O sistema impede a atribuição de códigos iniciados em `d` ou `n` (12x36) para profissionais que não são da categoria assistencial.
- [ ] O sistema impede a atribuição de códigos iniciados em `dn` (plantão semanal) para profissionais que não são médicos.
- [ ] Na aba "Criar nova escala", é possível marcar 3 dias e aplicar o mesmo código de uma só vez para os dias selecionados.
- [ ] Na aba "Criar nova escala", a Unidade do colaborador e o campo Posto de Serviço estão visíveis.
- [ ] Na aba "Copiar escala", os filtros Unidade e Posto de Serviço estão presentes e afetam a lista de colaboradores destino.
- [ ] Na aba "Copiar escala", o botão de conclusão possui um ícone claro indicando a ação.
- [ ] Na aba "Gerenciamento de escala", a busca permite filtrar a tabela pelos três novos campos (Unidade Org, Categoria, Posto de Serviço).
