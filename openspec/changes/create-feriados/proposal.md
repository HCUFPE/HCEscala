# Proposta: Cadastro de Feriados

## O que será feito
Implementar uma funcionalidade para cadastrar, listar, editar e excluir feriados por ano. Isso permitirá que os feriados sejam gerenciados de forma centralizada e utilizados futuramente na geração e validação das escalas dos funcionários (por exemplo, diferenciando carga horária ou plantões em dias de feriado).

## Por que é necessário
Atualmente, o sistema possui o cadastro de escalas e de funcionários, mas não tem ciência de quais dias são feriados (nacionais, estaduais ou municipais). Ao criar escalas para unidades que funcionam 24x7, ou mesmo unidades diaristas, é fundamental saber quando cai um feriado para calcular corretamente folgas, pagamentos extras ou horas trabalhadas.

## Requisitos principais
- **CRUD de Feriados**:
  - Criar feriado informando: `nome` (ex: Natal, Ano Novo), `data` (Dia/Mês/Ano), `tipo` (Nacional, Estadual, Municipal, Institucional).
  - Listar feriados com filtros por `ano`.
  - Atualizar ou Excluir feriados existentes.
- **Banco de Dados**: 
  - Tabela `feriados` com os campos acima e integração com SQLAlchemy.
- **Frontend**:
  - Nova tela `Feriados.vue` acessível via menu lateral.
  - Tabela de listagem e Modal de formulário seguindo o padrão atual do sistema.
