# Design: Unidades Organizacionais

## Architecture
- **Models**:
  - `Setor` (`src/models/setor.py`)
  - `Unidade` (`src/models/unidade.py`): terá um `relationship` com `Setor`.
  - `Posto` (`src/models/posto.py`): terá um `relationship` com `Unidade`.
- **Providers & Controllers**: Cada entidade terá o seu par de Provider e Controller seguindo o padrão já utilizado em Cargos e Vínculos.
- **Routers**: Rotas dedicadas com Schemas do Pydantic utilizando `ConfigDict(from_attributes=True)` para serialização correta das relações.
- **Frontend**: Uma única página `Organizacao.vue` para centralizar o cadastro das 3 entidades usando navegação por abas horizontais ou listagens agrupadas. Isso poupa espaço no menu lateral e melhora a experiência ao montar a árvore hierárquica.

## Data Types
Todos seguirão a restrição `login` obrigatória e automática pelo backend, capturando o token do FastAPI Depends, assim como a `data_alteracao` automatizada. A chave primária é do tipo Inteiro com Autoincremento, cumprindo com a exigência universal.
