from fastapi import FastAPI, HTTPException
# Reload trigger: sync_cargos_sequence_v1
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from .resources.database import DatabaseManager, Base
import src.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")

    # Initialize AGHU DB Manager and store in app.state
    aghu_dsn = os.getenv("POSTGRES_DSN")
    if aghu_dsn:
        app.state.aghu_db = DatabaseManager(aghu_dsn)
        print("AGHU PostgreSQL connection pool initialized.")
    else:
        print("WARNING: POSTGRES_DSN not found. Skipping AGHU DB initialization.")

    # Initialize App DB Manager (SQLite) and store in app.state
    app_dsn = os.getenv("SQLITE_DSN")
    if not app_dsn:
        raise ValueError("SQLITE_DSN not found in environment variables.")
    app.state.app_db = DatabaseManager(app_dsn)
    print("App SQLite connection pool initialized.")

    # Create tables for App DB (if they don't exist) - for development only, Alembic handles this in production
    async with app.state.app_db.engine.begin() as conn:
        # Migração automática de colunas para SQLite
        def _check_and_migrate(sync_conn):
            from sqlalchemy import text
            cursor = sync_conn.connection.cursor()
            
            # 1. Tabela escalas -> descricao
            cursor.execute("PRAGMA table_info(escalas)")
            columns = [row[1] for row in cursor.fetchall()]
            if columns and "descricao" not in columns:
                cursor.execute("ALTER TABLE escalas ADD COLUMN descricao VARCHAR(255) DEFAULT ''")
                print("Coluna 'descricao' adicionada à tabela 'escalas'.")

            # 2. Tabela postos -> garantir uorg_id e unidade_id compatíveis
            cursor.execute("PRAGMA table_info(postos)")
            posto_cols_info = cursor.fetchall()
            posto_col_names = [row[1] for row in posto_cols_info]
            
            if posto_cols_info:
                # Se existe coluna 'unidade_id' marcada como NOT NULL (notnull == 1)
                # ou se falta 'uorg_id'
                needs_postos_migration = False
                for col in posto_cols_info:
                    # row: (cid, name, type, notnull, dflt_value, pk)
                    if col[1] == 'unidade_id' and col[3] == 1:
                        needs_postos_migration = True
                        break

                if "uorg_id" not in posto_col_names:
                    needs_postos_migration = True

                if needs_postos_migration:
                    print("Executando migração de compatibilidade na tabela 'postos'...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS postos_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome VARCHAR(200) NOT NULL,
                            uorg_id INTEGER,
                            unidade_id INTEGER,
                            login VARCHAR(100) NOT NULL,
                            data_alteracao DATETIME
                        )
                    """)
                    
                    # Copiar dados existentes
                    if "uorg_id" in posto_col_names and "unidade_id" in posto_col_names:
                        cursor.execute("INSERT OR IGNORE INTO postos_new (id, nome, uorg_id, unidade_id, login, data_alteracao) SELECT id, nome, uorg_id, unidade_id, login, data_alteracao FROM postos")
                    elif "uorg_id" in posto_col_names:
                        cursor.execute("INSERT OR IGNORE INTO postos_new (id, nome, uorg_id, unidade_id, login, data_alteracao) SELECT id, nome, uorg_id, uorg_id, login, data_alteracao FROM postos")
                    elif "unidade_id" in posto_col_names:
                        cursor.execute("INSERT OR IGNORE INTO postos_new (id, nome, uorg_id, unidade_id, login, data_alteracao) SELECT id, nome, unidade_id, unidade_id, login, data_alteracao FROM postos")
                    
                    cursor.execute("DROP TABLE postos")
                    cursor.execute("ALTER TABLE postos_new RENAME TO postos")
                    print("Tabela 'postos' migrada com sucesso (uorg_id/unidade_id flexibilizados).")

            # 2.1 Tabela funcionarios_lotacoes -> garantir compatibilidade de colunas (uorg_id, unidade_id, posto_id nullable)
            cursor.execute("PRAGMA table_info(funcionarios_lotacoes)")
            lot_cols_info = cursor.fetchall()
            lot_col_names = [row[1] for row in lot_cols_info]
            if lot_cols_info:
                needs_lot_mig = False
                if "uorg_id" not in lot_col_names or "unidade_id" not in lot_col_names:
                    needs_lot_mig = True
                for col in lot_cols_info:
                    # Se unidade_id ou uorg_id ou posto_id estiver notnull indevidamente
                    if col[1] in ('unidade_id', 'uorg_id', 'posto_id') and col[3] == 1:
                        needs_lot_mig = True
                        break
                
                if needs_lot_mig:
                    print("Executando migração na tabela 'funcionarios_lotacoes'...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS funcionarios_lotacoes_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            funcionario_id INTEGER NOT NULL,
                            uorg_id INTEGER,
                            unidade_id INTEGER,
                            posto_id INTEGER,
                            data_inicio DATE NOT NULL,
                            data_fim DATE,
                            login VARCHAR(100) NOT NULL,
                            data_alteracao DATETIME
                        )
                    """)
                    # Copiar registros existentes de forma segura
                    cursor.execute("""
                        INSERT OR IGNORE INTO funcionarios_lotacoes_new (id, funcionario_id, uorg_id, unidade_id, posto_id, data_inicio, data_fim, login, data_alteracao)
                        SELECT 
                            id, 
                            funcionario_id, 
                            COALESCE(NULLIF(uorg_id, ''), NULLIF(unidade_id, '')), 
                            COALESCE(NULLIF(unidade_id, ''), NULLIF(uorg_id, '')), 
                            posto_id, 
                            data_inicio, 
                            data_fim, 
                            login, 
                            data_alteracao 
                        FROM funcionarios_lotacoes
                    """)
                    cursor.execute("DROP TABLE funcionarios_lotacoes")
                    cursor.execute("ALTER TABLE funcionarios_lotacoes_new RENAME TO funcionarios_lotacoes")
                    print("Tabela 'funcionarios_lotacoes' migrada com sucesso.")

            # 2.2 Migração: Transferir carga_horaria de cargos para funcionarios
            cursor.execute("PRAGMA table_info(funcionarios)")
            func_cols = [r[1] for r in cursor.fetchall()]
            if func_cols and "carga_horaria" not in func_cols:
                cursor.execute("ALTER TABLE funcionarios ADD COLUMN carga_horaria INTEGER NOT NULL DEFAULT 40")
                print("Coluna 'carga_horaria' adicionada à tabela 'funcionarios'.")
                # Inicializar carga_horaria dos funcionários com base na carga horária do cargo atual
                cursor.execute("PRAGMA table_info(cargos)")
                cargo_cols_temp = [r[1] for r in cursor.fetchall()]
                if "carga_horaria" in cargo_cols_temp:
                    cursor.execute("""
                        UPDATE funcionarios 
                        SET carga_horaria = COALESCE(
                            (SELECT c.carga_horaria FROM cargos c WHERE c.id = funcionarios.cargo_id), 
                            40
                        )
                    """)
                    print("Valores de 'carga_horaria' transferidos para os funcionários.")

            # 2.3 Tabela cargos -> migrar para tabela sem carga_horaria e com nome UNIQUE
            cursor.execute("PRAGMA table_info(cargos)")
            cargo_cols_info = [r[1] for r in cursor.fetchall()]
            if "carga_horaria" in cargo_cols_info:
                print("Migrando tabela 'cargos' para remover 'carga_horaria' e consolidar nomes únicos...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cargos_unificados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome VARCHAR(100) NOT NULL UNIQUE,
                        login VARCHAR(100) NOT NULL,
                        data_alteracao DATETIME
                    )
                """)
                # Inserir cargos distintos agrupados por nome
                cursor.execute("""
                    INSERT OR IGNORE INTO cargos_unificados (id, nome, login, data_alteracao)
                    SELECT MIN(id), TRIM(nome), login, data_alteracao FROM cargos GROUP BY TRIM(UPPER(nome))
                """)
                # Atualizar os funcionários para apontar para o ID canônico de cada cargo
                cursor.execute("""
                    UPDATE funcionarios
                    SET cargo_id = (
                        SELECT cu.id FROM cargos_unificados cu 
                        JOIN cargos c_antigo ON TRIM(UPPER(c_antigo.nome)) = TRIM(UPPER(cu.nome))
                        WHERE c_antigo.id = funcionarios.cargo_id
                    )
                    WHERE EXISTS (
                        SELECT 1 FROM cargos c_antigo WHERE c_antigo.id = funcionarios.cargo_id
                    )
                """)
                cursor.execute("DROP TABLE cargos")
                cursor.execute("ALTER TABLE cargos_unificados RENAME TO cargos")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_cargos_nome ON cargos (nome)")
                print("Tabela 'cargos' migrada com sucesso (carga horária agora fica em 'funcionarios').")

            # 2.4 Limpeza de matrículas com prefixo 99 e sufixo 26
            try:
                cursor.execute("SELECT id, matricula FROM funcionarios WHERE matricula LIKE '99%26'")
                funcs_to_clean = cursor.fetchall()
                for f_id, f_mat in funcs_to_clean:
                    cleaned_mat = f_mat.strip()
                    if cleaned_mat.startswith("99") and cleaned_mat.endswith("26") and len(cleaned_mat) > 4:
                        new_mat = cleaned_mat[2:-2]
                        # Verificar se já existe outro funcionário com a nova matrícula
                        cursor.execute("SELECT id FROM funcionarios WHERE matricula = ? AND id != ?", (new_mat, f_id))
                        conflito = cursor.fetchone()
                        if not conflito:
                            cursor.execute("UPDATE funcionarios SET matricula = ? WHERE id = ?", (new_mat, f_id))
                            print(f"Matrícula do funcionário {f_id} limpa: {f_mat} -> {new_mat}")
            except Exception as e_clean:
                print(f"Aviso ao limpar matrículas com 99...26: {e_clean}")

            # 2.5 Garantir tabela usuario_gerencias
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuario_gerencias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario VARCHAR(100) NOT NULL,
                        nome VARCHAR(200) NOT NULL,
                        nivel VARCHAR(50) NOT NULL,
                        uorg_id INTEGER,
                        posto_id INTEGER,
                        ativo BOOLEAN DEFAULT 1 NOT NULL,
                        login VARCHAR(100) NOT NULL,
                        data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (uorg_id) REFERENCES uorgs (id),
                        FOREIGN KEY (posto_id) REFERENCES postos (id)
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_usuario_gerencias_usuario ON usuario_gerencias (usuario)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_usuario_gerencias_uorg_id ON usuario_gerencias (uorg_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_usuario_gerencias_posto_id ON usuario_gerencias (posto_id)")

                # Garantir tabela audit_logs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario VARCHAR(100) NOT NULL,
                        tela VARCHAR(100) NOT NULL,
                        tabela VARCHAR(100) NOT NULL,
                        operacao VARCHAR(20) NOT NULL,
                        registro_id VARCHAR(100) NOT NULL,
                        dados_anteriores TEXT,
                        dados_posteriores TEXT,
                        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        revertido BOOLEAN DEFAULT 0 NOT NULL,
                        revertido_por VARCHAR(100),
                        revertido_em DATETIME
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_usuario ON audit_logs (usuario)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_tela ON audit_logs (tela)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_tabela ON audit_logs (tabela)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_operacao ON audit_logs (operacao)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_registro_id ON audit_logs (registro_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_data_hora ON audit_logs (data_hora)")
            except Exception as e_ger:
                print(f"Aviso ao verificar tabelas usuario_gerencias/audit_logs: {e_ger}")

            sync_conn.connection.commit()

        await conn.run_sync(_check_and_migrate)
        await conn.run_sync(Base.metadata.create_all)

    print("App SQLite tables checked/created.")

    yield

    # Shutdown
    print("Shutting down...")
    if hasattr(app.state, 'aghu_db') and app.state.aghu_db:
        await app.state.aghu_db.close_connection()
        print("AGHU PostgreSQL connection pool closed.")
    if hasattr(app.state, 'app_db') and app.state.app_db:
        await app.state.app_db.close_connection()
        print("App SQLite connection pool closed.")

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI(
    title="HC Escalas — Sistema de Gestão de Escalas de Serviço do Hospital das Clínicas da UFPE",
    description="API do Sistema de Gestão de Escalas de Serviço do Hospital das Clínicas da UFPE (HC-UFPE / EBSERH).",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuração de CORS para comunicação segura entre frontend e backend
# Permite origens locais típicas de desenvolvimento e produção
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:8000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de cabeçalhos de segurança anti-ataque
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Proteção contra Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Proteção contra MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Proteção contra XSS em navegadores mais antigos
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer Policy segura
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Controle de cache para rotas de API (evita armazenamento de dados sensíveis)
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Serve o frontend Vue 3 empacotado
os.makedirs("src/static/dist/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="src/static/dist/assets"), name="assets")
# Outros arquivos estáticos na raiz do dist (como favicon.ico)
app.mount("/static", StaticFiles(directory="src/static/dist"), name="static")

# Placeholder para incluir os roteadores da API
from .routers import paciente, auth, admin, aih, bpa, material, legenda, escala, cargo, vinculo, uorg, setor, unidade, posto, funcionario, feriado, grade, gerencia, divgp, digp, audit
app.include_router(paciente.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(audit.router)
app.include_router(aih.router)
app.include_router(bpa.router)
app.include_router(material.router)
app.include_router(legenda.router)
app.include_router(escala.router)
app.include_router(cargo.router)
app.include_router(vinculo.router)
app.include_router(uorg.router)
app.include_router(setor.router)
app.include_router(unidade.router)
app.include_router(posto.router)
app.include_router(funcionario.router)
app.include_router(feriado.router)
app.include_router(grade.router)
app.include_router(gerencia.router)
app.include_router(divgp.router)
app.include_router(digp.router)

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

health_router = APIRouter(prefix="/api", tags=["Health Check"])

@health_router.get("/health")
async def health_check(request: Request):
    # Teste simples de liveness / readiness
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "service": "HC-UTI Manager"}
    )

app.include_router(health_router)

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve o arquivo index.html para todas as rotas que não são da API ou arquivos estáticos.
    Isso é necessário para que o roteamento do Vue (SPA) funcione.
    """
    # Se a rota começa com 'api', deixa o roteador do FastAPI lidar
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    index_path = os.path.join("src", "static", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found"}

# Exemplo de criação e inclusão de roteador protegido por padrão:
# from fastapi import APIRouter, Depends
# from .auth.auth import auth_handler
# 
# # Proteção aplicada no nível do Roteador (Todas as rotas deste arquivo nascem trancadas)
# router = APIRouter(
#     prefix="/api/modulo",
#     tags=["Modulo"],
#     dependencies=[Depends(auth_handler.decode_token)] # Exige Token JWT válido
# )
# app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
