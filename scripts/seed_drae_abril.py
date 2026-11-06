# -*- coding: utf-8 -*-
"""
Carga automática da UORG DRAE e importação das escalas dos colaboradores para Abril de 2026.
"""

TABELA_DRAE = [
    {
        "nome": "ALEXANDRE PEREIRA DOS SANTOS",
        "matricula": "3048008",
        "conselho": "3048008 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 40,
        "dias": {
            10: "D6", 14: "D6", 16: "D6", 18: "D6", 19: "D6",
            22: "D6", 24: "D6", 27: "D6", 29: "D6", 30: "D6"
        }
    },
    {
        "nome": "SIMONE MARQUES DA SILVA",
        "matricula": "2164828",
        "conselho": "432676 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            10: "D6", 12: "D6", 14: "FE12D", 16: "FE12D", 18: "FE12D",
            21: "FE12D", 23: "FE12D", 25: "FE12D", 27: "FE12D", 28: "FE12D", 30: "FE12D"
        }
    },
    {
        "nome": "GORETE LOURDES RAIMUNDO",
        "matricula": "2173683",
        "conselho": "304855 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            10: "D6", 12: "D6", 14: "D6", 16: "D6", 18: "D6",
            21: "D6", 23: "D6", 25: "D6", 28: "D6", 30: "D6"
        }
    },
    {
        "nome": "ANA CLAUDIA A. CLEMENTE",
        "matricula": "2232181",
        "conselho": "202071 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            10: "D6", 13: "D6", 15: "D6", 17: "D6", 19: "D6",
            21: "D6", 23: "D6", 26: "D6", 28: "D6"
        }
    },
    {
        "nome": "ANA MARIA DA CONCEIÇÃO",
        "matricula": "2241712",
        "conselho": "339727 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            12: "D6", 14: "D6", 17: "D6", 19: "D6", 21: "D6",
            23: "D6", 25: "D6", 27: "D6", 28: "D6", 30: "D6"
        }
    },
    {
        "nome": "AMANDA VIEIRA DA SILVA",
        "matricula": "3433437",
        "conselho": "994769 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "D6", 13: "D6", 15: "D6", 17: "D6", 20: "D6",
            22: "D6", 23: "D6", 25: "D6", 27: "D6", 29: "D6"
        }
    },
    {
        "nome": "JOEL INACIO DO NASCIMENTO",
        "matricula": "2232211",
        "conselho": "360238 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            11: "D6", 14: "D6", 16: "D6", 18: "D6", 20: "D6",
            22: "D6", 24: "D6", 27: "D6", 29: "D6"
        }
    },
    {
        "nome": "MARIA DE FÁTIMA C. DA SILVA",
        "matricula": "2173775",
        "conselho": "567272 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "D6", 10: "D6", 13: "D6", 15: "D6", 17: "D6",
            20: "D6", 22: "D6", 23: "D6", 25: "D6", 27: "D6", 30: "D6"
        }
    },
    {
        "nome": "VERA LÚCIA QUEIROZ DE SOUZA",
        "matricula": "2244744",
        "conselho": "491560 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 40,
        "dias": {
            8: "D6", 10: "D6", 12: "D6", 14: "D6", 16: "D6",
            19: "D6", 21: "D6", 23: "D6", 26: "D6", 28: "D6", 30: "D6"
        }
    },
    {
        "nome": "DANIELE CONCEIÇÃO V. BERNARDO",
        "matricula": "3319587",
        "conselho": "418136 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "D6", 10: "D6", 12: "D6", 14: "D6", 16: "D6",
            18: "D6", 20: "D6", 22: "D6", 24: "D6", 27: "D6", 29: "D6"
        }
    },
    {
        "nome": "CLÁUDIA XAVIER A. DA SILVA",
        "matricula": "1864400",
        "conselho": "299672 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "RJU",
        "ch": 30,
        "dias": {
            8: "D6", 11: "D6", 14: "D6", 16: "D6", 19: "D6",
            21: "FE12D", 24: "FE12D", 27: "FE12D", 29: "FE12D"
        }
    },
    {
        "nome": "EVA MARIA DE SOUZA",
        "matricula": "3507182",
        "conselho": "302303 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            11: "D6", 14: "D6", 16: "D6", 18: "D6", 20: "D6",
            22: "D6", 23: "D6", 26: "D6", 28: "D6", 29: "D6"
        }
    },
    {
        "nome": "CRISTIANE DE CARVALHO REGO BARROS",
        "matricula": "3507458",
        "conselho": "1989978 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            10: "D6", 13: "D6", 15: "D6", 17: "D6", 19: "D6",
            21: "D6", 23: "D6", 25: "D6", 27: "D6", 29: "D6", 30: "D6"
        }
    },
    {
        "nome": "ROSÂNGELA LEITE DA S. COSTA",
        "matricula": "3312362",
        "conselho": "1526777 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "D6", 10: "D6", 11: "D6", 14: "D6", 16: "D6",
            17: "D6", 20: "D6", 22: "D6", 24: "D6", 26: "D6", 28: "D6", 30: "D6"
        }
    },
    {
        "nome": "ANDRÉA CARLA PEREIRA DA SILVA",
        "matricula": "3139447",
        "conselho": "648039 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "D6", 9: "D6", 13: "D6", 16: "D6", 18: "D6",
            20: "D6", 23: "D6", 24: "D6", 27: "D6", 28: "D6"
        }
    },
    {
        "nome": "VALDJANE NOGUEIRA N. NOBRE",
        "matricula": "2232733",
        "conselho": "641179 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "M15", 9: "M15", 11: "D6", 13: "M15", 14: "M15",
            15: "M15", 16: "M15", 17: "M15", 19: "M15", 20: "M15",
            21: "M15", 22: "M15", 23: "M15", 25: "M15", 26: "D6",
            27: "M15", 28: "M15", 29: "M15", 30: "M15"
        }
    },
    {
        "nome": "JOSEANE MARIA DA SILVA",
        "matricula": "3250019",
        "conselho": "648279 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            8: "AFIN6", 9: "AFIN7", 10: "AFIN8", 11: "AFIN6", 13: "AFIN6",
            14: "AFIN6", 15: "AFIN6", 16: "AFIN6", 17: "AFIN6", 18: "AFIN6",
            20: "AFIN6", 21: "AFIN6", 22: "AFIN6", 23: "AFIN6", 24: "AFIN6",
            25: "AFIN6", 27: "AFIN6", 28: "AFIN6", 29: "AFIN6", 30: "AFIN6"
        }
    },
    {
        "nome": "NATAN DUARTE SANTANA",
        "matricula": "3316150",
        "conselho": "1468055 TE",
        "cargo": "TEC. ENFERMAGEM",
        "vinculo": "EBSERH",
        "ch": 36,
        "dias": {
            13: "D6", 15: "D6", 17: "D6", 19: "D6", 21: "D6",
            23: "D6", 24: "D6", 27: "D6", 29: "D6", 30: "D6"
        }
    }
]

def seed_drae_abril_sync(cursor):
    print("Iniciando seed_drae_abril_sync...")

    # 1. Localizar ou Criar a UORG DRAE
    cursor.execute("""
        SELECT id, nome, sigla FROM uorgs 
        WHERE UPPER(sigla) = 'DRAE' 
           OR UPPER(nome) LIKE '%DRAE%' 
           OR UPPER(nome) LIKE '%DIVISAO DE GESTAO DO CUIDADO%'
           OR UPPER(nome) LIKE '%DIVISAO DE REABILITACAO%'
           OR UPPER(nome) LIKE '%REABILITACAO%'
    """)
    row_drae = cursor.fetchone()
    
    if row_drae:
        drae_id = row_drae[0]
        drae_nome = row_drae[1]
        print(f"UORG DRAE encontrada: ID {drae_id} ({drae_nome})")
    else:
        cursor.execute("""
            INSERT INTO uorgs (nome, sigla, login, data_alteracao)
            VALUES ('DIVISÃO DE REABILITAÇÃO E ATENÇÃO ESPECIALIZADA - DRAE', 'DRAE', 'sistema', datetime('now'))
        """)
        drae_id = cursor.lastrowid
        drae_nome = 'DIVISÃO DE REABILITAÇÃO E ATENÇÃO ESPECIALIZADA - DRAE'
        print(f"UORG DRAE criada com sucesso: ID {drae_id}")

    # 2. Garantir Posto Geral para a DRAE
    cursor.execute("SELECT id FROM postos WHERE uorg_id = ? OR unidade_id = ?", (drae_id, drae_id))
    row_posto = cursor.fetchone()
    if row_posto:
        posto_drae_id = row_posto[0]
    else:
        cursor.execute("""
            INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao)
            VALUES ('GERAL - DRAE', ?, ?, 'sistema', datetime('now'))
        """, (drae_id, drae_id))
        posto_drae_id = cursor.lastrowid

    # 3. Garantir Vínculos (EBSERH, RJU)
    cursor.execute("SELECT id, nome FROM vinculos")
    vinculos_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
    for v_nome in ["EBSERH", "RJU"]:
        if v_nome not in vinculos_map:
            cursor.execute("INSERT INTO vinculos (nome, login, data_alteracao) VALUES (?, 'sistema', datetime('now'))", (v_nome,))
            vinculos_map[v_nome] = cursor.lastrowid

    # 4. Garantir Cargos (TÉCNICO EM ENFERMAGEM)
    cursor.execute("SELECT id, nome FROM cargos")
    cargos_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
    
    # Procurar cargo adequado
    cargo_padrao_id = None
    for c_nome, c_id in cargos_map.items():
        if "TECNICO EM ENFERMAGEM" in c_nome or "TEC. ENFERMAGEM" in c_nome or "TECNICO DE ENFERMAGEM" in c_nome:
            cargo_padrao_id = c_id
            break

    if not cargo_padrao_id:
        cursor.execute("""
            INSERT INTO cargos (nome, carga_horaria, login, data_alteracao)
            VALUES ('TECNICO EM ENFERMAGEM', 36, 'sistema', datetime('now'))
        """)
        cargo_padrao_id = cursor.lastrowid
        cargos_map["TECNICO EM ENFERMAGEM"] = cargo_padrao_id

    # 5. Garantir Escala Padrão (ex: 12x36 / D6)
    cursor.execute("SELECT id, sigla FROM escalas")
    escalas_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
    escala_padrao_id = escalas_map.get("D6") or (list(escalas_map.values())[0] if escalas_map else None)

    # 6. Para cada colaborador da tabela:
    #    a) Localizar por matrícula ou nome; se não existir, cadastrar
    #    b) Garantir Lotação ativa na DRAE a partir de 2025-01-01
    #    c) Inserir ou atualizar Grade para Abril/2026 (mes=4, ano=2026)
    mes_alvo = 4
    ano_alvo = 2026

    for item in TABELA_DRAE:
        matricula = item["matricula"].strip()
        nome = item["nome"].strip()
        vinculo_nome = item["vinculo"].strip().upper()
        vinculo_id = vinculos_map.get(vinculo_nome, vinculos_map.get("EBSERH"))
        ch = item["ch"]

        # Busca funcionário por matrícula
        cursor.execute("SELECT id, nome, cargo_id FROM funcionarios WHERE matricula = ?", (matricula,))
        func_row = cursor.fetchone()

        if func_row:
            func_id = func_row[0]
            # Atualiza nome se necessário
            cursor.execute("UPDATE funcionarios SET nome = ? WHERE id = ?", (nome, func_id))
        else:
            # Buscar por nome aproximado
            cursor.execute("SELECT id, matricula, cargo_id FROM funcionarios WHERE UPPER(nome) = ?", (nome.upper(),))
            func_by_nome = cursor.fetchone()
            if func_by_nome:
                func_id = func_by_nome[0]
                cursor.execute("UPDATE funcionarios SET matricula = ? WHERE id = ?", (matricula, func_id))
            else:
                cursor.execute("""
                    INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                    VALUES (?, ?, ?, ?, ?, 'sistema', datetime('now'))
                """, (matricula, nome, cargo_padrao_id, escala_padrao_id, vinculo_id))
                func_id = cursor.lastrowid
                print(f"Funcionário cadastrado: {nome} ({matricula}) - ID {func_id}")

        # Garantir Lotação ativa na DRAE
        cursor.execute("""
            SELECT id FROM funcionarios_lotacoes 
            WHERE funcionario_id = ? AND (uorg_id = ? OR unidade_id = ?)
        """, (func_id, drae_id, drae_id))
        lot_row = cursor.fetchone()
        if not lot_row:
            cursor.execute("""
                INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                VALUES (?, ?, ?, ?, '2025-01-01', NULL, 'sistema', datetime('now'))
            """, (func_id, drae_id, drae_id, posto_drae_id))
            print(f"Lotação na DRAE criada para {nome}")

        # Localizar ou Criar Grade do mês 4/2026
        cursor.execute("""
            SELECT id, status FROM grades 
            WHERE funcionario_id = ? AND uorg_id = ? AND mes = ? AND ano = ?
        """, (func_id, drae_id, mes_alvo, ano_alvo))
        grade_row = cursor.fetchone()

        if grade_row:
            grade_id = grade_row[0]
            # Limpar dias anteriores
            cursor.execute("DELETE FROM grade_dias WHERE grade_id = ?", (grade_id,))
        else:
            cursor.execute("""
                INSERT INTO grades (funcionario_id, uorg_id, posto_id, mes, ano, status, observacao, login, data_alteracao)
                VALUES (?, ?, ?, ?, ?, 'Rascunho', 'Escala importada da DRAE', 'sistema', datetime('now'))
            """, (func_id, drae_id, posto_drae_id, mes_alvo, ano_alvo))
            grade_id = cursor.lastrowid

        # Inserir os dias da escala
        dias_dict = item["dias"]
        for dia_num in range(1, 31):
            sigla = dias_dict.get(dia_num)
            if sigla:
                escala_id = escalas_map.get(sigla.upper())
                cursor.execute("""
                    INSERT INTO grade_dias (grade_id, dia, escala_id, legenda_sigla)
                    VALUES (?, ?, ?, ?)
                """, (grade_id, dia_num, escala_id, sigla))

    print(f"Carga da DRAE para Abril/{ano_alvo} concluída com sucesso para {len(TABELA_DRAE)} colaboradores!")
