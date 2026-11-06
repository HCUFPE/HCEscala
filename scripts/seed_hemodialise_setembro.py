"""
Seed e carga das grades dos 20 colaboradores do Posto Hemodiálise
(Unidade de Sistema Urinário) para Setembro de 2026 (mes=9, ano=2026).
"""

RAW_DATA_SETEMBRO = """ALEXANDRE PEREIRA DOS SANTOS	3048008	3048008 TE	TE	CLT	40							FE12D		FE12D		FE6		D6		D6		D6		D6		D6		D6				D6		D6		D6	D6			D6	CH6	168
SIMONE MARQUES DA SILVA	2164828	432676 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
GORETE LOURDES RAIMUNDO  	2173683	304855 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
ANA CLAUDIA A. CLEMENTE	2232181	202071 TE	TE	CLT	36							D6		D6		CH6		D6		D6				D6		D6		D6				D6		D6		D6		D6		D6		150
ANA MARIA DA CONCEIÇÃO	2241712	339727 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				FE12D		FE12D				FE12D		FE12D		FE12D	FE12D			FE12D		156
AMANDA VIEIRA DA SILVA	3433437	994769 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
JOEL INACIO DO NASCIMENTO	2232211	360238 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6	156
MARIA DE FÁTIMA C. DA SILVA	2173775	567272 TE	TE	CLT	36								D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6		D6		D6			156
VERA LÚCIA QUEIROZ DE SOUZA	2244744	491560 TE	TE	CLT	40								D6		D6	D6			D6		FE12D		FE12D		FE12D		FE12D		FE12D				D6		D6		D6		D6		D6	168
DANIELE CONCEIÇÃO V. BERNARDO	3319587	418136 TE	TE	CLT	36								D6		D6		D6		D6				D6		D6		D6		D6				D6		D6		D6		D6		D6	156
EVA MARIA DE SOUZA	3507182	302303 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6	156
ALDSON  ALVES MARCELINO	3467618	1397808 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6	156
CLÁUDIA XAVIER A. DA SILVA	1864400	299672 TE	TE	RJU	30							D6			D6	D6		D6			D6				D6		D6			D6			D6			D6			D6			132
ROSÂNGELA LEITE DA S. COSTA	3312362	1526777 TE	TE	CLT	36							D6			D6			D6			D6		D6	D6			D6		D6	D6			D6			D6			D6		D6	156
ANTÔNIO OTÁVIO DE SENA BARROS 	3422267	2101001TE	TE	CLT	36							CH12D		D6					D6		D6		D6			D6			D6					D6	D6		D6	D6		D6	D6	156
CRISTIANE DE CARVALHO REGO BARROS 	3507458	1989978 TE 	TE	CLT	36									D6			D6			D6	D6		D6		D6	D6			D6			D6			D6			D6		D6	D6	156
ANDRÉA CARLA PEREIRA DA SILVA	3139447	648039 TE	TE	CLT	36								D6		D6				D6		D6	D6			D6		D6	D6		D6		D6		D6			D6			D6		156
FERNANDA OLIVEIRA DA SILVA	1507288	668309 TE	TE	CLT	37								D6		D6	D6			D6			D6			D6		D6	D6		D6		D6		D6			D6		D6			156
VALDJANE NOGUEIRA N. NOBRE	2232733	641179 TE	TE	CLT	36							M16	M16	M16	M16				M16	M16	M16	M16	D6		M16	M16	M16	M16	M16			M16	M16	M16	M16	M16	D6		M16	M16	M16	150
JOSEANE MARIA DA SILVA	3250019	648279 TE	TE	CLT	36							AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	156"""

def seed_hemodialise_setembro_sync(cursor):
    # 1. Localizar a UORG Unidade de Sistema Urinário
    cursor.execute("SELECT id, nome FROM uorgs WHERE UPPER(nome) LIKE '%SISTEMA URIN%'")
    uorg_row = cursor.fetchone()
    if not uorg_row:
        cursor.execute("INSERT INTO uorgs (nome, sigla, login, data_alteracao) VALUES ('UNIDADE DE SISTEMA URINÁRIO', 'USU', 'sistema', datetime('now'))")
        uorg_id = cursor.lastrowid
    else:
        uorg_id = uorg_row[0]

    # 2. Localizar o Posto de Serviço Hemodiálise
    cursor.execute("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%'")
    posto_row = cursor.fetchone()
    if not posto_row:
        cursor.execute("INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('HEMODIÁLISE', ?, ?, 'sistema', datetime('now'))", (uorg_id, uorg_id))
        posto_id = cursor.lastrowid
    else:
        posto_id = posto_row[0]

    # 3. Garantir escalas que aparecem na grade
    escalas_necessarias = [
        ("D6", "DIURNO 6 HORAS", "D6", "07:00", "13:00", 1),
        ("FE12D", "FÉRIAS 12H DIURNO", "FE12D", "07:00", "19:00", 0),
        ("FE6", "FÉRIAS 6H", "FE6", "07:00", "13:00", 0),
        ("CH6", "COMPENSAÇÃO DE HORAS 6H", "CH6", "07:00", "13:00", 0),
        ("CH12D", "COMPENSAÇÃO DE HORAS 12H DIURNO", "CH12D", "07:00", "19:00", 0),
        ("M16", "MANHÃ 16H / JORNADA M16", "M16", "07:00", "23:00", 1),
        ("AFIN6", "AFINIDADE 6H", "AFIN6", "07:00", "13:00", 1)
    ]

    for sigla, desc, cod, ini, fim, assist in escalas_necessarias:
        cursor.execute("SELECT id FROM escalas WHERE UPPER(sigla) = ?", (sigla.upper(),))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO escalas (sigla, descricao, codigo, inicio_jornada, fim_jornada, apenas_assistenciais, login, data_alteracao)
                VALUES (?, ?, ?, ?, ?, ?, 'sistema', datetime('now'))
            """, (sigla.upper(), desc, cod, ini, fim, assist))

    # Mapear escalas
    cursor.execute("SELECT UPPER(sigla), id FROM escalas")
    escalas_map = {r[0].strip(): r[1] for r in cursor.fetchall()}

    mes_alvo = 9
    ano_alvo = 2026
    total_grades = 0
    total_dias = 0
    detalhes = []

    for line in RAW_DATA_SETEMBRO.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        nome = parts[0].strip()
        mat = parts[1].strip()
        dias_cols = parts[6:36] # 30 dias de setembro

        # 4. Localizar funcionário
        cursor.execute("SELECT id, nome FROM funcionarios WHERE matricula = ?", (mat,))
        func_row = cursor.fetchone()
        if not func_row:
            cursor.execute("SELECT id, matricula FROM funcionarios WHERE UPPER(TRIM(nome)) = ?", (nome.upper(),))
            func_row = cursor.fetchone()

        if not func_row:
            continue
        func_id = func_row[0]

        # 5. Criar ou atualizar a Grade de Setembro de 2026
        cursor.execute("""
            SELECT id FROM grades 
            WHERE funcionario_id = ? AND uorg_id = ? AND mes = ? AND ano = ?
        """, (func_id, uorg_id, mes_alvo, ano_alvo))
        grade_row = cursor.fetchone()

        if grade_row:
            grade_id = grade_row[0]
            cursor.execute("""
                UPDATE grades 
                SET posto_id = ?, observacao = 'Escala Hemodiálise Setembro/2026', data_alteracao = datetime('now') 
                WHERE id = ?
            """, (posto_id, grade_id))
            cursor.execute("DELETE FROM grade_dias WHERE grade_id = ?", (grade_id,))
        else:
            cursor.execute("""
                INSERT INTO grades (funcionario_id, uorg_id, posto_id, mes, ano, status, observacao, login, data_alteracao)
                VALUES (?, ?, ?, ?, ?, 'Rascunho', 'Escala Hemodiálise Setembro/2026', 'sistema', datetime('now'))
            """, (func_id, uorg_id, posto_id, mes_alvo, ano_alvo))
            grade_id = cursor.lastrowid

        # 6. Inserir os dias da escala do colaborador
        dias_cadastrados = 0
        for idx, val in enumerate(dias_cols):
            dia_num = idx + 1
            sigla_clean = val.strip().upper()
            if sigla_clean:
                e_id = escalas_map.get(sigla_clean)
                cursor.execute("""
                    INSERT INTO grade_dias (grade_id, dia, escala_id, legenda_sigla)
                    VALUES (?, ?, ?, ?)
                """, (grade_id, dia_num, e_id, sigla_clean))
                dias_cadastrados += 1
                total_dias += 1

        total_grades += 1
        detalhes.append({
            "matricula": mat,
            "nome": nome,
            "grade_id": grade_id,
            "dias_cadastrados": dias_cadastrados
        })

    return {
        "status": "success",
        "mes": mes_alvo,
        "ano": ano_alvo,
        "uorg_id": uorg_id,
        "posto_id": posto_id,
        "total_grades": total_grades,
        "total_dias_escalados": total_dias,
        "detalhes": detalhes
    }
