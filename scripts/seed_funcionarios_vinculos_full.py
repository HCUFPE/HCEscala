import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.resources.database import DatabaseManager
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.cargo import Cargo
from src.models.escala import Escala
from src.models.unidade import Unidade
from src.models.setor import Setor
from src.models.vinculo import Vinculo

async def main():
    load_dotenv()
    app_dsn = os.getenv("SQLITE_DSN", "sqlite+aiosqlite:///app.db")
    db = DatabaseManager(app_dsn)

    # 1. Carregar registros de dados_rh.tsv e dados_vinculos_novos.tsv
    raw_records = []
    
    files_to_read = ['dados_rh.tsv', 'dados_vinculos_novos.tsv']
    for filename in files_to_read:
        if not os.path.exists(filename):
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('<') or line.startswith('DADO'):
                    continue
                parts = line.split('\t')
                if len(parts) >= 6:
                    vinculo_txt = parts[0].strip()
                    mat_txt = parts[1].strip()
                    if vinculo_txt.lower() == 'vinculo' or mat_txt.lower() == 'matricula':
                        continue
                    nome_txt = parts[2].strip().upper()
                    
                    # Identificar campos dependendo da quantidade de colunas
                    if len(parts) >= 8:
                        # Formato: Vinculo, Matricula, Nome, Cargo Comissao, Descricao1, Descricao2, Lotacao, Ingresso
                        cargo_txt = parts[4].strip() or parts[5].strip()
                        lotacao_txt = parts[6].strip()
                        ingresso_txt = parts[7].strip()
                    elif len(parts) == 6:
                        # Formato: Vinculo, Matricula, Nome, Descricao, Lotacao, Ingresso
                        cargo_txt = parts[3].strip()
                        lotacao_txt = parts[4].strip()
                        ingresso_txt = parts[5].strip()
                    else:
                        cargo_txt = parts[3].strip()
                        lotacao_txt = parts[-2].strip()
                        ingresso_txt = parts[-1].strip()

                    raw_records.append({
                        'vinculo': vinculo_txt,
                        'matricula': mat_txt,
                        'nome': nome_txt,
                        'cargo': cargo_txt,
                        'lotacao': lotacao_txt,
                        'ingresso': ingresso_txt
                    })

    print(f"Total de linhas lidas dos arquivos: {len(raw_records)}")

    # Deduplicar por matrícula dando preferência ao registro mais completo
    by_matricula = {}
    for r in raw_records:
        mat = r['matricula']
        if mat not in by_matricula:
            by_matricula[mat] = r
        else:
            # Atualiza se tiver mais dados
            if r['vinculo'] and not by_matricula[mat]['vinculo']:
                by_matricula[mat]['vinculo'] = r['vinculo']
            if r['cargo'] and len(r['cargo']) > len(by_matricula[mat]['cargo']):
                by_matricula[mat]['cargo'] = r['cargo']

    print(f"Total de matrículas únicas a processar: {len(by_matricula)}")

    async with db.async_session_maker() as session:
        # Garantir Setor Padrão
        res_setor = await session.execute(select(Setor).limit(1))
        setor_padrao = res_setor.scalars().first()
        if not setor_padrao:
            setor_padrao = Setor(nome="SETOR PADRÃO", sigla="SPAD", login="sistema")
            session.add(setor_padrao)
            await session.flush()

        # Garantir Escala Padrão
        res_esc = await session.execute(select(Escala).limit(1))
        escala_padrao = res_esc.scalars().first()
        if not escala_padrao:
            from datetime import time
            escala_padrao = Escala(
                codigo="D8", sigla="D8", inicio_jornada=time(8, 0), fim_jornada=time(17, 0),
                apenas_assistenciais=False, login="sistema"
            )
            session.add(escala_padrao)
            await session.flush()

        # Carregar Caches
        vinculos_cache = {}
        for v in (await session.execute(select(Vinculo))).scalars().all():
            vinculos_cache[v.nome.strip().upper()] = v

        cargos_cache = {}
        for c in (await session.execute(select(Cargo))).scalars().all():
            cargos_cache[c.nome.strip().upper()] = c

        unidades_cache = {}
        for u in (await session.execute(select(Unidade))).scalars().all():
            unidades_cache[u.nome.strip().upper()] = u

        # 2. Garantir todos os Vínculos
        vinculos_adicionados = 0
        for r in by_matricula.values():
            v_nome = r['vinculo'].strip()
            if v_nome and v_nome.upper() not in vinculos_cache:
                novo_v = Vinculo(nome=v_nome, login="sistema")
                session.add(novo_v)
                await session.flush()
                vinculos_cache[v_nome.upper()] = novo_v
                vinculos_adicionados += 1

        print(f"Vínculos garantidos no banco. Novos adicionados: {vinculos_adicionados}")

        # 3. Processar funcionários
        cadastrados = 0
        atualizados = 0

        for r in by_matricula.values():
            mat = r['matricula']
            nome = r['nome']
            v_nome = r['vinculo'].strip()
            c_nome = r['cargo'].strip().upper() or "CARGO GERAL"
            u_nome = r['lotacao'].strip().upper() or "UNIDADE GERAL"
            ing_str = r['ingresso'].strip()

            # Obter vinculo_id
            vinculo_obj = vinculos_cache.get(v_nome.upper()) if v_nome else None
            vinculo_id = vinculo_obj.id if vinculo_obj else None

            # Obter ou criar Cargo
            if c_nome not in cargos_cache:
                carga = 40
                if "36 H" in c_nome: carga = 36
                elif "24 H" in c_nome: carga = 24
                elif "30 H" in c_nome: carga = 30
                elif "20 H" in c_nome: carga = 20
                novo_c = Cargo(nome=c_nome, carga_horaria=carga, login="sistema")
                session.add(novo_c)
                await session.flush()
                cargos_cache[c_nome] = novo_c
            cargo_obj = cargos_cache[c_nome]

            # Obter ou criar Unidade
            if u_nome not in unidades_cache:
                nova_u = Unidade(nome=u_nome, setor_id=setor_padrao.id, login="sistema")
                session.add(nova_u)
                await session.flush()
                unidades_cache[u_nome] = nova_u
            unidade_obj = unidades_cache[u_nome]

            # Parse data de ingresso
            try:
                data_inicio = datetime.strptime(ing_str, "%d/%m/%Y").date()
            except:
                data_inicio = datetime.now().date()

            # Verificar se funcionário já existe
            res_func = await session.execute(select(Funcionario).where(Funcionario.matricula == mat))
            func = res_func.scalars().first()

            if not func:
                # Criar novo
                func = Funcionario(
                    matricula=mat,
                    nome=nome,
                    cargo_id=cargo_obj.id,
                    escala_id=escala_padrao.id,
                    vinculo_id=vinculo_id,
                    login="sistema"
                )
                session.add(func)
                await session.flush()

                # Criar Lotação
                lotacao = FuncionarioLotacao(
                    funcionario_id=func.id,
                    unidade_id=unidade_obj.id,
                    data_inicio=data_inicio,
                    login="sistema"
                )
                session.add(lotacao)
                cadastrados += 1
            else:
                # Atualizar existente
                func.nome = nome
                func.cargo_id = cargo_obj.id
                func.vinculo_id = vinculo_id
                
                # Verificar se já tem lotação para a unidade
                res_lot = await session.execute(
                    select(FuncionarioLotacao).where(
                        FuncionarioLotacao.funcionario_id == func.id,
                        FuncionarioLotacao.unidade_id == unidade_obj.id
                    )
                )
                lot = res_lot.scalars().first()
                if not lot:
                    lotacao = FuncionarioLotacao(
                        funcionario_id=func.id,
                        unidade_id=unidade_obj.id,
                        data_inicio=data_inicio,
                        login="sistema"
                    )
                    session.add(lotacao)

                atualizados += 1

        await session.commit()
        print(f"Carga finalizada com SUCESSO!")
        print(f"Novos funcionários cadastrados: {cadastrados}")
        print(f"Funcionários existentes atualizados com Vínculo: {atualizados}")

        # 4. Verificar estatísticas de colaboradores com múltiplos vínculos
        from collections import Counter
        all_funcs = (await session.execute(select(Funcionario))).scalars().all()
        nomes_counter = Counter(f.nome for f in all_funcs)
        duplos = {nome: count for nome, count in nomes_counter.items() if count > 1}
        print(f"\nTotal geral de funcionários no banco: {len(all_funcs)}")
        print(f"Colaboradores com 2 ou mais vínculos/matrículas cadastrados: {len(duplos)}")
        print("Exemplos de colaboradores com múltiplos vínculos no banco:")
        for nome in list(duplos.keys())[:10]:
            print(f" - {nome} ({duplos[nome]} matrículas/vínculos)")

if __name__ == "__main__":
    asyncio.run(main())
