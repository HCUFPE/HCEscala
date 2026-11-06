import sqlite3
import os

def migrate():
    db_path = "app.db"
    if not os.path.exists(db_path):
        print("app.db não encontrado!")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("Iniciando migração de Setores e Unidades para UORGs...")

    # 1. Criar tabela uorgs
    c.execute("""
    CREATE TABLE IF NOT EXISTS uorgs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo VARCHAR(50),
        sigla VARCHAR(50),
        nome VARCHAR(200) NOT NULL UNIQUE,
        uorg_pai_id INTEGER REFERENCES uorgs(id) ON DELETE SET NULL,
        login VARCHAR(100) NOT NULL,
        data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # 2. Migrar Setores -> UORGs raiz (uorg_pai_id = NULL)
    setor_to_uorg = {}
    try:
        c.execute("SELECT id, nome, login, data_alteracao FROM setores")
        setores = c.fetchall()
        for sid, nome, login, data_alt in setores:
            c.execute("SELECT id FROM uorgs WHERE nome = ?", (nome,))
            existing = c.fetchone()
            if existing:
                uorg_id = existing[0]
            else:
                c.execute(
                    "INSERT INTO uorgs (nome, uorg_pai_id, login, data_alteracao) VALUES (?, NULL, ?, ?)",
                    (nome, login or "sistema", data_alt)
                )
                uorg_id = c.lastrowid
            setor_to_uorg[sid] = uorg_id
        print(f"Migrados {len(setores)} setores para UORGs de nível raiz.")
    except Exception as e:
        print(f"Aviso ao ler setores: {e}")

    # 3. Migrar Unidades -> UORGs filhas (uorg_pai_id = setor_uorg_id)
    unidade_to_uorg = {}
    try:
        c.execute("SELECT id, nome, setor_id, login, data_alteracao FROM unidades")
        unidades = c.fetchall()
        for uid, nome, setor_id, login, data_alt in unidades:
            pai_id = setor_to_uorg.get(setor_id)
            c.execute("SELECT id FROM uorgs WHERE nome = ?", (nome,))
            existing = c.fetchone()
            if existing:
                uorg_id = existing[0]
                if pai_id:
                    c.execute("UPDATE uorgs SET uorg_pai_id = ? WHERE id = ? AND uorg_pai_id IS NULL", (pai_id, uorg_id))
            else:
                c.execute(
                    "INSERT INTO uorgs (nome, uorg_pai_id, login, data_alteracao) VALUES (?, ?, ?, ?)",
                    (nome, pai_id, login or "sistema", data_alt)
                )
                uorg_id = c.lastrowid
            unidade_to_uorg[uid] = uorg_id
        print(f"Migradas {len(unidades)} unidades para UORGs subordinadas.")
    except Exception as e:
        print(f"Aviso ao ler unidades: {e}")

    conn.commit()

    # 4. Atualizar funcionarios_lotacoes
    c.execute("PRAGMA table_info(funcionarios_lotacoes)")
    cols_lot = [col[1] for col in c.fetchall()]
    if "uorg_id" not in cols_lot:
        c.execute("ALTER TABLE funcionarios_lotacoes ADD COLUMN uorg_id INTEGER REFERENCES uorgs(id)")
        conn.commit()
        print("Coluna uorg_id adicionada em funcionarios_lotacoes.")

    if "unidade_id" in cols_lot:
        for uid, uorg_id in unidade_to_uorg.items():
            c.execute("UPDATE funcionarios_lotacoes SET uorg_id = ? WHERE unidade_id = ? AND (uorg_id IS NULL OR uorg_id = 0)", (uorg_id, uid))
        conn.commit()
        print("funcionarios_lotacoes mapeadas para uorg_id com sucesso.")

    # 5. Atualizar grades
    c.execute("PRAGMA table_info(grades)")
    cols_grd = [col[1] for col in c.fetchall()]
    if "uorg_id" not in cols_grd:
        c.execute("ALTER TABLE grades ADD COLUMN uorg_id INTEGER REFERENCES uorgs(id)")
        conn.commit()
        print("Coluna uorg_id adicionada em grades.")

    if "unidade_id" in cols_grd:
        for uid, uorg_id in unidade_to_uorg.items():
            c.execute("UPDATE grades SET uorg_id = ? WHERE unidade_id = ? AND (uorg_id IS NULL OR uorg_id = 0)", (uorg_id, uid))
        conn.commit()
        print("grades mapeadas para uorg_id com sucesso.")

    # 6. Atualizar usuario_gerencias
    c.execute("PRAGMA table_info(usuario_gerencias)")
    cols_ger = [col[1] for col in c.fetchall()]
    if "uorg_id" not in cols_ger:
        c.execute("ALTER TABLE usuario_gerencias ADD COLUMN uorg_id INTEGER REFERENCES uorgs(id)")
        conn.commit()
        print("Coluna uorg_id adicionada em usuario_gerencias.")

    # Mapear gerencias de setores e unidades
    if "setor_id" in cols_ger:
        for sid, uorg_id in setor_to_uorg.items():
            c.execute("UPDATE usuario_gerencias SET uorg_id = ?, nivel = 'UORG' WHERE setor_id = ? AND uorg_id IS NULL", (uorg_id, sid))
    if "unidade_id" in cols_ger:
        for uid, uorg_id in unidade_to_uorg.items():
            c.execute("UPDATE usuario_gerencias SET uorg_id = ?, nivel = 'UORG' WHERE unidade_id = ? AND uorg_id IS NULL", (uorg_id, uid))
    conn.commit()
    print("usuario_gerencias atualizadas para nível UORG.")

    # 7. Atualizar postos
    c.execute("PRAGMA table_info(postos)")
    cols_pos = [col[1] for col in c.fetchall()]
    if "uorg_id" not in cols_pos:
        c.execute("ALTER TABLE postos ADD COLUMN uorg_id INTEGER REFERENCES uorgs(id)")
        conn.commit()
        print("Coluna uorg_id adicionada em postos.")

    if "unidade_id" in cols_pos:
        for uid, uorg_id in unidade_to_uorg.items():
            c.execute("UPDATE postos SET uorg_id = ? WHERE unidade_id = ? AND (uorg_id IS NULL OR uorg_id = 0)", (uorg_id, uid))
        conn.commit()
        print("postos mapeados para uorg_id.")

    # Contagem final
    c.execute("SELECT COUNT(*) FROM uorgs")
    total_uorgs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM uorgs WHERE uorg_pai_id IS NOT NULL")
    uorgs_com_pai = c.fetchone()[0]
    print(f"\nMigração concluída com sucesso!")
    print(f"Total de UORGs cadastradas: {total_uorgs}")
    print(f"UORGs com UORG Pai vinculada: {uorgs_com_pai}")

    conn.close()

if __name__ == "__main__":
    migrate()
