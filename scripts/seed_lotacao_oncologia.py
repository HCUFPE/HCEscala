"""
Script de seed para lotar os funcionários no serviço de Oncologia da Unidade de Ambulatório.
Regras:
- Fechar a lotação anterior definindo data_fim = '2024-12-31'
- Criar a nova lotação com data_inicio = '2025-01-01' e data_fim = NULL
- Vincular à UORG Oncologia e ao Posto de Oncologia
"""

import sys
import os

FUNCIONARIOS_RAW = [
    # (Nome, Matricula, Registro, Cargo)
    ("BRUNA GABRIELLE DE S. COSTA", "1015514", "355552", "ENFERMEIRO-AREA"),
    ("EMANUELLE PINHEIRO DE MENEZES", "2173646", "165882", "ENFERMEIRO-AREA"),
    ("JADSON MENDOÇA GALINDO", "3037540", "238743", "ENFERMEIRO-AREA"),
    ("LARISSA LAÍS MARIA DA SILVA", "1926809", "254851", "ENFERMEIRO-AREA"),
    ("POLIANA SILVA DE BRITO", "2173845", "238749", "ENFERMEIRO-AREA"),
    ("POLLYANNA DUTRA SOBRAL", "1791588", "255313", "ENFERMEIRO-AREA"),
    ("RAFAELLA ARAUJO CORREIA", "1791618", "259815", "ENFERMEIRO-AREA"),
    ("PRISCILA DE OLIVEIRA CARVALHO", "2058498", "324757", "ENFERMEIRO-AREA"),
    ("JOSÉ ROBERTO ROCHA DA SILVA", "1424932", "103675", "ENFERMEIRO-AREA"),
    ("DANIELLY ACIOLI GALVÃO DE SOUZA", "2204775", "193608", "ENFERMEIRO-AREA"),
    ("LUANA PINHEIRO DE SOUSA", "2204432", "261736", "ENF NAVEGAÇÃO"),
    ("EDSON LAERSON BARBOSA ACIOLI", "1424221", "95674", "ENFERMEIRO -RHC"),
    ("NEIDEJANE TRAJANO DO NASCIMENTO", "1881820", "654413", "TEC ENFERMAGEM"),
    ("JOSEFA MARIA OLIVEIRA XAVIER", "2361722", "653383", "TEC ENFERMAGEM"),
    ("WEDJA DA SILVA LIMA", "2168117", "897071", "TEC ENFERMAGEM"),
    ("ROSILENE VILA NOVA", "1516113", "432374", "AUX ENFERMAGEM"),
    ("AURINEA SANTOS DA ROCHA", "1133918", "2945224", "AUX ENFERMAGEM"),
    ("JALDECIR FERREIRA DE MENDONÇA", "1440361", "486886", "AUX ENFERMAGEM"),
    ("VIVIANE MARIA DA SILVA", "3333403", "728472", "TEC ENFERMAGEM"),
    ("BRUNO JOSÉ BEZERRA", "2259734", "958611", "TEC ENFERMAGEM"),
    ("MARIA DE FÁTIMA DA FONSECA VERAS", "1134403", "95756", "AUX ENFERMAGEM"),
    ("FADIA MARIA COLIGNY E SILVA", "188585", "124523", "AUX ENFERMAGEM"),
    ("UILMA MENEZES DA SILVA", "1832777", "118831", "AUX ENFERMAGEM"),
]

def seed_lotacao_oncologia_sync(cursor):
    logs = []
    
    # 1. Localizar ou criar UORG Oncologia (subordinada ao Ambulatório)
    cursor.execute("SELECT id FROM uorgs WHERE UPPER(nome) = 'UNIDADE DE AMBULATÓRIO' OR UPPER(sigla) = 'AMB'")
    amb_row = cursor.fetchone()
    amb_id = amb_row[0] if amb_row else None

    cursor.execute("SELECT id FROM uorgs WHERE UPPER(nome) = 'ONCOLOGIA'")
    onc_uorg_row = cursor.fetchone()
    if not onc_uorg_row:
        cursor.execute("""
            INSERT INTO uorgs (nome, uorg_pai_id, login, data_alteracao)
            VALUES ('ONCOLOGIA', ?, 'sistema', datetime('now'))
        """, (amb_id,))
        onc_uorg_id = cursor.lastrowid
        logs.append(f"UORG ONCOLOGIA criada com id {onc_uorg_id}")
    else:
        onc_uorg_id = onc_uorg_row[0]
        logs.append(f"UORG ONCOLOGIA localizada com id {onc_uorg_id}")

    # 2. Localizar ou criar Posto de Oncologia
    cursor.execute("SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA'")
    onc_posto_row = cursor.fetchone()
    if not onc_posto_row:
        cursor.execute("""
            INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao)
            VALUES ('ONCOLOGIA', ?, ?, 'sistema', datetime('now'))
        """, (onc_uorg_id, onc_uorg_id))
        onc_posto_id = cursor.lastrowid
        logs.append(f"Posto ONCOLOGIA criado com id {onc_posto_id}")
    else:
        onc_posto_id = onc_posto_row[0]
        logs.append(f"Posto ONCOLOGIA localizado com id {onc_posto_id}")

    # 3. Cache de Cargos e Escalas
    cursor.execute("SELECT id, UPPER(nome) FROM cargos")
    cargos_dict = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT id, UPPER(sigla) FROM escalas")
    escalas_dict = {row[1]: row[0] for row in cursor.fetchall()}
    default_escala_id = list(escalas_dict.values())[0] if escalas_dict else 1

    cursor.execute("SELECT id, UPPER(nome) FROM vinculos")
    vinculos_dict = {row[1]: row[0] for row in cursor.fetchall()}
    default_vinculo_id = list(vinculos_dict.values())[0] if vinculos_dict else 1

    detalhes_processados = []

    for nome, matricula, registro, cargo_nome in FUNCIONARIOS_RAW:
        nome_clean = nome.strip()
        matr_clean = matricula.strip()
        cargo_clean = cargo_nome.strip().upper()

        # Garantir Cargo
        cargo_id = cargos_dict.get(cargo_clean)
        if not cargo_id:
            # Tentar achar por substring
            for c_nome, c_id in cargos_dict.items():
                if cargo_clean in c_nome or c_nome in cargo_clean:
                    cargo_id = c_id
                    break
        if not cargo_id:
            # Determinar carga horária padrão
            ch = 36 if ("TEC" in cargo_clean or "AUX" in cargo_clean or "ENF" in cargo_clean) else 40
            cursor.execute("""
                INSERT INTO cargos (nome, carga_horaria, login, data_alteracao)
                VALUES (?, ?, 'sistema', datetime('now'))
            """, (cargo_clean, ch))
            cargo_id = cursor.lastrowid
            cargos_dict[cargo_clean] = cargo_id
            logs.append(f"Cargo '{cargo_clean}' criado com id {cargo_id}")

        # Localizar Funcionário por matrícula ou nome
        cursor.execute("SELECT id, nome, cargo_id FROM funcionarios WHERE matricula = ?", (matr_clean,))
        func_row = cursor.fetchone()
        
        if not func_row:
            cursor.execute("SELECT id, nome, cargo_id FROM funcionarios WHERE UPPER(TRIM(nome)) = ?", (nome_clean.upper(),))
            func_row = cursor.fetchone()

        if not func_row:
            # Cadastrar funcionário
            cursor.execute("""
                INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                VALUES (?, ?, ?, ?, ?, 'sistema', datetime('now'))
            """, (matr_clean, nome_clean, cargo_id, default_escala_id, default_vinculo_id))
            func_id = cursor.lastrowid
            status_func = "Cadastrado novo"
        else:
            func_id = func_row[0]
            # Atualiza cargo e matrícula se necessário
            cursor.execute("""
                UPDATE funcionarios
                SET matricula = ?, nome = ?, cargo_id = ?, data_alteracao = datetime('now')
                WHERE id = ?
            """, (matr_clean, nome_clean, cargo_id, func_id))
            status_func = "Atualizado existente"

        # 4. Fechar lotações ativas anteriores (definir data_fim = '2024-12-31')
        cursor.execute("""
            UPDATE funcionarios_lotacoes
            SET data_fim = '2024-12-31', data_alteracao = datetime('now')
            WHERE funcionario_id = ? 
              AND (data_fim IS NULL OR data_fim = '' OR TRIM(data_fim) = '' OR data_fim > '2024-12-31')
              AND (uorg_id != ? OR uorg_id IS NULL)
        """, (func_id, onc_uorg_id))
        fechadas = cursor.rowcount

        # 5. Verificar se já possui lotação ativa na Oncologia com data_inicio = '2025-01-01'
        cursor.execute("""
            SELECT id, data_inicio, data_fim 
            FROM funcionarios_lotacoes 
            WHERE funcionario_id = ? AND uorg_id = ? AND (data_fim IS NULL OR data_fim = '' OR TRIM(data_fim) = '')
        """, (func_id, onc_uorg_id))
        lot_ativa_onc = cursor.fetchone()

        if not lot_ativa_onc:
            cursor.execute("""
                INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                VALUES (?, ?, ?, '2025-01-01', NULL, 'sistema', datetime('now'))
            """, (func_id, onc_uorg_id, onc_posto_id))
            lot_id = cursor.lastrowid
            status_lotacao = f"Nova lotação criada (ID {lot_id}) a partir de 2025-01-01"
        else:
            lot_id = lot_ativa_onc[0]
            cursor.execute("""
                UPDATE funcionarios_lotacoes
                SET data_inicio = '2025-01-01', posto_id = ?, data_alteracao = datetime('now')
                WHERE id = ?
            """, (onc_posto_id, lot_id))
            status_lotacao = f"Lotação existente (ID {lot_id}) ajustada para 2025-01-01 em aberto"

        detalhes_processados.append({
            "id": func_id,
            "matricula": matr_clean,
            "nome": nome_clean,
            "cargo": cargo_clean,
            "status_func": status_func,
            "lotacoes_anteriores_fechadas": fechadas,
            "status_lotacao": status_lotacao
        })

    return {
        "logs": logs,
        "uorg_oncologia_id": onc_uorg_id,
        "posto_oncologia_id": onc_posto_id,
        "total_processados": len(detalhes_processados),
        "funcionarios": detalhes_processados
    }
