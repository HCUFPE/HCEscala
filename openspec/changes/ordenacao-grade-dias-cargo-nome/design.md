# Technical Design: Ordenação Hierárquica da Grade por Dia / Dias Alocados ➔ Cargo ➔ Nome

## Overview
O frontend da aplicação (`Grade.vue`) renderiza uma matriz mensal reativa baseada na computed `sortedMatrixData`. Esta proposta padroniza a cadeia de comparadores de ordenação em JavaScript/TypeScript para garantir que qualquer clique de ordenação (em dias ou botões) preserve sempre um critério secundário e terciário estável: **Cargo** seguido de **Nome**.

## Architecture & Logic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       EVENTO DE CLIQUE                      │
│     (Cabeçalho do Dia 1..31 OU Botão Superior de Ordenação)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CRITÉRIO PRIMÁRIO SELECIONADO               │
│  - Dia Específico (tem plantão no dia? sigla do turno?)     │
│  - Dias Alocados (total de plantões do mês)                 │
│  - Código da Escala Cadastrada                              │
│  - Denominação do Cargo                                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Diferente? ────┴──── Iguais / Empate?
                     │                      │
                     ▼                      ▼
           Aplica Ordenação         CRITÉRIO SECUNDÁRIO:
           Ascendente/Descendente         CARGO
                                      (localeCompare)
                                            │
                             Diferente? ────┴──── Iguais?
                                  │                  │
                                  ▼                  ▼
                         Aplica Ordenação    CRITÉRIO TERCIÁRIO:
                             por Cargo              NOME
                                               (localeCompare)
```

## Detailed Implementation (`Grade.vue`)

### 1. Função de Comparação Base (`compareByCargoAndNome`)
```typescript
const compareByCargoAndNome = (a: ColaboradorGradeRow, b: ColaboradorGradeRow): number => {
  const cargoA = (a.cargo && a.cargo !== '-' ? a.cargo : 'Sem Cargo').trim();
  const cargoB = (b.cargo && b.cargo !== '-' ? b.cargo : 'Sem Cargo').trim();
  const cmpCargo = cargoA.localeCompare(cargoB, 'pt-BR');
  if (cmpCargo !== 0) return cmpCargo;
  return (a.nome || '').localeCompare(b.nome || '', 'pt-BR');
};
```

### 2. Ordenação por Dia (`dia_${dia}`)
```typescript
if (col.startsWith('dia_')) {
  const diaNum = parseInt(col.replace('dia_', ''), 10);
  const temPlantaoA = hasPlantaoNoDia(a, diaNum) ? 1 : 0;
  const temPlantaoB = hasPlantaoNoDia(b, diaNum) ? 1 : 0;
  
  // Quem tem plantão no dia vem primeiro (se dir for desc)
  if (temPlantaoA !== temPlantaoB) {
    return (temPlantaoA - temPlantaoB) * dir;
  }
  
  const sigA = getDiaSiglaOrStatus(a, diaNum);
  const sigB = getDiaSiglaOrStatus(b, diaNum);
  if (sigA !== sigB) {
    return sigA.localeCompare(sigB, 'pt-BR') * dir;
  }
  
  // Desempate determinístico
  return compareByCargoAndNome(a, b);
}
```

### 3. Ordenação por Dias Alocados (`dias_alocados`)
```typescript
if (col === 'dias_alocados') {
  const countA = countDiasAlocados(a);
  const countB = countDiasAlocados(b);
  if (countA !== countB) {
    return (countA - countB) * dir;
  }
  return compareByCargoAndNome(a, b);
}
```

## Testability & Non-Regression
- Testar a interação visual clicando em vários dias (ex: dia 1, dia 15) e verificar que médicos ou enfermeiros que trabalham no dia ficam agrupados por cargo e em ordem alfabética.
- Clicar em "Dias Alocados" e confirmar que colaboradores com 15 plantões ficam ordenados por cargo e nome entre si.
