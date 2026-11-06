import os
import io
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import HTTPException

from src.models.cargo import Cargo
from src.models.vinculo import Vinculo
from src.models.escala import Escala
from src.models.uorg import Uorg
from src.models.posto import Posto
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao

def normalize(txt: str) -> str:
    if not txt:
        return ""
    nfkd = unicodedata.normalize('NFKD', txt.strip().upper())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

class FuncionarioImporter:
    @staticmethod
    async def import_from_excel(
        session: AsyncSession,
        file_path_or_bytes: Any,
        login: str = "sistema",
        sheet_target: str = "Relação nominal trabalhador"
    ) -> Dict[str, Any]:
        """
        Importa os colaboradores, vínculos, cargos e lotações da aba 'Relação nominal trabalhador'.
        """
        if isinstance(file_path_or_bytes, bytes):
            zfile = zipfile.ZipFile(io.BytesIO(file_path_or_bytes), 'r')
        else:
            zfile = zipfile.ZipFile(file_path_or_bytes, 'r')

        with zfile as z:
            # 1. Carregar sharedStrings.xml
            shared_strings: List[str] = []
            if "xl/sharedStrings.xml" in z.namelist():
                ss_xml = z.read("xl/sharedStrings.xml")
                ss_root = ET.fromstring(ss_xml)
                for si in ss_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    text_elems = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    shared_strings.append("".join(t.text or "" for t in text_elems))

            # 2. Localizar a sheet target no workbook.xml
            wb_xml = z.read("xl/workbook.xml")
            wb_root = ET.fromstring(wb_xml)
            r_id = None
            found_sheet_name = ""
            for s in wb_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                name = s.attrib.get('name', '')
                if normalize(name) == normalize(sheet_target) or 'NOMINAL' in normalize(name):
                    r_id = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    found_sheet_name = name
                    break

            if not r_id:
                # Fallback para primeira planilha
                r_id = "rId1"

            # 3. Ler o target rels
            target_path = "xl/worksheets/sheet1.xml"
            if "xl/_rels/workbook.xml.rels" in z.namelist():
                rels_xml = z.read("xl/_rels/workbook.xml.rels")
                rels_root = ET.fromstring(rels_xml)
                for rel in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                    if rel.attrib.get('Id') == r_id:
                        target = rel.attrib.get('Target', '').lstrip('/')
                        if not target.startswith('xl/'):
                            target = f"xl/{target}"
                        target_path = target
                        break

            if target_path not in z.namelist():
                target_path = "xl/worksheets/sheet1.xml"

            # 4. Ler as linhas da worksheet
            sheet_xml = z.read(target_path)
            sh_root = ET.fromstring(sheet_xml)
            rows = []
            for row_elem in sh_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                cells_by_col = {}
                for c in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    r_ref = c.attrib.get('r', '')
                    col_letter = "".join(ch for ch in r_ref if ch.isalpha())
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    val_str = ""
                    if v is not None and v.text is not None:
                        val_str = v.text
                        if c.attrib.get('t') == 's' and val_str.isdigit():
                            idx = int(val_str)
                            if idx < len(shared_strings):
                                val_str = shared_strings[idx]
                    cells_by_col[col_letter] = val_str
                rows.append(cells_by_col)

        if not rows or len(rows) < 2:
            raise HTTPException(status_code=400, detail="Planilha de colaboradores vazia ou sem dados.")

        # Cache de Vinculos
        res_vinc = await session.execute(select(Vinculo))
        db_vinculos = {normalize(v.nome): v for v in res_vinc.scalars().all()}

        # Cache de Cargos
        res_cargo = await session.execute(select(Cargo))
        db_cargos = {normalize(c.nome): c for c in res_cargo.scalars().all()}

        # Cache de Escalas (padrao D6 ou primeira encontrada)
        res_escala = await session.execute(select(Escala))
        escalas_list = res_escala.scalars().all()
        escala_padrao = None
        for esc in escalas_list:
            if esc.sigla.upper() in ["D6", "D", "ADM", "M6"]:
                escala_padrao = esc
                break
        if not escala_padrao and escalas_list:
            escala_padrao = escalas_list[0]
        elif not escala_padrao:
            from datetime import time
            escala_padrao = Escala(
                inicio_jornada=time(7, 0),
                fim_jornada=time(13, 0),
                sigla="D6",
                codigo="D6",
                descricao="Turno Diurno 6 Horas",
                apenas_assistenciais=False,
                login="sistema"
            )
            session.add(escala_padrao)
            await session.flush()

        # Cache de UORGs
        res_uorg = await session.execute(select(Uorg))
        db_uorgs = {normalize(u.nome): u for u in res_uorg.scalars().all()}

        # Cache de Postos
        res_postos = await session.execute(select(Posto))
        db_postos = {}
        for p in res_postos.scalars().all():
            k = (p.uorg_id, normalize(p.nome))
            db_postos[k] = p

        # Cache de Funcionarios existentes por Matricula
        res_func = await session.execute(select(Funcionario))
        db_funcs = {f.matricula.strip(): f for f in res_func.scalars().all()}

        # Cache de Lotações ativas por Funcionario ID
        res_lot = await session.execute(select(FuncionarioLotacao).where(FuncionarioLotacao.data_fim.is_(None)))
        db_lots_ativas = {l.funcionario_id: l for l in res_lot.scalars().all()}

        criados = 0
        atualizados = 0
        lotacoes_criadas = 0
        data_padrao_inicio = date(2025, 1, 1)

        # Processar linhas (a partir da linha 2)
        for r in rows[1:]:
            vinc_raw = r.get('A', '').strip()
            matr_raw = r.get('B', '').strip()
            nome_raw = r.get('C', '').strip()
            cargo_desc_raw = r.get('E', '').strip() or r.get('F', '').strip()
            lotacao_raw = r.get('G', '').strip()
            ingresso_raw = r.get('H', '').strip()

            if not matr_raw or not nome_raw:
                continue

            # Sanitização: se a matrícula iniciar com 99 e terminar com 26, remover os prefixos/sufixos
            if matr_raw.startswith("99") and matr_raw.endswith("26") and len(matr_raw) > 4:
                matr_raw = matr_raw[2:-2]

            # 1. Vínculo
            vinc_nome = "EBSERH" if "EFETIVO" in normalize(vinc_raw) or "EMPREGADO" in normalize(vinc_raw) else "RJU"
            if "RJU" in normalize(vinc_raw):
                vinc_nome = "RJU"
            norm_v = normalize(vinc_nome)
            vinculo_obj = db_vinculos.get(norm_v)
            if not vinculo_obj:
                vinculo_obj = Vinculo(nome=vinc_nome, login=login)
                session.add(vinculo_obj)
                await session.flush()
                db_vinculos[norm_v] = vinculo_obj

            # 2. Cargo e Carga Horária
            # Extrair carga horária (ex: 36 H, 40 H, 24 H, 30 H)
            ch_match = re.search(r'(\d+)\s*H', cargo_desc_raw.upper())
            carga_horaria = int(ch_match.group(1)) if ch_match else 40
            
            # Limpar nome do cargo (remover sufixos tipo "- 36 H", "- RJU")
            clean_cargo_nome = re.sub(r'-\s*\d+\s*H.*$', '', cargo_desc_raw, flags=re.IGNORECASE).strip()
            clean_cargo_nome = re.sub(r'-\s*RJU.*$', '', clean_cargo_nome, flags=re.IGNORECASE).strip().upper()
            if not clean_cargo_nome:
                clean_cargo_nome = cargo_desc_raw.upper() or "COLABORADOR"

            norm_c = normalize(clean_cargo_nome)
            cargo_obj = db_cargos.get(norm_c)
            if not cargo_obj:
                cargo_obj = Cargo(
                    nome=clean_cargo_nome,
                    login=login
                )
                session.add(cargo_obj)
                await session.flush()
                db_cargos[norm_c] = cargo_obj

            # 3. UORG / Lotação
            uorg_obj = None
            if lotacao_raw:
                norm_lot = normalize(lotacao_raw)
                uorg_obj = db_uorgs.get(norm_lot)
                if not uorg_obj:
                    # Tentar correspondência parcial
                    for u_nome_norm, u_inst in db_uorgs.items():
                        if u_nome_norm in norm_lot or norm_lot in u_nome_norm:
                            uorg_obj = u_inst
                            break
                if not uorg_obj:
                    # Criar UORG caso não exista ainda
                    uorg_obj = Uorg(
                        nome=lotacao_raw.strip().upper(),
                        sigla="",
                        login=login
                    )
                    session.add(uorg_obj)
                    await session.flush()
                    db_uorgs[normalize(uorg_obj.nome)] = uorg_obj

            # Posto de Serviço padrão para a UORG
            posto_obj = None
            if uorg_obj:
                posto_key = (uorg_obj.id, normalize(uorg_obj.nome))
                posto_obj = db_postos.get(posto_key)
                if not posto_obj:
                    posto_obj = Posto(
                        nome=uorg_obj.nome,
                        uorg_id=uorg_obj.id,
                        unidade_id=uorg_obj.id,
                        login=login
                    )
                    session.add(posto_obj)
                    await session.flush()
                    db_postos[posto_key] = posto_obj

            # 4. Funcionário
            func_obj = db_funcs.get(matr_raw)
            if not func_obj:
                func_obj = Funcionario(
                    matricula=matr_raw,
                    nome=nome_raw.strip().upper(),
                    carga_horaria=carga_horaria,
                    cargo_id=cargo_obj.id,
                    escala_id=escala_padrao.id,
                    vinculo_id=vinculo_obj.id,
                    login=login
                )
                session.add(func_obj)
                await session.flush()
                db_funcs[matr_raw] = func_obj
                criados += 1
            else:
                func_obj.nome = nome_raw.strip().upper()
                func_obj.carga_horaria = carga_horaria
                func_obj.cargo_id = cargo_obj.id
                func_obj.vinculo_id = vinculo_obj.id
                atualizados += 1

            # 5. Lotação
            if uorg_obj:
                lot_ativa = db_lots_ativas.get(func_obj.id)
                if not lot_ativa or lot_ativa.uorg_id != uorg_obj.id:
                    if lot_ativa and lot_ativa.uorg_id != uorg_obj.id:
                        # Encerrar anterior
                        lot_ativa.data_fim = data_padrao_inicio

                    nova_lot = FuncionarioLotacao(
                        funcionario_id=func_obj.id,
                        uorg_id=uorg_obj.id,
                        posto_id=posto_obj.id if posto_obj else None,
                        data_inicio=data_padrao_inicio,
                        data_fim=None,
                        login=login
                    )
                    session.add(nova_lot)
                    db_lots_ativas[func_obj.id] = nova_lot
                    lotacoes_criadas += 1

        await session.commit()

        return {
            "sucesso": True,
            "aba_processada": found_sheet_name or sheet_target,
            "total_linhas": len(rows) - 1,
            "funcionarios_criados": criados,
            "funcionarios_atualizados": atualizados,
            "lotacoes_vinculadas": lotacoes_criadas,
            "mensagem": f"Importação concluída com sucesso! {criados} novos colaboradores cadastrados e {atualizados} atualizados."
        }
