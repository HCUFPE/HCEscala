import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from src.resources.database import DatabaseManager

async def main():
    db = DatabaseManager(os.getenv("SQLITE_DSN", "sqlite+aiosqlite:///./app.db"))
    async with db.get_session() as session:
        # Obter UORG e Posto
        res_uorg = await session.execute(text("SELECT id, nome FROM uorgs WHERE UPPER(nome) LIKE '%URINARIO%' OR UPPER(sigla) = 'USUR' LIMIT 1"))
        uorg_row = res_uorg.first()
        if not uorg_row:
            print("ERRO: UORG não encontrada!")
            return
        uorg_id = uorg_row[0]
        uorg_nome = uorg_row[1]

        res_posto = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
        posto_row = res_posto.first()
        if not posto_row:
            await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('HEMODIÁLISE', {uorg_id}, {uorg_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_posto2 = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
            posto_row = res_posto2.first()
        posto_id = posto_row[0]
        posto_nome = posto_row[1]

        # Garantir vínculo
        await session.execute(text(f"UPDATE postos SET uorg_id = {uorg_id}, unidade_id = {uorg_id} WHERE id = {posto_id}"))
        await session.commit()

        # Obter IDs padrão
        res_c = await session.execute(text("SELECT id FROM cargos WHERE UPPER(nome) LIKE '%TECNICO%ENFERMAGEM%' LIMIT 1"))
        cargo_tec_id = res_c.scalar() or 1

        res_e = await session.execute(text("SELECT id FROM escalas WHERE UPPER(sigla) = 'D6' or UPPER(descricao) LIKE '%D6%' LIMIT 1"))
        escala_def_id = res_e.scalar()
        if not escala_def_id:
            res_e2 = await session.execute(text("SELECT id FROM escalas LIMIT 1"))
            escala_def_id = res_e2.scalar() or 1

        res_v = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) LIKE '%EBSERH%' LIMIT 1"))
        vinculo_def_id = res_v.scalar() or 1

        funcionarios = [
            {"matricula": "3048008", "nome": "ALEXANDRE PEREIRA DOS SANTOS"},
            {"matricula": "2164828", "nome": "SIMONE MARQUES DA SILVA"},
            {"matricula": "2173683", "nome": "GORETE LOURDES RAIMUNDO"},
            {"matricula": "2232181", "nome": "ANA CLAUDIA A. CLEMENTE"},
            {"matricula": "2241712", "nome": "ANA MARIA DA CONCEIÇÃO"},
            {"matricula": "3433437", "nome": "AMANDA VIEIRA DA SILVA"},
            {"matricula": "2232211", "nome": "JOEL INACIO DO NASCIMENTO"},
            {"matricula": "2173775", "nome": "MARIA DE FÁTIMA C. DA SILVA"},
            {"matricula": "2244744", "nome": "VERA LÚCIA QUEIROZ DE SOUZA"},
            {"matricula": "3319587", "nome": "DANIELE CONCEIÇÃO V. BERNARDO"},
            {"matricula": "3507182", "nome": "EVA MARIA DE SOUZA"},
            {"matricula": "3467618", "nome": "ALDSON ALVES MARCELINO"},
            {"matricula": "1864400", "nome": "CLÁUDIA XAVIER A. DA SILVA"},
            {"matricula": "3312362", "nome": "ROSÂNGELA LEITE DA S. COSTA"},
            {"matricula": "3422267", "nome": "ANTÔNIO OTÁVIO DE SENA BARROS"},
            {"matricula": "3507458", "nome": "CRISTIANE DE CARVALHO REGO BARROS"},
            {"matricula": "3139447", "nome": "ANDRÉA CARLA PEREIRA DA SILVA"},
            {"matricula": "1507288", "nome": "FERNANDA OLIVEIRA DA SILVA"},
            {"matricula": "2232733", "nome": "VALDJANE NOGUEIRA N. NOBRE"},
            {"matricula": "3250019", "nome": "JOSEANE MARIA DA SILVA"},
        ]

        data_inicio_str = "2025-01-01"
        cadastrados = []

        for item in funcionarios:
            mat = item["matricula"].strip()
            nome = item["nome"].strip()

            res_f = await session.execute(
                text("SELECT id, nome FROM funcionarios WHERE matricula = :mat OR UPPER(nome) = :nome LIMIT 1"),
                {"mat": mat, "nome": nome.upper()}
            )
            f_row = res_f.first()
            if f_row:
                func_id = f_row[0]
                await session.execute(
                    text("UPDATE funcionarios SET matricula = :mat WHERE id = :fid"),
                    {"mat": mat, "fid": func_id}
                )
            else:
                await session.execute(
                    text("""
                        INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                        VALUES (:mat, :nome, :cid, :eid, :vid, 'sistema', CURRENT_TIMESTAMP)
                    """),
                    {"mat": mat, "nome": nome, "cid": cargo_tec_id, "eid": escala_def_id, "vid": vinculo_def_id}
                )
                await session.commit()
                res_f2 = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
                func_id = res_f2.scalar()

            # Lotação
            res_lot = await session.execute(
                text("SELECT id FROM funcionarios_lotacoes WHERE funcionario_id = :fid AND uorg_id = :uid AND posto_id = :pid"),
                {"fid": func_id, "uid": uorg_id, "pid": posto_id}
            )
            lot_id = res_lot.scalar()

            if lot_id:
                await session.execute(
                    text("""
                        UPDATE funcionarios_lotacoes
                        SET data_inicio = :dini, data_fim = NULL, login = 'sistema', data_alteracao = CURRENT_TIMESTAMP
                        WHERE id = :lid
                    """),
                    {"dini": data_inicio_str, "lid": lot_id}
                )
            else:
                await session.execute(
                    text("""
                        INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                        VALUES (:fid, :uid, :pid, :dini, NULL, 'sistema', CURRENT_TIMESTAMP)
                    """),
                    {"fid": func_id, "uid": uorg_id, "pid": posto_id, "dini": data_inicio_str}
                )
            cadastrados.append((mat, nome, func_id))

        await session.commit()

        print(f"SUCESSO: {len(cadastrados)} funcionários vinculados à UORG {uorg_nome} (ID {uorg_id}) e Posto {posto_nome} (ID {posto_id}) a partir de {data_inicio_str}!")
        for c in cadastrados:
            print(f" - Matrícula: {c[0]} | Nome: {c[1]} | ID: {c[2]}")

if __name__ == "__main__":
    asyncio.run(main())
