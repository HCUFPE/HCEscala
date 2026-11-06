# Tasks: Implementação da Ordenação Hierárquica por Dia / Dias Alocados com Desempate por Cargo e Nome

## Frontend Tasks
- [x] 1. Ajustar o comparador `compareByCargoAndNome` em `frontend/src/views/Grade.vue` para garantir tratamento consistente de nulos/sem cargo (`Sem Cargo`) e ordenação alfabética em português (`pt-BR`).
- [x] 2. Refinar a ordenação por dia específico (`dia_${dia}`) em `sortedMatrixData` para priorizar quem tem plantão/escala no dia selecionado e aplicar imediatamente o desempate hierárquico por Cargo e Nome.
- [x] 3. Refinar a ordenação por `dias_alocados`, `cargo` e `escala` para garantir a mesma cadeia rigorosa de desempate por Cargo e Nome.
- [x] 4. Validar visualmente no navegador o comportamento de clique nos dias do mês e botões da barra azul de ordenação.
