# Specification: Escalas

## Overview
Esta especificação define o comportamento do gerenciamento de escalas (schedules) no sistema.

## Requirements

1. **Modelo de Dados (Backend)**
   - O sistema deve persistir as seguintes informações para cada Escala:
     - `id`: Inteiro, Chave Primária (auto-incremento).
     - `inicio_jornada`: Horário (Time) de início da jornada.
     - `fim_jornada`: Horário (Time) de término da jornada.
     - `codigo`: String ou inteiro que identifica a escala.
     - `sigla`: String curta representando a escala (deve ser única na tabela).
     - `descricao`: String descritiva detalhando o código/escala.
     - `apenas_assistenciais`: Booleano indicando se a escala é restrita a categorias assistenciais (true) ou aplicável a todas as categorias (false).
     - `login`: String contendo o username/identificador do usuário responsável pela criação/alteração.
     - `data_alteracao`: Data e hora (Timestamp) da última modificação no registro.

2. **API (Backend)**
   - Criar endpoints RESTFul (GET, POST, PUT, DELETE) na rota `/api/escalas`.
   - Garantir validação dos dados de entrada (Pydantic models) para garantir que o horário de início e fim sejam horários válidos.
   - Garantir que a `sigla` seja única, retornando erro apropriado (HTTP 400) em caso de duplicidade.

3. **Interface de Usuário (Frontend)**
   - O sistema deve exibir uma tela de listagem de escalas cadastradas em formato de tabela.
   - **Ordenação Dinâmica de Colunas**: O usuário deve poder ordenar os registros clicando em qualquer cabeçalho de coluna da tabela (ID, Sigla, Descrição, Horários, Restrição Assistencial, Usuário e Data de Alteração), alternando entre ascendente, descendente e exibindo indicadores visuais (`↕`, `▲`, `▼`).
   - O sistema deve fornecer um formulário (modal) para criar uma nova escala ou editar uma existente, contendo validações para código, sigla e descrição.
   - O design da tela deve seguir as melhores práticas estéticas definidas para o projeto, utilizando Vue 3, layout limpo e interações dinâmicas (micro-animações).

4. **Consistências Cruzadas e Regras de Exclusão**
   - **Exclusão de Escala**:
     - Não é permitida a exclusão se a escala estiver configurada como padrão de algum colaborador (`Funcionario.escala_id`).
     - Não é permitida a exclusão se a escala tiver sido utilizada em lançamentos diários de qualquer grade de serviço (`GradeDia.escala_id`).
     - Em caso de violação, o sistema retorna erro HTTP 400 informando os vínculos existentes.
