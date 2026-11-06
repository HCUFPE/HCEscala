from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.uorg_controller import UorgController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/uorgs",
    tags=["Unidades Organizacionais (UORGs)"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class UorgSimpleResponse(BaseModel):
    id: int
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    model_config = ConfigDict(from_attributes=True)

class PostoSimpleResponse(BaseModel):
    id: int
    nome: str
    model_config = ConfigDict(from_attributes=True)

class UorgBase(BaseModel):
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    uorg_pai_id: Optional[int] = None

class UorgCreate(UorgBase):
    pass

class UorgUpdate(BaseModel):
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: Optional[str] = None
    uorg_pai_id: Optional[int] = None

class UorgResponse(UorgBase):
    id: int
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    uorg_pai: Optional[UorgSimpleResponse] = None
    subordinadas: List[UorgSimpleResponse] = []
    postos: List[PostoSimpleResponse] = []
    model_config = ConfigDict(from_attributes=True)

class UorgTreeItem(BaseModel):
    id: int
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    uorg_pai_id: Optional[int] = None
    postos: List[PostoSimpleResponse] = []
class UorgImportResponse(BaseModel):
    status: str
    mensagem: str
    total_processados: int
    inseridos: int
    atualizados: int
    hierarquias_vinculadas: int

ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"

def require_admin_user(current_user: dict = Depends(auth_handler.decode_token)) -> dict:
    username = current_user.get("sub") or current_user.get("username") or ""
    groups = current_user.get("groups", [])
    is_admin = (ADMIN_GROUP in groups) or (username.lower() == "admin")
    if not is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado: A funcionalidade de importar planilha é exclusiva para usuários com perfil Administrador."
        )
    return current_user

@router.post("/import-estrutura", response_model=UorgImportResponse)
async def import_estrutura(
    file: Optional[UploadFile] = File(None),
    clear_existing: bool = False,
    session: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(require_admin_user)
):
    import os
    username = admin_user.get("sub") or admin_user.get("username") or "admin"
    if file:
        content = await file.read()
        return await UorgController.import_estrutura_excel(session, content, login=username, clear_existing=clear_existing)
    else:
        # Tenta o arquivo padrão da pasta Downloads
        default_path = r"C:\Users\marcio.gomes.1\Downloads\Downloads\Estrutura oragnizacinalHC-UFPE.xlsx"
        if not os.path.exists(default_path):
            # Tenta também na pasta raiz de Downloads
            default_path = r"C:\Users\marcio.gomes.1\Downloads\Estrutura oragnizacinalHC-UFPE.xlsx"
            
        if not os.path.exists(default_path):
            raise HTTPException(status_code=400, detail="Nenhum arquivo enviado e o arquivo padrão 'Estrutura oragnizacinalHC-UFPE.xlsx' não foi encontrado na pasta Downloads.")
        return await UorgController.import_estrutura_excel(session, default_path, login=username, clear_existing=clear_existing)

@router.get("/reset-and-import-clean")
async def reset_and_import_clean(
    session: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(require_admin_user)
):
    """
    Limpa as UORGs existentes e reimporta a planilha oficial da pasta Downloads.
    """
    import os
    import traceback
    from sqlalchemy import text
    try:
        default_path = r"C:\Users\marcio.gomes.1\Downloads\Downloads\Estrutura oragnizacinalHC-UFPE.xlsx"
        if not os.path.exists(default_path):
            default_path = r"C:\Users\marcio.gomes.1\Downloads\Estrutura oragnizacinalHC-UFPE.xlsx"
        if not os.path.exists(default_path):
            raise HTTPException(status_code=400, detail="Arquivo 'Estrutura oragnizacinalHC-UFPE.xlsx' não encontrado na pasta Downloads.")
        
        # Reset limpo no banco
        await session.execute(text("PRAGMA foreign_keys = OFF"))
        await session.execute(text("UPDATE uorgs SET uorg_pai_id = NULL"))
        await session.execute(text("UPDATE funcionarios_lotacoes SET uorg_id = NULL WHERE uorg_id IS NOT NULL"))
        await session.execute(text("UPDATE usuario_gerencias SET uorg_id = NULL WHERE uorg_id IS NOT NULL"))
        await session.execute(text("DELETE FROM grade_dias"))
        await session.execute(text("DELETE FROM grades"))
        await session.execute(text("DELETE FROM postos WHERE uorg_id IS NOT NULL"))
        await session.execute(text("DELETE FROM uorgs"))
        await session.commit()
        await session.execute(text("PRAGMA foreign_keys = ON"))

        return await UorgController.import_estrutura_excel(session, default_path, login="sistema", clear_existing=False)
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@router.get("/{id}/subordinadas-ids", response_model=List[int])
async def get_subordinate_ids(id: int, session: AsyncSession = Depends(get_app_db_session)):
    """
    Retorna o ID da UORG e todos os IDs subordinados hierarquicamente a ela.
    """
    return await UorgProvider.get_descendant_ids(session, id)

@router.get("/seed-drae-now")
async def seed_drae_now(session: AsyncSession = Depends(get_app_db_session)):
    import traceback
    try:
        from scripts.seed_drae_abril import TABELA_DRAE
        from sqlalchemy import text
        # 1. Obter ou criar UORG DRAE
        res_uorg = await session.execute(text("SELECT id, nome, sigla FROM uorgs WHERE UPPER(sigla) = 'DRAE' OR UPPER(nome) LIKE '%DRAE%'"))
        row_uorg = res_uorg.fetchone()
        if row_uorg:
            drae_id = row_uorg[0]
        else:
            await session.execute(text("INSERT INTO uorgs (nome, sigla, login, data_alteracao) VALUES ('DIVISÃO DE REABILITAÇÃO E ATENÇÃO ESPECIALIZADA - DRAE', 'DRAE', 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_uorg2 = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(sigla) = 'DRAE'"))
            drae_id = res_uorg2.scalar()

        # 2. Obter ou criar Posto DRAE
        res_p = await session.execute(text(f"SELECT id FROM postos WHERE uorg_id = {drae_id} OR unidade_id = {drae_id}"))
        posto_id = res_p.scalar()
        if not posto_id:
            await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('GERAL - DRAE', {drae_id}, {drae_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_p2 = await session.execute(text(f"SELECT id FROM postos WHERE uorg_id = {drae_id}"))
            posto_id = res_p2.scalar()

        # 3. Cargo e Escala
        res_c = await session.execute(text("SELECT id FROM cargos WHERE UPPER(nome) LIKE '%ENFERM%' LIMIT 1"))
        cargo_id = res_c.scalar() or 1
        res_e = await session.execute(text("SELECT id FROM escalas WHERE sigla = 'D6' LIMIT 1"))
        escala_padrao_id = res_e.scalar() or 1
        res_v = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) = 'EBSERH' LIMIT 1"))
        vinculo_ebserh_id = res_v.scalar() or 1
        res_vrju = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) = 'RJU' LIMIT 1"))
        vinculo_rju_id = res_vrju.scalar() or vinculo_ebserh_id

        # Mapeamento de todas as escalas cadastradas
        res_all_e = await session.execute(text("SELECT sigla, id FROM escalas"))
        escalas_map = {r[0].strip().upper(): r[1] for r in res_all_e.fetchall()}

        processados = 0
        for item in TABELA_DRAE:
            mat = item["matricula"].strip()
            nome = item["nome"].strip()
            v_id = vinculo_rju_id if item["vinculo"] == "RJU" else vinculo_ebserh_id

            # Funcionario
            res_f = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
            func_id = res_f.scalar()
            if not func_id:
                res_fnome = await session.execute(text("SELECT id FROM funcionarios WHERE UPPER(nome) = :nome"), {"nome": nome.upper()})
                func_id = res_fnome.scalar()
                if func_id:
                    await session.execute(text("UPDATE funcionarios SET matricula = :mat WHERE id = :id"), {"mat": mat, "id": func_id})
                else:
                    await session.execute(text("""
                        INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                        VALUES (:mat, :nome, :cargo_id, :escala_id, :vinculo_id, 'sistema', CURRENT_TIMESTAMP)
                    """), {"mat": mat, "nome": nome, "cargo_id": cargo_id, "escala_id": escala_padrao_id, "vinculo_id": v_id})
                    await session.commit()
                    res_f2 = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
                    func_id = res_f2.scalar()

            # Lotação
            res_lot = await session.execute(text("SELECT id FROM funcionarios_lotacoes WHERE funcionario_id = :fid AND (uorg_id = :uid OR unidade_id = :uid)"), {"fid": func_id, "uid": drae_id})
            if not res_lot.scalar():
                await session.execute(text("""
                    INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                    VALUES (:fid, :uid, :uid, :pid, '2025-01-01', NULL, 'sistema', CURRENT_TIMESTAMP)
                """), {"fid": func_id, "uid": drae_id, "pid": posto_id})
                await session.commit()

            # Grade mes 4 ano 2026
            res_g = await session.execute(text("SELECT id FROM grades WHERE funcionario_id = :fid AND uorg_id = :uid AND mes = 4 AND ano = 2026"), {"fid": func_id, "uid": drae_id})
            grade_id = res_g.scalar()
            if grade_id:
                await session.execute(text("DELETE FROM grade_dias WHERE grade_id = :gid"), {"gid": grade_id})
            else:
                await session.execute(text("""
                    INSERT INTO grades (funcionario_id, uorg_id, posto_id, mes, ano, status, observacao, login, data_alteracao)
                    VALUES (:fid, :uid, :pid, 4, 2026, 'Rascunho', 'Carga DRAE Abril/2026', 'sistema', CURRENT_TIMESTAMP)
                """), {"fid": func_id, "uid": drae_id, "pid": posto_id})
                await session.commit()
                res_g2 = await session.execute(text("SELECT id FROM grades WHERE funcionario_id = :fid AND uorg_id = :uid AND mes = 4 AND ano = 2026"), {"fid": func_id, "uid": drae_id})
                grade_id = res_g2.scalar()

            # Dias
            for dia_num, sigla in item["dias"].items():
                e_id = escalas_map.get(sigla.upper())
                await session.execute(text("""
                    INSERT INTO grade_dias (grade_id, dia, escala_id, legenda_sigla)
                    VALUES (:gid, :dia, :eid, :sigla)
                """), {"gid": grade_id, "dia": dia_num, "eid": e_id, "sigla": sigla})

            processados += 1

        await session.commit()
        return {"status": "success", "total_processados": processados, "drae_id": drae_id}
    except Exception as exc:
        await session.rollback()
        return {"status": "error", "message": str(exc), "traceback": traceback.format_exc()}

@router.get("/seed-oncologia-now")
async def seed_oncologia_now(session: AsyncSession = Depends(get_app_db_session)):
    import traceback
    try:
        from scripts.seed_oncologia_abril import TABELA_ONCOLOGIA
        from sqlalchemy import text

        # 1. Localizar ou Criar UORG 'UNIDADE DE AMBULATÓRIO'
        res_amb = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) LIKE '%AMBULAT%' OR UPPER(sigla) = 'AMB'"))
        amb_id = res_amb.scalar()
        if not amb_id:
            await session.execute(text("INSERT INTO uorgs (nome, sigla, login, data_alteracao) VALUES ('UNIDADE DE AMBULATÓRIO', 'AMB', 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_amb2 = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(sigla) = 'AMB'"))
            amb_id = res_amb2.scalar()

        # 2. Localizar ou Criar UORG 'ONCOLOGIA'
        res_onco = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) = 'ONCOLOGIA'"))
        onco_id = res_onco.scalar()
        if not onco_id:
            await session.execute(text(f"INSERT INTO uorgs (nome, sigla, uorg_pai_id, login, data_alteracao) VALUES ('ONCOLOGIA', 'ONCO', {amb_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_onco2 = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) = 'ONCOLOGIA'"))
            onco_id = res_onco2.scalar()
        else:
            await session.execute(text(f"UPDATE uorgs SET uorg_pai_id = {amb_id} WHERE id = {onco_id} AND (uorg_pai_id IS NULL OR uorg_pai_id = '')"))
            await session.commit()

        # 3. Localizar ou Criar Posto 'ONCOLOGIA'
        res_posto = await session.execute(text(f"SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' AND (uorg_id = {onco_id} OR unidade_id = {onco_id})"))
        posto_id = res_posto.scalar()
        if not posto_id:
            await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('ONCOLOGIA', {onco_id}, {onco_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_posto2 = await session.execute(text(f"SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' AND (uorg_id = {onco_id} OR unidade_id = {onco_id})"))
            posto_id = res_posto2.scalar()

        # 4. Vínculos
        res_vinc = await session.execute(text("SELECT id, UPPER(nome) FROM vinculos"))
        vinculos_map = {r[1]: r[0] for r in res_vinc.fetchall()}
        if "CLT" not in vinculos_map:
            await session.execute(text("INSERT INTO vinculos (nome, login, data_alteracao) VALUES ('CLT', 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_vinc2 = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) = 'CLT'"))
            vinculos_map["CLT"] = res_vinc2.scalar()
        if "RJU" not in vinculos_map:
            await session.execute(text("INSERT INTO vinculos (nome, login, data_alteracao) VALUES ('RJU', 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_vinc3 = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) = 'RJU'"))
            vinculos_map["RJU"] = res_vinc3.scalar()

        # 5. Escalas
        escalas_necessarias = {
            "D6": ("07:00:00", "13:00:00", "DIURNO 6H"),
            "M15": ("07:00:00", "13:00:00", "MANHÃ 6H (M15)"),
            "FD0": ("00:00:00", "00:00:00", "FOLGA DIARISTA / FERIADO"),
            "FD6": ("07:00:00", "13:00:00", "FOLGA DIARISTA COMPENSADA"),
            "FE12D": ("07:00:00", "19:00:00", "FÉRIAS DIURNO 12H"),
            "FE6": ("07:00:00", "13:00:00", "FÉRIAS DIURNO 6H"),
            "FE8": ("07:00:00", "16:00:00", "FÉRIAS DIURNO 8H"),
            "AB12D": ("07:00:00", "19:00:00", "ABONO DIURNO 12H"),
            "MT26": ("07:00:00", "13:00:00", "MANHÃ/TARDE 6H")
        }
        res_esc = await session.execute(text("SELECT UPPER(sigla), id FROM escalas"))
        escalas_map = {r[0]: r[1] for r in res_esc.fetchall()}

        for sig, (ini, fim, desc) in escalas_necessarias.items():
            if sig not in escalas_map:
                await session.execute(text(f"""
                    INSERT INTO escalas (sigla, codigo, inicio_jornada, fim_jornada, descricao, apenas_assistenciais, login, data_alteracao)
                    VALUES ('{sig}', '{sig}', '{ini}', '{fim}', '{desc}', 1, 'sistema', CURRENT_TIMESTAMP)
                """))
                await session.commit()
                res_e2 = await session.execute(text(f"SELECT id FROM escalas WHERE UPPER(sigla) = '{sig}'"))
                escalas_map[sig] = res_e2.scalar()

        escala_padrao_id = escalas_map.get("D6") or (list(escalas_map.values())[0] if escalas_map else 1)

        # 6. Cargos
        res_c = await session.execute(text("SELECT id, UPPER(nome), carga_horaria FROM cargos"))
        cargos_map = {(r[1], r[2]): r[0] for r in res_c.fetchall()}

        async def get_or_create_cargo_async(nome_c, ch_c):
            key = (nome_c.upper(), ch_c)
            if key in cargos_map:
                return cargos_map[key]
            await session.execute(text(f"""
                INSERT INTO cargos (nome, carga_horaria, login, data_alteracao)
                VALUES ('{nome_c.upper()}', {ch_c}, 'sistema', CURRENT_TIMESTAMP)
            """))
            await session.commit()
            res_cid = await session.execute(text(f"SELECT id FROM cargos WHERE UPPER(nome) = '{nome_c.upper()}' AND carga_horaria = {ch_c}"))
            cid = res_cid.scalar()
            cargos_map[key] = cid
            return cid

        # 7. Processar cada colaborador
        processados = 0
        for item in TABELA_ONCOLOGIA:
            mat = item["matricula"].strip()
            nome = item["nome"].strip()
            cargo_nome = item["cargo"].strip()
            ch = item["ch"]
            vinc_tipo = item["vinculo"].strip().upper()
            v_id = vinculos_map.get(vinc_tipo, vinculos_map.get("CLT", 1))
            c_id = await get_or_create_cargo_async(cargo_nome, ch)

            # Funcionario
            res_f = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
            func_id = res_f.scalar()
            if not func_id:
                res_f2 = await session.execute(text("SELECT id FROM funcionarios WHERE UPPER(nome) = :nome"), {"nome": nome.upper()})
                func_id = res_f2.scalar()
                if func_id:
                    await session.execute(text("UPDATE funcionarios SET matricula = :mat, cargo_id = :cid, vinculo_id = :vid WHERE id = :fid"), {"mat": mat, "cid": c_id, "vid": v_id, "fid": func_id})
                else:
                    await session.execute(text("""
                        INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                        VALUES (:mat, :nome, :cid, :eid, :vid, 'sistema', CURRENT_TIMESTAMP)
                    """), {"mat": mat, "nome": nome, "cid": c_id, "eid": escala_padrao_id, "vid": v_id})
                    await session.commit()
                    res_f3 = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
                    func_id = res_f3.scalar()
            else:
                await session.execute(text("UPDATE funcionarios SET nome = :nome, cargo_id = :cid, vinculo_id = :vid WHERE id = :fid"), {"nome": nome, "cid": c_id, "vid": v_id, "fid": func_id})

            # Lotacao
            res_lot = await session.execute(text("SELECT id FROM funcionarios_lotacoes WHERE funcionario_id = :fid AND (uorg_id = :uid OR unidade_id = :uid)"), {"fid": func_id, "uid": onco_id})
            if not res_lot.scalar():
                await session.execute(text("""
                    INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                    VALUES (:fid, :uid, :uid, :pid, '2025-01-01', NULL, 'sistema', CURRENT_TIMESTAMP)
                """), {"fid": func_id, "uid": onco_id, "pid": posto_id})

            # Grade
            res_g = await session.execute(text("SELECT id FROM grades WHERE funcionario_id = :fid AND uorg_id = :uid AND mes = 4 AND ano = 2026"), {"fid": func_id, "uid": onco_id})
            grade_id = res_g.scalar()
            if grade_id:
                await session.execute(text("DELETE FROM grade_dias WHERE grade_id = :gid"), {"gid": grade_id})
            else:
                await session.execute(text("""
                    INSERT INTO grades (funcionario_id, uorg_id, posto_id, mes, ano, status, observacao, login, data_alteracao)
                    VALUES (:fid, :uid, :pid, 4, 2026, 'Rascunho', 'Escala Oncologia Ambulatório Abril/2026', 'sistema', CURRENT_TIMESTAMP)
                """), {"fid": func_id, "uid": onco_id, "pid": posto_id})
                await session.commit()
                res_g2 = await session.execute(text("SELECT id FROM grades WHERE funcionario_id = :fid AND uorg_id = :uid AND mes = 4 AND ano = 2026"), {"fid": func_id, "uid": onco_id})
                grade_id = res_g2.scalar()

            # Dias da escala
            for dia_num, sigla in item["dias"].items():
                e_id = escalas_map.get(sigla.upper())
                await session.execute(text("""
                    INSERT INTO grade_dias (grade_id, dia, escala_id, legenda_sigla)
                    VALUES (:gid, :dia, :eid, :sigla)
                """), {"gid": grade_id, "dia": dia_num, "eid": e_id, "sigla": sigla})

            processados += 1

        await session.commit()
        return {
            "status": "success",
            "mensagem": f"Escala de Oncologia para Abril/2026 carregada com sucesso para {processados} colaboradores!",
            "uorg_id": onco_id,
            "posto_id": posto_id,
            "total_colaboradores": processados
        }
    except Exception as exc:
        await session.rollback()
        return {"status": "error", "message": str(exc), "traceback": traceback.format_exc()}

@router.get("/recarregar-oncologia-18-v2")
async def recarregar_oncologia_18_v2(session: AsyncSession = Depends(get_app_db_session)):
    import traceback
    import importlib
    from sqlalchemy import text
    try:
        import scripts.seed_oncologia_abril as seed_mod
        importlib.reload(seed_mod)
        # Filtrar expressamente para conter apenas os 18 colaboradores oficiais (excluindo 2259734 se presente)
        TABELA_ONCOLOGIA = [
            item for item in seed_mod.TABELA_ONCOLOGIA 
            if item.get("matricula", "").strip() != "2259734" and "BRUNO" not in item.get("nome", "").upper()
        ][:18]

        # 1. Localizar UORG Ambulatório
        res_amb = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) LIKE '%AMBULAT%' OR UPPER(sigla) = 'AMB'"))
        amb_id = res_amb.scalar() or 28

        # 2. Localizar ou Criar UORG Oncologia (filha de Ambulatório)
        res_onco = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) = 'ONCOLOGIA'"))
        onco_id = res_onco.scalar()
        if not onco_id:
            await session.execute(text(f"INSERT INTO uorgs (nome, sigla, uorg_pai_id, login, data_alteracao) VALUES ('ONCOLOGIA', 'ONCO', {amb_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_onco2 = await session.execute(text("SELECT id FROM uorgs WHERE UPPER(nome) = 'ONCOLOGIA'"))
            onco_id = res_onco2.scalar()
        else:
            await session.execute(text(f"UPDATE uorgs SET uorg_pai_id = {amb_id} WHERE id = {onco_id}"))
            await session.commit()

        # 3. Localizar ou Criar Posto ONCOLOGIA vinculado à UORG Oncologia
        res_posto = await session.execute(text(f"SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' AND (uorg_id = {onco_id} OR unidade_id = {onco_id})"))
        posto_id = res_posto.scalar()
        if not posto_id:
            res_any_p = await session.execute(text("SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' LIMIT 1"))
            posto_id = res_any_p.scalar()
            if posto_id:
                await session.execute(text(f"UPDATE postos SET uorg_id = {onco_id}, unidade_id = {onco_id} WHERE id = {posto_id}"))
                await session.commit()
            else:
                await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('ONCOLOGIA', {onco_id}, {onco_id}, 'sistema', CURRENT_TIMESTAMP)"))
                await session.commit()
                res_p2 = await session.execute(text(f"SELECT id FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' AND uorg_id = {onco_id}"))
                posto_id = res_p2.scalar()

        # Excluir outros postos duplicados com nome ONCOLOGIA
        await session.execute(text(f"DELETE FROM postos WHERE UPPER(nome) = 'ONCOLOGIA' AND id != {posto_id}"))
        await session.commit()

        # 4. Mapeamento de Vínculos
        res_vinc = await session.execute(text("SELECT id, UPPER(nome) FROM vinculos"))
        vinculos_map = {r[1]: r[0] for r in res_vinc.fetchall()}

        # 5. Mapeamento de Escalas
        res_esc = await session.execute(text("SELECT UPPER(sigla), id FROM escalas"))
        escalas_map = {r[0]: r[1] for r in res_esc.fetchall()}

        # 6. Mapeamento de Cargos
        res_c = await session.execute(text("SELECT id, UPPER(nome), carga_horaria FROM cargos"))
        cargos_map = {(r[1], r[2]): r[0] for r in res_c.fetchall()}

        async def get_or_create_cargo(nome_c, ch_c):
            key = (nome_c.upper(), ch_c)
            if key in cargos_map:
                return cargos_map[key]
            await session.execute(text(f"INSERT INTO cargos (nome, carga_horaria, login, data_alteracao) VALUES ('{nome_c.upper()}', {ch_c}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res = await session.execute(text(f"SELECT id FROM cargos WHERE UPPER(nome) = '{nome_c.upper()}' AND carga_horaria = {ch_c}"))
            cid = res.scalar()
            cargos_map[key] = cid
            return cid

        # Matrículas dos 18 funcionários oficiais de Oncologia
        matriculas_18 = [item["matricula"].strip() for item in TABELA_ONCOLOGIA]

        # 7. Cadastrar / Atualizar os 18 funcionários
        func_ids_18 = []
        for item in TABELA_ONCOLOGIA:
            mat = item["matricula"].strip()
            nome = item["nome"].strip()
            cargo_nome = item["cargo"].strip()
            ch = item["ch"]
            vinc_tipo = item["vinculo"].strip().upper()
            v_id = vinculos_map.get(vinc_tipo, vinculos_map.get("CLT", 1))
            c_id = await get_or_create_cargo(cargo_nome, ch)
            e_id = escalas_map.get("D6", 1)

            res_f = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
            fid = res_f.scalar()
            if not fid:
                res_f2 = await session.execute(text("SELECT id FROM funcionarios WHERE UPPER(nome) = :nome"), {"nome": nome.upper()})
                fid = res_f2.scalar()
                if fid:
                    await session.execute(text("UPDATE funcionarios SET matricula = :mat, cargo_id = :cid, vinculo_id = :vid WHERE id = :fid"), {"mat": mat, "cid": c_id, "vid": v_id, "fid": fid})
                else:
                    await session.execute(text("""
                        INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                        VALUES (:mat, :nome, :cid, :eid, :vid, 'sistema', CURRENT_TIMESTAMP)
                    """), {"mat": mat, "nome": nome, "cid": c_id, "eid": e_id, "vid": v_id})
                    await session.commit()
                    res_f3 = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
                    fid = res_f3.scalar()
            else:
                await session.execute(text("UPDATE funcionarios SET nome = :nome, cargo_id = :cid, vinculo_id = :vid WHERE id = :fid"), {"nome": nome, "cid": c_id, "vid": v_id, "fid": fid})
            
            func_ids_18.append(fid)

        await session.commit()

        # 8. Limpar lotações indevidas na UORG Oncologia e no Posto Oncologia (deixando SOMENTE os 18)
        fid_list_str = ",".join(str(i) for i in func_ids_18)
        await session.execute(text(f"""
            DELETE FROM funcionarios_lotacoes 
            WHERE (uorg_id = {onco_id} OR unidade_id = {onco_id} OR posto_id = {posto_id})
              AND funcionario_id NOT IN ({fid_list_str})
        """))
        await session.execute(text(f"""
            DELETE FROM grades 
            WHERE (uorg_id = {onco_id} OR posto_id = {posto_id})
              AND funcionario_id NOT IN ({fid_list_str})
        """))
        await session.commit()

        # 9. Garantir que cada um dos 18 funcionários possui lotação na UORG Oncologia com o posto_id correto
        for fid in func_ids_18:
            res_lot = await session.execute(text(f"""
                SELECT id FROM funcionarios_lotacoes 
                WHERE funcionario_id = {fid} AND (uorg_id = {onco_id} OR unidade_id = {onco_id})
            """))
            lot_id = res_lot.scalar()
            if not lot_id:
                await session.execute(text(f"""
                    INSERT INTO funcionarios_lotacoes (funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                    VALUES ({fid}, {onco_id}, {onco_id}, {posto_id}, '2025-01-10', NULL, 'sistema', CURRENT_TIMESTAMP)
                """))
            else:
                await session.execute(text(f"""
                    UPDATE funcionarios_lotacoes 
                    SET uorg_id = {onco_id}, unidade_id = {onco_id}, posto_id = {posto_id}, data_inicio = '2025-01-10'
                    WHERE id = {lot_id}
                """))

        await session.commit()

        # 10. Cadastrar as grades completas para todos os meses de 2026 (1 a 12)
        meses_alvo = list(range(1, 13))  # Todos os 12 meses de 2026
        grades_criadas = 0

        for item, fid in zip(TABELA_ONCOLOGIA, func_ids_18):
            dias_dict = item["dias"]
            for mes_alvo in meses_alvo:
                res_g = await session.execute(text(f"""
                    SELECT id FROM grades 
                    WHERE funcionario_id = {fid} AND uorg_id = {onco_id} AND mes = {mes_alvo} AND ano = 2026
                """))
                gid = res_g.scalar()
                if gid:
                    await session.execute(text(f"DELETE FROM grade_dias WHERE grade_id = {gid}"))
                    await session.execute(text(f"UPDATE grades SET posto_id = {posto_id} WHERE id = {gid}"))
                else:
                    await session.execute(text(f"""
                        INSERT INTO grades (funcionario_id, uorg_id, posto_id, mes, ano, status, observacao, login, data_alteracao)
                        VALUES ({fid}, {onco_id}, {posto_id}, {mes_alvo}, 2026, 'Rascunho', 'Escala Oncologia Ambulatório', 'sistema', CURRENT_TIMESTAMP)
                    """))
                    await session.commit()
                    res_g2 = await session.execute(text(f"""
                        SELECT id FROM grades 
                        WHERE funcionario_id = {fid} AND uorg_id = {onco_id} AND mes = {mes_alvo} AND ano = 2026
                    """))
                    gid = res_g2.scalar()

                # Inserir dias respeitando a quantidade de dias do mês
                import calendar
                _, max_dias_mes = calendar.monthrange(2026, mes_alvo)
                for dia_num, sigla in dias_dict.items():
                    if dia_num <= max_dias_mes:
                        e_id = escalas_map.get(sigla.upper(), 1)
                        await session.execute(text(f"""
                            INSERT INTO grade_dias (grade_id, dia, escala_id, legenda_sigla)
                            VALUES ({gid}, {dia_num}, {e_id}, '{sigla}')
                        """))
                grades_criadas += 1

        await session.commit()

        return {
            "status": "success",
            "mensagem": "Oncologia reconfigurada com sucesso para exatamente 18 colaboradores e suas grades!",
            "uorg_id": onco_id,
            "posto_id": posto_id,
            "total_colaboradores": len(func_ids_18),
            "grades_criadas": grades_criadas
        }
    except Exception as exc:
        await session.rollback()
        return {"status": "error", "message": str(exc), "traceback": traceback.format_exc()}


@router.get("/lotar-hemodialise-20")
async def lotar_hemodialise_20(session: AsyncSession = Depends(get_app_db_session)):
    import traceback
    from datetime import date, datetime
    from sqlalchemy import text
    try:
        # Reload test comment 2026-09-29
        # 1. Obter UORG e Posto
        res_uorg = await session.execute(text("SELECT id, nome FROM uorgs WHERE UPPER(nome) LIKE '%URINARIO%' OR UPPER(sigla) = 'USUR' LIMIT 1"))
        uorg_row = res_uorg.first()
        if not uorg_row:
            return {"status": "error", "message": "UORG Unidade de Sistema Urinário não encontrada."}
        uorg_id = uorg_row[0]

        res_posto = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
        posto_row = res_posto.first()
        if not posto_row:
            # Criar posto se não existir
            await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('HEMODIÁLISE', {uorg_id}, {uorg_id}, 'sistema', CURRENT_TIMESTAMP)"))
            await session.commit()
            res_posto2 = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
            posto_row = res_posto2.first()
        posto_id = posto_row[0]

        # Garantir vínculo do posto à UORG
        await session.execute(text(f"UPDATE postos SET uorg_id = {uorg_id}, unidade_id = {uorg_id} WHERE id = {posto_id}"))
        await session.commit()

        # Obter IDs padrão para Cargo (Técnico em Enfermagem), Escala (D6 ou standard) e Vínculo
        res_c = await session.execute(text("SELECT id FROM cargos WHERE UPPER(nome) LIKE '%TECNICO%ENFERMAGEM%' LIMIT 1"))
        cargo_tec_id = res_c.scalar() or 1

        res_e = await session.execute(text("SELECT id FROM escalas WHERE UPPER(sigla) = 'D6' or UPPER(descricao) LIKE '%D6%' LIMIT 1"))
        escala_def_id = res_e.scalar()
        if not escala_def_id:
            res_e2 = await session.execute(text("SELECT id FROM escalas LIMIT 1"))
            escala_def_id = res_e2.scalar() or 1

        res_v = await session.execute(text("SELECT id FROM vinculos WHERE UPPER(nome) LIKE '%EBSERH%' LIMIT 1"))
        vinculo_def_id = res_v.scalar() or 1

        funcionarios_hemodialise = [
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

        for item in funcionarios_hemodialise:
            mat = item["matricula"].strip()
            nome = item["nome"].strip()

            # Buscar funcionário por matrícula ou nome
            res_f = await session.execute(
                text("SELECT id, nome, cargo_id FROM funcionarios WHERE matricula = :mat OR UPPER(nome) = :nome LIMIT 1"),
                {"mat": mat, "nome": nome.upper()}
            )
            f_row = res_f.first()

            if f_row:
                func_id = f_row[0]
                # Atualizar matricula caso tenha achado por nome
                await session.execute(
                    text("UPDATE funcionarios SET matricula = :mat WHERE id = :fid"),
                    {"mat": mat, "fid": func_id}
                )
            else:
                # Criar funcionário
                res_ins = await session.execute(
                    text("""
                        INSERT INTO funcionarios (matricula, nome, cargo_id, escala_id, vinculo_id, login, data_alteracao)
                        VALUES (:mat, :nome, :cid, :eid, :vid, 'sistema', CURRENT_TIMESTAMP)
                    """),
                    {"mat": mat, "nome": nome, "cid": cargo_tec_id, "eid": escala_def_id, "vid": vinculo_def_id}
                )
                await session.commit()
                res_f2 = await session.execute(text("SELECT id FROM funcionarios WHERE matricula = :mat"), {"mat": mat})
                func_id = res_f2.scalar()

            # Verificar lotação existente para este funcionário
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

            cadastrados.append({"matricula": mat, "nome": nome, "funcionario_id": func_id})

        await session.commit()

        return {
            "status": "success",
            "mensagem": f"Sucesso! {len(cadastrados)} funcionários foram cadastrados/lotados na Unidade de Sistema Urinário (Posto Hemodiálise) com data de início em {data_inicio_str}.",
            "uorg_id": uorg_id,
            "posto_id": posto_id,
            "total_cadastrados": len(cadastrados),
            "cadastrados": cadastrados
        }
    except Exception as exc:
        await session.rollback()
        return {"status": "error", "message": str(exc), "traceback": traceback.format_exc()}




@router.get("", response_model=List[UorgResponse])
async def get_all_uorgs(session: AsyncSession = Depends(get_app_db_session)):
    return await UorgController.get_all(session)

@router.get("/arvore", response_model=List[UorgTreeItem])
async def get_uorgs_tree(session: AsyncSession = Depends(get_app_db_session)):
    return await UorgController.get_arvore(session)


@router.get("/{id}", response_model=UorgResponse)
async def get_uorg_by_id(id: int, session: AsyncSession = Depends(get_app_db_session)):
    return await UorgController.get_by_id(session, id)

@router.post("", response_model=UorgResponse)
async def create_uorg(
    data: UorgCreate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UorgController.create(session, data.model_dump(), username)

@router.put("/{id}", response_model=UorgResponse)
async def update_uorg(
    id: int, 
    data: UorgUpdate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UorgController.update(session, id, data.model_dump(exclude_unset=True), username)

@router.delete("/{id}")
async def delete_uorg(
    id: int, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UorgController.delete(session, id)

