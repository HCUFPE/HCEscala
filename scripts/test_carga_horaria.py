import urllib.request
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth.auth import auth_handler

def test_carga_horaria_rules():
    base_url = "http://127.0.0.1:8080"

    # Token de Administrador
    token_admin = auth_handler.create_access_token({"username": "admin", "groups": ["GLO-SEC-HCPE-SETISD"]})
    headers_admin = {"Authorization": f"Bearer {token_admin}", "Content-Type": "application/json"}

    # Token de Gerente de Unidade
    token_gerente = auth_handler.create_access_token({"username": "gerente.enfermaria", "groups": ["Users"]})
    headers_gerente = {"Authorization": f"Bearer {token_gerente}", "Content-Type": "application/json"}

    def req(headers, method, path, data=None):
        url = f"{base_url}{path}"
        req_data = json.dumps(data).encode("utf-8") if data is not None else None
        req_obj = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req_obj) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body
            return e.code, parsed

    print("\n--- 1. Buscar Funcionarios e Unidades ---")
    status, funcs = req(headers_admin, "GET", "/api/funcionarios")
    assert status == 200 and len(funcs) > 0
    func = funcs[0]
    func_id = func["id"]
    cargo_ch = func["cargo"]["carga_horaria"] if func.get("cargo") else 40
    print(f"Colaborador selecionado: {func['nome']} (ID={func_id}, Cargo={func.get('cargo', {}).get('nome')}, CH Semanal={cargo_ch}h)")

    status, unidades = req(headers_admin, "GET", "/api/unidades")
    assert status == 200 and len(unidades) > 0
    unidade_id = unidades[0]["id"]

    print("\n--- 2. Testar Gravacao de Grade Excedendo Carga Horaria (Deve Bloquear com 400) ---")
    # Gerar 25 plantões de 12h = 300h (ultrapassa teto de ~101h para 24h/sem ou ~177h para 40h/sem)
    dias_excedentes = [{"dia": d, "legenda_sigla": "D", "descricao": "Plantao Diurno 12h"} for d in range(1, 26)]
    payload_excesso = {
        "funcionario_id": func_id,
        "unidade_id": unidade_id,
        "mes": 8,
        "ano": 2026,
        "status": "Rascunho",
        "dias": dias_excedentes
    }

    status, err_resp = req(headers_gerente, "POST", "/api/grades", payload_excesso)
    print(f"Status retorno tentativa com horas excedentes: {status} | Resposta: {err_resp}")
    assert status == 400
    assert "ultrapassa a carga" in err_resp.get("detail", "").lower()
    print("[SUCESSO] Bloqueio de carga horaria excessiva validado!")

    print("\n--- 3. Testar Gravacao de Grade Dentro da Carga Horaria Permitida ---")
    # Gerar 6 plantões de 12h = 72h (dentro do limite contratual do colaborador)
    dias_validos = [{"dia": d, "legenda_sigla": "D", "descricao": "Plantao Diurno 12h"} for d in [2, 6, 10, 14, 18, 22]]
    payload_valido = {
        "funcionario_id": func_id,
        "unidade_id": unidade_id,
        "mes": 8,
        "ano": 2026,
        "status": "Rascunho",
        "dias": dias_validos
    }

    status, grade_salva = req(headers_gerente, "POST", "/api/grades", payload_valido)
    assert status == 200
    print(f"[SUCESSO] Grade valida salva: ID={grade_salva['id']}, Total Dias={len(grade_salva.get('dias', []))}")

    print("\n--- 4. Verificar Metricas de Carga Horaria na Matriz (/api/grades) ---")
    status, matrix = req(headers_admin, "GET", f"/api/grades?mes=8&ano=2026&unidade_id={unidade_id}")
    assert status == 200
    row = next((r for r in matrix if r["funcionario_id"] == func_id), None)
    assert row is not None
    print(f"Metricas retornadas para {row['nome']}:")
    print(f"  - CH Semanal: {row.get('carga_horaria_semanal')}h")
    print(f"  - CH Mensal Teto: {row.get('carga_horaria_mensal_teto')}h")
    print(f"  - Total Horas Escaladas: {row.get('total_horas_escaladas')}h")
    print(f"  - Saldo de Horas: {row.get('saldo_horas')}h")
    print(f"  - Horas Excedentes: {row.get('horas_excedentes')}h")
    print(f"  - Ultrapassou Carga Horaria: {row.get('ultrapassou_carga_horaria')}")

    assert row.get("total_horas_escaladas") == 72.0
    assert row.get("ultrapassou_carga_horaria") == False

    print("\n[TESTES FINALIZADOS COM SUCESSO] Todas as validacoes de soma e limites de carga horaria foram aprovadas com 100% de sucesso!")

if __name__ == "__main__":
    test_carga_horaria_rules()
