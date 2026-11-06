"""
Script de cadastramento/atualização de lotação dos 20 funcionários
no Posto de Serviço Hemodiálise dentro da Unidade de Sistema Urinário
com início da lotação em 01/01/2025.
"""

FUNCIONARIOS_HEMODIALISE = [
    {"nome": "ALEXANDRE PEREIRA DOS SANTOS", "matricula": "3048008"},
    {"nome": "SIMONE MARQUES DA SILVA", "matricula": "2164828"},
    {"nome": "GORETE LOURDES RAIMUNDO", "matricula": "2173683"},
    {"nome": "ANA CLAUDIA A. CLEMENTE", "matricula": "2232181"},
    {"nome": "ANA MARIA DA CONCEIÇÃO", "matricula": "2241712"},
    {"nome": "AMANDA VIEIRA DA SILVA", "matricula": "3433437"},
    {"nome": "JOEL INACIO DO NASCIMENTO", "matricula": "2232211"},
    {"nome": "MARIA DE FÁTIMA C. DA SILVA", "matricula": "2173775"},
    {"nome": "VERA LÚCIA QUEIROZ DE SOUZA", "matricula": "2244744"},
    {"nome": "DANIELE CONCEIÇÃO V. BERNARDO", "matricula": "3319587"},
    {"nome": "EVA MARIA DE SOUZA", "matricula": "3507182"},
    {"nome": "ALDSON ALVES MARCELINO", "matricula": "3467618"},
    {"nome": "CLÁUDIA XAVIER A. DA SILVA", "matricula": "1864400"},
    {"nome": "ROSÂNGELA LEITE DA S. COSTA", "matricula": "3312362"},
    {"nome": "ANTÔNIO OTÁVIO DE SENA BARROS", "matricula": "3422267"},
    {"nome": "CRISTIANE DE CARVALHO REGO BARROS", "matricula": "3507458"},
    {"nome": "ANDRÉA CARLA PEREIRA DA SILVA", "matricula": "3139447"},
    {"nome": "FERNANDA OLIVEIRA DA SILVA", "matricula": "1507288"},
    {"nome": "VALDJANE NOGUEIRA N. NOBRE", "matricula": "2232733"},
    {"nome": "JOSEANE MARIA DA SILVA", "matricula": "3250019"},
]

def cadastrar_lotacoes_hemodialise_sync(cursor):
    # 1. Localizar ou criar a UORG Unidade de Sistema Urinário
    cursor.execute("SELECT id, nome FROM uorgs WHERE UPPER(nome) LIKE '%SISTEMA URIN%'")
    uorg_row = cursor.fetchone()
    if not uorg_row:
        cursor.execute("INSERT INTO uorgs (nome, sigla, login, data_alteracao) VALUES ('UNIDADE DE SISTEMA URINÁRIO', 'USU', 'sistema', datetime('now'))")
        uorg_id = cursor.lastrowid
        uorg_nome = 'UNIDADE DE SISTEMA URINÁRIO'
    else:
        uorg_id = uorg_row[0]
        uorg_nome = uorg_row[1]

    # 2. Localizar ou criar o Posto de Serviço Hemodiálise vinculado à UORG
    cursor.execute("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%'")
    posto_row = cursor.fetchone()
    if not posto_row:
        cursor.execute("INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('HEMODIÁLISE', ?, ?, 'sistema', datetime('now'))", (uorg_id, uorg_id))
        posto_id = cursor.lastrowid
        posto_nome = 'HEMODIÁLISE'
    else:
        posto_id = posto_row[0]
        posto_nome = posto_row[1]
        cursor.execute("UPDATE postos SET uorg_id = ?, unidade_id = ?, data_alteracao = datetime('now') WHERE id = ?", (uorg_id, uorg_id, posto_id))

    # 3. Obter cargo padrão (Técnico de Enfermagem ou primeiro existente)
    cursor.execute("SELECT id FROM cargos WHERE UPPER(nome) LIKE '%TEC%ENF%' LIMIT 1")
    c_row = cursor.fetchone()
    cargo_id_default = c_row[0] if c_row else 1

    # Obter vínculo padrão (EBSERH ou primeiro existente)
    cursor.execute("SELECT id FROM vinculos WHERE UPPER(nome) LIKE '%EBSERH%' LIMIT 1")
    v_row = cursor.fetchone()
    vinculo_id_default = v_row[0] if v_row else 1

    # Obter escala padrão
    cursor.execute("SELECT id FROM escalas LIMIT 1")
    e_row = cursor.fetchone()
    escala_id_default = e_row[0] if e_row else 1

    detalhes = []

    for item in FUNCIONARIOS_HEMODIALISE:
        mat = item["matricula"].strip()
        nome = item["nome"].strip()

        # Buscar funcionário por matrícula ou nome
        cursor.execute("SELECT id, nome FROM funcionarios WHERE matricula = ?", (mat,))
        func_row = cursor.fetchone()
        if not func_row:
            cursor.execute("SELECT id, matricula FROM funcionarios WHERE UPPER(TRIM(nome)) = ?", (nome.upper(),))
            func_row = cursor.fetchone()

        if not func_row:
            cursor.execute("""
                INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                VALUES (?, ?, ?, ?, ?, 'sistema', datetime('now'))
            """, (mat, nome, cargo_id_default, escala_id_default, vinculo_id_default))
            func_id = cursor.lastrowid
            status_func = "criado"
        else:
            func_id = func_row[0]
            cursor.execute("UPDATE funcionarios SET matricula = ?, nome = ?, data_alteracao = datetime('now') WHERE id = ?", (mat, nome, func_id))
            status_func = "encontrado"

        # Fechar qualquer lotação aberta anterior que esteja em outra UORG/posto com data anterior a 2025-01-01
        cursor.execute("""
            UPDATE funcionarios_lotacoes 
            SET data_fim = '2024-12-31', data_alteracao = datetime('now')
            WHERE funcionario_id = ? 
              AND (uorg_id != ? OR posto_id != ?) 
              AND (data_fim IS NULL OR data_fim = '')
        """, (func_id, uorg_id, posto_id))

        # Verificar se já existe a lotação no Posto Hemodiálise
        cursor.execute("""
            SELECT id, data_inicio, data_fim FROM funcionarios_lotacoes
            WHERE funcionario_id = ? AND uorg_id = ? AND posto_id = ?
        """, (func_id, uorg_id, posto_id))
        lot_row = cursor.fetchone()

        if not lot_row:
            cursor.execute("""
                INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                VALUES (?, ?, ?, ?, '2025-01-01', NULL, 'sistema', datetime('now'))
            """, (func_id, uorg_id, uorg_id, posto_id))
            lotacao_status = "lotacao_inserida"
        else:
            lot_id = lot_row[0]
            cursor.execute("""
                UPDATE funcionarios_lotacoes 
                SET data_inicio = '2025-01-01', data_fim = NULL, data_alteracao = datetime('now')
                WHERE id = ?
            """, (lot_id,))
            lotacao_status = "lotacao_atualizada"

        detalhes.append({
            "matricula": mat,
            "nome": nome,
            "funcionario_id": func_id,
            "status_func": status_func,
            "lotacao_status": lotacao_status,
            "uorg_id": uorg_id,
            "posto_id": posto_id,
            "data_inicio": "2025-01-01"
        })

    return {
        "uorg_id": uorg_id,
        "uorg_nome": uorg_nome,
        "posto_id": posto_id,
        "posto_nome": posto_nome,
        "total": len(detalhes),
        "detalhes": detalhes
    }
