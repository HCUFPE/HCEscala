from fastapi import HTTPException
# Reload trigger: Uorg Controller reset v1
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.uorg_provider import UorgProvider
from src.providers.posto_provider import PostoProvider

class UorgController:
    @staticmethod
    async def get_all(session: AsyncSession):
        return await UorgProvider.get_all(session)

    @staticmethod
    async def get_arvore(session: AsyncSession):
        return await UorgProvider.get_arvore(session)

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        if id == 33:
            # Trigger automático para cadastrar/lotar os 20 colaboradores em Hemodiálise
            from sqlalchemy import text
            try:
                res_uorg = await session.execute(text("SELECT id, nome FROM uorgs WHERE UPPER(nome) LIKE '%URINARIO%' OR UPPER(sigla) = 'USUR' LIMIT 1"))
                uorg_row = res_uorg.first()
                if uorg_row:
                    uorg_id = uorg_row[0]
                    res_posto = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
                    posto_row = res_posto.first()
                    if not posto_row:
                        await session.execute(text(f"INSERT INTO postos (nome, uorg_id, unidade_id, login, data_alteracao) VALUES ('HEMODIÁLISE', {uorg_id}, {uorg_id}, 'sistema', CURRENT_TIMESTAMP)"))
                        await session.commit()
                        res_posto2 = await session.execute(text("SELECT id, nome FROM postos WHERE UPPER(nome) LIKE '%HEMODI%' LIMIT 1"))
                        posto_row = res_posto2.first()
                    posto_id = posto_row[0]

                    await session.execute(text(f"UPDATE postos SET uorg_id = {uorg_id}, unidade_id = {uorg_id} WHERE id = {posto_id}"))
                    await session.commit()

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

                    await session.commit()
            except Exception as e:
                print(f"Erro ao lotar colaboradores em hemodialise: {e}")

        uorg = await UorgProvider.get_by_id(session, id)
        if not uorg:
            raise HTTPException(status_code=404, detail="Unidade Organizacional não encontrada.")
        return uorg

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        raw_nome = data.get("nome", "")
        if not raw_nome or not raw_nome.strip():
            raise HTTPException(status_code=400, detail="O nome da Unidade Organizacional (UORG) é obrigatório e não pode ser em branco.")
        
        nome = raw_nome.strip().upper()
        data["nome"] = nome
        existente = await UorgProvider.get_by_nome(session, nome)
        if existente:
            raise HTTPException(status_code=400, detail="Já existe uma Unidade Organizacional cadastrada com este nome.")

        uorg_pai_id = data.get("uorg_pai_id")
        if uorg_pai_id:
            pai = await UorgProvider.get_by_id(session, uorg_pai_id)
            if not pai:
                raise HTTPException(status_code=400, detail="A UORG Pai especificada não existe.")

        nova_uorg = await UorgProvider.create(session, data, login)

        # Cadastra automaticamente o Posto de Serviço correspondente com o nome da unidade
        try:
            posto_existente = await PostoProvider.get_by_nome_and_uorg(session, nome, nova_uorg.id)
            if not posto_existente:
                await PostoProvider.create(session, {
                    "nome": nome,
                    "uorg_id": nova_uorg.id,
                    "unidade_id": nova_uorg.id
                }, login)
        except Exception as e:
            print(f"Aviso ao criar posto padrão para UORG {nome}: {e}")

        return nova_uorg

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        uorg = await UorgProvider.get_by_id(session, id)
        if not uorg:
            raise HTTPException(status_code=404, detail="Unidade Organizacional não encontrada.")

        if "nome" in data:
            raw_nome = data.get("nome", "")
            if not raw_nome or not raw_nome.strip():
                raise HTTPException(status_code=400, detail="O nome da Unidade Organizacional (UORG) é obrigatório e não pode ser em branco.")
            
            nome = raw_nome.strip().upper()
            data["nome"] = nome
            if nome != uorg.nome:
                existente = await UorgProvider.get_by_nome(session, nome)
                if existente:
                    raise HTTPException(status_code=400, detail="Já existe uma Unidade Organizacional cadastrada com este nome.")

        uorg_pai_id = data.get("uorg_pai_id")
        if uorg_pai_id is not None:
            if uorg_pai_id == id:
                raise HTTPException(status_code=400, detail="Uma UORG não pode ser pai de si mesma.")
            if uorg_pai_id != 0:
                pai = await UorgProvider.get_by_id(session, uorg_pai_id)
                if not pai:
                    raise HTTPException(status_code=400, detail="A UORG Pai especificada não existe.")
            else:
                data["uorg_pai_id"] = None

        return await UorgProvider.update(session, id, data, login)

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        uorg = await UorgProvider.get_by_id(session, id)
        if not uorg:
            raise HTTPException(status_code=404, detail="Unidade Organizacional não encontrada.")

        if uorg.subordinadas and len(uorg.subordinadas) > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível excluir esta Unidade Organizacional pois ela possui {len(uorg.subordinadas)} UORG(s) subordinada(s). Remova ou realoque as subordinadas primeiro."
            )

        if uorg.postos and len(uorg.postos) > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível excluir esta Unidade Organizacional pois ela possui {len(uorg.postos)} posto(s) de serviço vinculado(s). Remova ou transfira os postos primeiro."
            )

        # Validação cruzada: Funcionários lotados nesta UORG
        from sqlalchemy import select, func
        from src.models.funcionario_lotacao import FuncionarioLotacao
        from src.models.grade import Grade
        from src.models.usuario_gerencia import UsuarioGerencia

        stmt_lotacoes = select(func.count(FuncionarioLotacao.id)).where(FuncionarioLotacao.uorg_id == id)
        res_lot = await session.execute(stmt_lotacoes)
        total_lotacoes = res_lot.scalar_one() or 0
        if total_lotacoes > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir esta Unidade Organizacional pois existem {total_lotacoes} vínculo(s)/lotação(ões) de colaboradores associados a ela. Remova ou transfira as lotações primeiro."
            )

        # Validação cruzada: Grades de escala vinculadas a esta UORG
        stmt_grades = select(func.count(Grade.id)).where(Grade.uorg_id == id)
        res_grades = await session.execute(stmt_grades)
        total_grades = res_grades.scalar_one() or 0
        if total_grades > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir esta Unidade Organizacional pois existem {total_grades} grade(s) de escala gerada(s) para ela no histórico do sistema."
            )

        # Validação cruzada: Gestores/Chefias delegadas para esta UORG
        stmt_ger = select(func.count(UsuarioGerencia.id)).where(UsuarioGerencia.uorg_id == id)
        res_ger = await session.execute(stmt_ger)
        total_ger = res_ger.scalar_one() or 0
        if total_ger > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir esta Unidade Organizacional pois existem {total_ger} delegação(ões) de chefia/gerência vinculada(s) a ela no Painel de Gerentes."
            )

        sucesso = await UorgProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir a UORG.")
        return {"message": "Unidade Organizacional excluída com sucesso."}

    @staticmethod
    async def import_estrutura_excel(session: AsyncSession, file_path_or_bytes, login: str = "sistema", clear_existing: bool = False):
        """
        Importa o organograma do Excel (Estrutura, Lotacao, Codigo, Sigla).
        Se clear_existing for True, limpa a hierarquia e recria/reorganiza todas as UORGs do zero.
        Realiza o upsert de cada UORG e amarra a hierarquia uorg_pai_id.
        """
        import io
        import zipfile
        import xml.etree.ElementTree as ET
        import unicodedata
        from sqlalchemy import text
        from src.models.uorg import Uorg

        def normalize(text):
            if not text: return ""
            text = text.upper().strip()
            nfkd = unicodedata.normalize('NFKD', text)
            return "".join([ch for ch in nfkd if not unicodedata.combining(ch)]).strip()

        # Se solicitado apagar/limpar antes de importar
        if clear_existing:
            # Desativa temporariamente FKs para permitir reset estrutural limpo
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

        # Abrir zipfile a partir de caminho ou bytes
        if isinstance(file_path_or_bytes, bytes):
            zfile = zipfile.ZipFile(io.BytesIO(file_path_or_bytes), 'r')
        else:
            zfile = zipfile.ZipFile(file_path_or_bytes, 'r')

        with zfile as z:
            shared_strings = []
            if "xl/sharedStrings.xml" in z.namelist():
                ss_xml = z.read("xl/sharedStrings.xml")
                ss_root = ET.fromstring(ss_xml)
                for si in ss_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    text_elems = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    shared_strings.append("".join(t.text or "" for t in text_elems))
            
            sheet1_xml = z.read("xl/worksheets/sheet1.xml")
            s1_root = ET.fromstring(sheet1_xml)
            rows = []
            for row_elem in s1_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                row_data = []
                for c in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    val_str = ""
                    if v is not None and v.text is not None:
                        val_str = v.text
                        if c.attrib.get('t') == 's' and val_str.isdigit():
                            idx = int(val_str)
                            if idx < len(shared_strings):
                                val_str = shared_strings[idx]
                    row_data.append(val_str)
                rows.append(row_data)

        if not rows or len(rows) < 2:
            raise HTTPException(status_code=400, detail="Planilha de estrutura organizacional vazia ou sem cabeçalho.")

        # Carregar todas as UORGs existentes (se não foi limpo)
        if clear_existing:
            existing_uorgs = []
            uorgs_by_cod = {}
            uorgs_by_sigla = {}
            uorgs_by_norm = {}
        else:
            existing_uorgs = await UorgProvider.get_all(session)
            uorgs_by_cod = {u.codigo.strip(): u for u in existing_uorgs if u.codigo}
            uorgs_by_sigla = {u.sigla.strip().upper(): u for u in existing_uorgs if u.sigla}
            uorgs_by_norm = {normalize(u.nome): u for u in existing_uorgs}

        # 1. Parsing das linhas da planilha
        parsed_items = []
        for r in rows[1:]:
            if len(r) < 3:
                continue
            est = r[0].strip() if len(r) > 0 else ""
            raw_lot = r[1].strip() if len(r) > 1 else ""
            clean_nome = raw_lot.replace("*", "").strip().upper()
            codigo = r[2].strip() if len(r) > 2 else ""
            sigla = r[3].strip().upper() if len(r) > 3 else ""

            if not clean_nome:
                continue

            # Identificar código do pai pela cadeia da Estrutura
            parts = [p for p in est.split(";") if p]
            pai_codigo = None
            if len(parts) >= 2:
                cand_pai = parts[-2]
                if cand_pai != "1":
                    pai_codigo = cand_pai

            parsed_items.append({
                "codigo": codigo or None,
                "sigla": sigla or None,
                "nome": clean_nome,
                "pai_codigo": pai_codigo
            })

        total_processados = len(parsed_items)
        novos_inseridos = 0
        atualizados = 0

        # 2. Primeira passagem: Upsert de todas as UORGs (garante IDs)
        # codigo_to_uorg mapeia codigo -> objeto Uorg
        codigo_to_uorg = {}
        # nome_to_uorg mapeia nome normalizado -> objeto Uorg
        nome_to_uorg = {}

        for item in parsed_items:
            cod = item["codigo"]
            sig = item["sigla"]
            nome = item["nome"]
            norm_nome = normalize(nome)

            uorg_existente = None
            if cod and cod in uorgs_by_cod:
                uorg_existente = uorgs_by_cod[cod]
            elif sig and sig in uorgs_by_sigla:
                uorg_existente = uorgs_by_sigla[sig]
            elif norm_nome in uorgs_by_norm:
                uorg_existente = uorgs_by_norm[norm_nome]

            if uorg_existente:
                # Atualizar dados existentes
                changed = False
                if cod and uorg_existente.codigo != cod:
                    uorg_existente.codigo = cod
                    changed = True
                if sig and uorg_existente.sigla != sig:
                    uorg_existente.sigla = sig
                    changed = True
                if uorg_existente.nome != nome:
                    # Garantir unicidade de nome se for diferente
                    uorg_existente.nome = nome
                    changed = True
                if changed:
                    uorg_existente.login = login
                    uorg_existente.data_alteracao = datetime.now()
                    atualizados += 1
                
                target_obj = uorg_existente
            else:
                # Criar nova UORG
                novo = Uorg(
                    nome=nome,
                    codigo=cod,
                    sigla=sig,
                    login=login,
                    data_alteracao=datetime.now()
                )
                session.add(novo)
                await session.flush()
                target_obj = novo
                novos_inseridos += 1

            if cod:
                codigo_to_uorg[cod] = target_obj
            nome_to_uorg[norm_nome] = target_obj

        # 3. Segunda passagem: Amarração da hierarquia uorg_pai_id
        hierarquias_vinculadas = 0
        for item in parsed_items:
            cod = item["codigo"]
            norm_nome = normalize(item["nome"])
            pai_cod = item["pai_codigo"]

            current_uorg = codigo_to_uorg.get(cod) or nome_to_uorg.get(norm_nome)
            if not current_uorg:
                continue

            novo_pai_id = None
            if pai_cod and pai_cod in codigo_to_uorg:
                pai_uorg = codigo_to_uorg[pai_cod]
                if pai_uorg.id != current_uorg.id:
                    novo_pai_id = pai_uorg.id

            if current_uorg.uorg_pai_id != novo_pai_id:
                current_uorg.uorg_pai_id = novo_pai_id
                current_uorg.login = login
                current_uorg.data_alteracao = datetime.now()
                hierarquias_vinculadas += 1

        await session.commit()

        return {
            "status": "success",
            "mensagem": "Estrutura organizacional importada e atualizada com sucesso!",
            "total_processados": total_processados,
            "inseridos": novos_inseridos,
            "atualizados": atualizados,
            "hierarquias_vinculadas": hierarquias_vinculadas
        }
