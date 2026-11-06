import json
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.resources.database import DatabaseManager
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.funcionario_ferias import FuncionarioFerias
from src.models.cargo import Cargo
from src.models.escala import Escala
from src.models.unidade import Unidade
from src.models.setor import Setor
from src.models.posto import Posto
from src.models.vinculo import Vinculo

async def seed_data():
    load_dotenv()
    
    app_dsn = os.getenv("SQLITE_DSN")
    if not app_dsn:
        print("Erro: SQLITE_DSN não configurado.")
        return
        
    db = DatabaseManager(app_dsn)
    
    transcript_path = r"C:\Users\marcio.gomes.1\.gemini\antigravity-ide\brain\e8edc338-329a-47fb-9fb9-9d4429e51d21\.system_generated\logs\transcript_full.jsonl"
    
    last_user_input = None
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines):
                data = json.loads(line)
                if data.get('type') == 'USER_INPUT':
                    last_user_input = data.get('content', '')
                    if "ler  a planilha abaixo e cadastrar na tabela funcionarios" in last_user_input:
                        break
    except Exception as e:
        print(f"Erro lendo transcript: {e}")
        return

    if not last_user_input:
        print("Não foi possível encontrar os dados na última mensagem.")
        return

    # Processar linhas da planilha
    all_lines = last_user_input.split('\n')
    csv_lines = [line for line in all_lines if '\t' in line]
    
    if not csv_lines:
        print("Nenhuma linha com tabulação encontrada.")
        return
        
    # Ignorar cabeçalho se houver
    if "Matricula" in csv_lines[0]:
        csv_lines = csv_lines[1:]

    async with db.engine.begin() as conn:
        pass # just to ensure tables can be accessed if needed, but we use async session
        
    async with db.async_session_maker() as session:
        # Garantir que existe um Setor Padrão para novas unidades
        result_setor = await session.execute(select(Setor).limit(1))
        setor_padrao = result_setor.scalars().first()
        if not setor_padrao:
            setor_padrao = Setor(nome="SETOR PADRAO (SISTEMA)", sigla="SPS", login="sistema")
            session.add(setor_padrao)
            await session.commit()
            await session.refresh(setor_padrao)

        # Garantir que existe uma Escala Padrão
        result_escala = await session.execute(select(Escala).limit(1))
        escala_padrao = result_escala.scalars().first()
        if not escala_padrao:
            from datetime import time
            escala_padrao = Escala(
                codigo="DIAR", sigla="DIARISTA", inicio_jornada=time(8, 0), fim_jornada=time(17, 0),
                apenas_assistenciais=False, login="sistema"
            )
            session.add(escala_padrao)
            await session.commit()
            await session.refresh(escala_padrao)
        
        # Caches
        cargos_cache = {}
        unidades_cache = {}
        
        # Carregar caches
        for c in (await session.execute(select(Cargo))).scalars().all():
            cargos_cache[c.nome.upper()] = c
            
        for u in (await session.execute(select(Unidade))).scalars().all():
            unidades_cache[u.nome.upper()] = u

        cadastrados = 0
        erros = 0
        
        print(f"Iniciando processamento de {len(csv_lines)} registros...")

        for idx, line in enumerate(csv_lines):
            parts = line.split('\t')
            if len(parts) < 8:
                continue
                
            vinculo = parts[0].strip()
            matricula = parts[1].strip()
            nome = parts[2].strip()
            # 3 = Cargo Comissao
            descricao1 = parts[4].strip() # TECNICO EM ENFERMAGEM - 36 H
            descricao2 = parts[5].strip() # Tecnico em Enfermagem
            lotacao = parts[6].strip()
            ingresso = parts[7].strip()
            
            # Ajustar carga horaria
            carga = 40
            if "36 H" in descricao1: carga = 36
            elif "24 H" in descricao1: carga = 24
            elif "30 H" in descricao1: carga = 30
            
            nome_cargo = descricao1.upper() if descricao1 else descricao2.upper()
            if not nome_cargo:
                nome_cargo = "CARGO NAO ESPECIFICADO"
                
            # Obter ou criar Cargo
            if nome_cargo not in cargos_cache:
                novo_cargo = Cargo(nome=nome_cargo, carga_horaria=carga, login="sistema")
                session.add(novo_cargo)
                await session.flush()
                cargos_cache[nome_cargo] = novo_cargo
                
            cargo_obj = cargos_cache[nome_cargo]
            
            # Obter ou criar Unidade
            nome_unidade = lotacao.upper()
            if not nome_unidade:
                nome_unidade = "UNIDADE NAO ESPECIFICADA"
                
            if nome_unidade not in unidades_cache:
                nova_unidade = Unidade(nome=nome_unidade, setor_id=setor_padrao.id, login="sistema")
                session.add(nova_unidade)
                await session.flush()
                unidades_cache[nome_unidade] = nova_unidade
                
            unidade_obj = unidades_cache[nome_unidade]
            
            # Verificar se funcionario ja existe
            result = await session.execute(select(Funcionario).where(Funcionario.matricula == matricula))
            func = result.scalars().first()
            
            if not func:
                func = Funcionario(
                    matricula=matricula,
                    nome=nome.upper(),
                    cargo_id=cargo_obj.id,
                    escala_id=escala_padrao.id,
                    login="sistema"
                )
                session.add(func)
                await session.flush()
                
                # Parse data
                try:
                    data_inicio = datetime.strptime(ingresso, "%d/%m/%Y").date()
                except:
                    data_inicio = datetime.now().date()
                    
                lotacao_obj = FuncionarioLotacao(
                    funcionario_id=func.id,
                    unidade_id=unidade_obj.id,
                    data_inicio=data_inicio,
                    login="sistema"
                )
                session.add(lotacao_obj)
                
                cadastrados += 1
            else:
                # Ja existe, pula
                erros += 1
                
            if (idx + 1) % 100 == 0:
                print(f"Processados {idx + 1} registros...")

        print("Salvando no banco de dados...")
        await session.commit()
        print(f"Finalizado! {cadastrados} funcionarios cadastrados. {erros} pulados (já existentes ou erro).")

if __name__ == "__main__":
    asyncio.run(seed_data())
