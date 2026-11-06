# Spec: Feriados

## Modelagem de Dados

### Entidade `Feriado`
- `id` (PK, Integer)
- `nome` (String, obrigatório): Nome descritivo (ex: "Confraternização Universal")
- `data` (Date, obrigatório): Data exata do feriado
- `tipo` (String, obrigatório): "Nacional", "Estadual", "Municipal", ou "Institucional"
- `login` (String, obrigatório): Auditoria
- `data_alteracao` (DateTime): Auditoria

## Comportamentos (Regras de Negócio)
1. **Unicidade**: Não deve ser possível cadastrar dois feriados na mesma `data` com o mesmo `nome`.
2. **Consultas**: O endpoint de listagem deverá poder receber um parâmetro opcional `ano` para retornar apenas os feriados daquele ano.

## Endpoints da API

- `GET /api/feriados`: Lista todos os feriados ordenados por data. Pode receber query params `ano`, `mes`.
- `POST /api/feriados`: Cria um novo feriado.
- `PUT /api/feriados/{id}`: Atualiza os dados de um feriado.
- `DELETE /api/feriados/{id}`: Remove o feriado permanentemente.

## Interface (Frontend)
- View `Feriados.vue` com listagem em tabela e modal de cadastro/edição.
- **Ordenação Dinâmica de Colunas**: Os cabeçalhos das colunas (Data, Nome/Descrição e Tipo de Feriado) são clicáveis e permitem alternar a ordenação entre ascendente e descendente com ícones visuais (`↕`, `▲`, `▼`).
