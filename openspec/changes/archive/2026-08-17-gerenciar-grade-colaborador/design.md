# Design: Gerenciamento de Grade do Colaborador

## Architecture
A solução segue rigorosamente o padrão monolítico em camadas do projeto estabelecido no `GEMINI.md`:
**Vue 3 Component (Frontend) -> FastAPI Router -> Controller -> Provider -> SQLAlchemy ORM (SQLite/PostgreSQL)**

```
┌───────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                      │
│   Grade.vue (Filtros, Cards Indicadores, Matriz Mensal)   │
│   ├── ModalCriarGrade.vue                                 │
│   └── ModalCopiarGrade.vue                                │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP JSON Requests (Axios)
                              ▼
┌───────────────────────────────────────────────────────────┐
│                 FastAPI Router (src/routers/grade.py)     │
│   - Validação de entrada Pydantic                         │
│   - Autenticação e extração do usuário (auth_wrapper)     │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│            Controller (src/controllers/grade_controller.py)│
│   - Lógica de negócio, permissões por unidade do usuário  │
│   - Cálculo e consolidação dos indicadores de gestão      │
│   - Orquestração da cópia de grades entre colaboradores   │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│             Provider (src/providers/grade_provider.py)    │
│   - Queries assíncronas SQLAlchemy                        │
│   - Junções com Funcionarios, Lotações, Férias, Escalas   │
│   - Operações em lote (Batch insert/copy)                 │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│               Database Models (src/models/grade.py)       │
│   - Tabelas: grades, grade_dias                           │
└───────────────────────────────────────────────────────────┘
```

---

## 1. Banco de Dados (SQLAlchemy Models)

### `src/models/grade.py`
```python
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, index=True)
    posto_id = Column(Integer, ForeignKey("postos.id"), nullable=True)
    mes = Column(Integer, nullable=False) # 1 a 12
    ano = Column(Integer, nullable=False) # ex: 2026
    status = Column(String(50), default="Rascunho", nullable=False)
    observacao = Column(String(500), nullable=True)
    
    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    funcionario = relationship("Funcionario")
    unidade = relationship("Unidade")
    posto = relationship("Posto")
    dias = relationship("GradeDia", back_populates="grade", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("funcionario_id", "unidade_id", "mes", "ano", name="uq_grade_func_unidade_mes_ano"),
    )


class GradeDia(Base):
    __tablename__ = "grade_dias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, index=True)
    dia = Column(Integer, nullable=False) # 1 a 31
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=True)
    legenda_sigla = Column(String(20), nullable=True) # ex: 'M', 'T', 'N', 'FE', 'F', 'SN'
    descricao = Column(String(100), nullable=True)

    # Relacionamento
    grade = relationship("Grade", back_populates="dias")
    escala = relationship("Escala")

    __table_args__ = (
        UniqueConstraint("grade_id", "dia", name="uq_grade_dia"),
    )
```

---

## 2. Backend (FastAPI Layer)

### `src/providers/grade_provider.py`
- **`get_grades_by_filter(session, unidade_id, mes, ano, cargo_id, search_term)`**:
  - Consulta funcionários alocados na unidade (`FuncionarioLotacao`), com seus cargos, escalas base e a grade correspondente ao mês/ano (se já cadastrada).
  - Inclui dias preenchidos (`GradeDia`) e flags de férias (`FuncionarioFerias`).
- **`get_grade_indicators(session, unidade_id, mes, ano)`**:
  - `total_colaboradores`: Contagem de funcionários ativos na unidade no mês.
  - `total_ferias`: Contagem de funcionários com registros de férias sobrepondo o mês (`data_inicio <= fim_mes` AND `data_fim >= inicio_mes`).
  - `total_multiplas_lotacoes`: Contagem de funcionários da unidade que possuem mais de 1 registro em `funcionarios_lotacoes` sem `data_fim` ou com vigência ativa no mês.
- **`create_grade(session, grade_data, dias_data, username)`**:
  - Cria cabeçalho e insere todos os itens diários em transação atômica.
- **`copy_grade(session, source_func_id, source_mes, source_ano, target_func_ids, target_mes, target_ano, unidade_id, username)`**:
  - Carrega a grade e os dias de origem.
  - Para cada funcionário de destino, cria/sobrescreve a grade do mês/ano alvo, replicando a alocação dos dias ajustada ao limite de dias do mês de destino.

### `src/controllers/grade_controller.py`
- **Validação de Regras de Negócio**:
  - Validação de ranges de mês (1-12) e ano (> 2000).
  - Verificação de autorização do usuário na unidade.
  - Formatação e estruturação dos dados retornados para a visão em matriz do frontend.
- **Pydantic Schemas**:
  - `GradeDiaCreate`, `GradeDiaResponse`
  - `GradeCreate`, `GradeUpdate`, `GradeResponse`, `GradeMatrixResponse`
  - `GradeCopyRequest`
  - `GradeIndicatorsResponse`

### `src/routers/grade.py`
- `GET /api/grades`: Listagem para a matriz mensal com filtros.
- `GET /api/grades/indicadores`: Dados para os 3 cards de resumo.
- `GET /api/grades/{id}`: Grade específica com dias.
- `POST /api/grades`: Criação de nova grade.
- `PUT /api/grades/{id}`: Atualização de grade.
- `POST /api/grades/copiar`: Endpoint para clonagem de grade.
- `DELETE /api/grades/{id}`: Exclusão de grade.

---

## 3. Frontend (Vue 3 + Tailwind/Vanilla CSS)

### `frontend/src/views/Grade.vue`
A página principal será estruturada em seções coordenadas:
1. **Cabeçalho com Seletor de Período**:
   - Mês e Ano (dropdown ou botões de navegação rápida de mês).
   - Botões de Ação Primária: **"Criar Nova Grade"** e **"Copiar Grade"**.
2. **Cards de Indicadores de Gestão**:
   - 3 cards estilizados com números em destaque:
     - 👥 **Total no Setor/Unidade**
     - 🏖️ **Férias/Afastamentos no Mês**
     - 🔄 **Múltiplos Postos / Lotações**
3. **Barra de Filtros Dinâmicos**:
   - Seletor de **Unidade** (carregado via API de unidades e restrito ao perfil do usuário).
   - Seletor de **Categoria / Cargo** (carregado de `/api/cargos`).
   - Campo de **Busca Textual** (filtro por Nome ou SIAPE).
   - Botão **Limpar Filtros**.
4. **Matriz / Tabela da Grade**:
   - Renderização dos dias do mês (1 até o último dia: 28, 29, 30 ou 31).
   - Coluna de colaborador fixada (*sticky left*).
   - Células com badges coloridos para cada tipo de escala/legenda:
     - Manhã (`M`): Azul suave (`bg-blue-100 text-blue-800`)
     - Tarde (`T`): Âmbar suave (`bg-amber-100 text-amber-800`)
     - Noite (`N`): Roxo suave (`bg-purple-100 text-purple-800`)
     - Plantão Diurno (`D`): Verde suave (`bg-emerald-100 text-emerald-800`)
     - Férias (`FE`): Vermelho suave (`bg-rose-100 text-rose-800`)
     - Folga (`F`): Cinza suave (`bg-gray-100 text-gray-700`)
   - Destaque em cinza claro para fins de semana (Sábado/Domingo) e feriados.
5. **Modal "Criar Nova Grade"**:
   - Seleção do colaborador, mês/ano e unidade.
   - Assistente para preencher automaticamente com base na escala contratual ou preenchimento dia a dia.
6. **Modal "Copiar Grade"**:
   - Seleção do Colaborador de Origem (e mês/ano de referência).
   - Seleção de um ou múltiplos Colaboradores de Destino.
   - Visualização prévia e botão de confirmação.

---

## 4. Segurança e Controle de Acesso
- O endpoint `/api/grades` verifica o token JWT recebido no header `Authorization`.
- Caso o usuário não possua privilégios administrativos globais (`GLO-SEC-HCPE-SETISD`), as unidades listadas e consultadas são filtradas para aquelas permitidas.
- Todas as operações de criação, alteração e cópia de grade gravam os dados de auditoria padrão (`login` do usuário autenticado e `data_alteracao` do servidor).
