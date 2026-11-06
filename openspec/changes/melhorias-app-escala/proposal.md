# Proposal: melhorias-app-escala

## Why
É necessário aprimorar a usabilidade e os filtros no gerenciamento de escalas para facilitar a criação, cópia e gestão, garantindo que o usuário tenha todas as informações e filtros necessários de forma intuitiva, em conformidade com as regras de negócio de alocação de postos de serviço e unidades.

## What
- **Criar nova escala (Aba 1):**
  - Alterar a forma de preenchimento dos dias para exibir um calendário com seleção via *checkbox*, permitindo lançar os códigos.
  - Incluir exibição da Unidade do colaborador.
  - Incluir o campo de Posto de Serviço.
- **Copiar escala (Aba 2):**
  - Acrescentar a Unidade e o Posto de Serviço para possibilitar o filtro posterior de quais colaboradores terão a escala replicada/copiada.
  - Acrescentar o ícone de concluir (botão ou ação visual).
- **Gerenciamento de escala (Aba 3):**
  - Incluir campo de busca/filtro para Unidade Organizacional.
  - Incluir campo de busca/filtro para Categoria.
  - Incluir campo de busca/filtro para Posto de Serviço.

## Impact
- **Frontend (Vue/Vite):** Alterações nos componentes das abas "Criar nova escala", "Copiar escala" e "Gerenciamento de escala" para introduzir novos inputs, calendário, botões e filtros.
- **Backend (FastAPI):** Ajustar controllers e rotas (se necessário) para retornar e aceitar os novos filtros de Unidade Organizacional e Posto de Serviço ao salvar/consultar/copiar as escalas.
