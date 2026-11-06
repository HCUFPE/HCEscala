# Proposal: Gerenciamento de Grade do Colaborador

## Problem Statement
Atualmente, a tela de **Grade** (`Grade.vue`) funciona apenas como um protótipo estático de interface com dados ilustrativos. Os gestores e chefias de unidade do Hospital das Clínicas (HC/UFPE) necessitam de uma solução completa, integrada e dinâmica para gerenciar a escala mensal de trabalho dos seus colaboradores.

Para viabilizar a gestão operacional das escalas, o sistema precisa:
1. **Controle de Acesso por Unidade**: Permitir que o usuário visualize e gerencie apenas as unidades organizacionais para as quais possui permissão de acesso (gestores de setor/unidade ou administradores).
2. **Filtros e Busca Abrangentes**: Filtrar por mês/ano de referência, unidade organizacional e categoria profissional (cargo), além de busca textual em tempo real por nome ou SIAPE/matrícula do colaborador.
3. **Indicadores de Gestão em Tempo Real**: Exibir cartões de métricas consolidadas do setor/unidade no mês selecionado:
   - Total de colaboradores no setor/unidade selecionada;
   - Quantidade de colaboradores em gozo de férias/afastamento no período;
   - Quantidade de colaboradores lotados em mais de um posto de serviço/unidade (múltiplas lotações).
4. **Matriz de Grade Mensal Dinâmica**: Visualizar a distribuição dos turnos/escalas (ex: Manhã `M`, Tarde `T`, Noite `N`, Férias `FE`, Folga `F`) ao longo de todos os dias do mês selecionado (1 a 28/29/30/31), com destaque para fins de semana e feriados.
5. **Ações de Produtividade na Mesma Tela**:
   - **Criar Nova Grade**: Possibilidade de cadastrar a escala mensal de um colaborador selecionado para o mês de trabalho.
   - **Copiar Grade**: Funcionalidade rápida para clonar a escala de um colaborador existente para outro colaborador (ou replicar de meses anteriores), agilizando o preenchimento de plantões e escalas padronizadas.

## Proposed Solution
Desenvolver a funcionalidade ponta a ponta seguindo o padrão arquitetural em camadas do projeto (**SQL/SQLAlchemy -> Provider -> Controller -> Router -> Vue 3 Frontend**):
- **Modelagem de Dados**: Criar as entidades `Grade` (cabeçalho mensal por colaborador/unidade/mês/ano) e `GradeDia` (registros diários de turno/escala/legenda para cada dia do mês).
- **Serviço de Indicadores**: Implementar agregação no backend para calcular os números de colaboradores na unidade, colaboradores de férias (`FuncionarioFerias`) e colaboradores com múltiplas lotações (`FuncionarioLotacao`).
- **Serviço de Cópia e Criação de Grade**: Endpoint transacional para criação unitária e clonagem de grade entre colaboradores com preenchimento em lote dos dias.
- **Interface Reativa no Frontend**: Evoluir a página `frontend/src/views/Grade.vue` para consumir os novos endpoints, com reatividade completa nos filtros, grid mensal interativo com legendas coloridas e modais de criação e cópia de grade.

## Goals
- Criar modelos `Grade` e `GradeDia` com migração Alembic correspondente.
- Implementar camada de backend (`grade_provider.py`, `grade_controller.py`, `src/routers/grade.py`) com validações Pydantic e controle de permissões por unidade do usuário autenticado.
- Implementar cálculo de indicadores de equipe por unidade/mês.
- Implementar mecanismo de clonagem/cópia de grade entre colaboradores.
- Refatorar a visualização da tela `Grade.vue` com suporte a filtros (mês/ano, unidade autorizada, categoria, pesquisa por nome/SIAPE), cards de indicadores dinâmicos e tabela de grade interativa.
- Adicionar modais modernos de "Criar Nova Grade" e "Copiar Grade".

## Non-Goals
- Integração em tempo real com relógio de ponto eletrônico biométrico (será abordado em módulo posterior de apuração de frequência).
- Assinatura digital por certificado ICP-Brasil (será tratada no fluxo de homologação avançada).
