import urllib.request
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth.auth import auth_handler

def test_lock_rule():
    base_url = "http://127.0.0.1:8080"

    # Token 1: Gerente da Área (Sem grupo admin)
    token_gerente = auth_handler.create_access_token({"username": "gerente.enfermaria", "groups": ["Users", "Chefia-Enf"]})
    headers_gerente = {"Authorization": f"Bearer {token_gerente}", "Content-Type": "application/json"}

    # Token 2: Administrador / DIVGP.
    token_admin = auth_handler.create_access_token({"username": "admin.DIVGP.", "groups": ["GLO-SEC-HCPE-SETISD"]})
    headers_admin = {"Authorization": f"Bearer {token_admin}", "Content-Type": "application/json"}

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

    print("\n--- 1. Gerente cria uma grade em 'Rascunho' para o mês 7/2026 ---")
    status, data = req(headers_gerente, "GET", "/api/grades?mes=7&ano=2026")
    assert status == 200
    primeiro_func = data[0]
    func_id = primeiro_func["funcionario_id"]
    unidade_id = primeiro_func.get("unidade_id") or 1

    payload = {
        "funcionario_id": func_id,
        "unidade_id": unidade_id,
        "mes": 7,
        "ano": 2026,
        "status": "Rascunho",
        "observacao": "Escala preliminar",
        "dias": [
            {"dia": 1, "legenda_sigla": "M"},
            {"dia": 2, "legenda_sigla": "T"}
        ]
    }
    status, grade_created = req(headers_gerente, "POST", "/api/grades", payload)
    assert status == 200
    grade_id = grade_created["id"]
    print(f"Grade criada com ID={grade_id}, Status='{grade_created['status']}'")

    print("\n--- 2. Gerente edita a grade enquanto ainda está em 'Rascunho' ---")
    update_payload = {
        "dias": [
            {"dia": 1, "legenda_sigla": "M"},
            {"dia": 2, "legenda_sigla": "M"},
            {"dia": 3, "legenda_sigla": "T"}
        ]
    }
    status, grade_up = req(headers_gerente, "PUT", f"/api/grades/{grade_id}", update_payload)
    assert status == 200
    print(f"Edição permitida em Rascunho! Total de dias: {len(grade_up['dias'])}")

    print("\n--- 3. Publicando a Grade para a DIVGP. (status='Publicada') ---")
    status, pub_res = req(headers_gerente, "POST", f"/api/grades/{grade_id}/publicar")
    assert status == 200
    assert pub_res["status"] == "Publicada"
    print(f"Grade publicada com sucesso! Status='{pub_res['status']}'")

    print("\n--- 4. Gerente tenta EDITAR a grade Publicada -> Deve ser BLOQUEADO com 403 ---")
    status, err_put = req(headers_gerente, "PUT", f"/api/grades/{grade_id}", {"observacao": "Tentativa de troca de plantao"})
    print(f"Status PUT gerente: {status} | Resposta: {err_put}")
    assert status == 403
    print("[BLOQUEIO CONFIRMADO] Gerente não consegue alterar a grade publicada.")

    print("\n--- 5. Gerente tenta EXCLUIR a grade Publicada -> Deve ser BLOQUEADO com 403 ---")
    status, err_del = req(headers_gerente, "DELETE", f"/api/grades/{grade_id}")
    print(f"Status DELETE gerente: {status} | Resposta: {err_del}")
    assert status == 403
    print("[BLOQUEIO CONFIRMADO] Gerente não consegue excluir a grade publicada.")

    print("\n--- 6. Gerente tenta SOBRESCREVER criando ou copiando sobre a grade Publicada -> Deve ser BLOQUEADO com 403 ---")
    status, err_post = req(headers_gerente, "POST", "/api/grades", payload)
    print(f"Status POST gerente: {status} | Resposta: {err_post}")
    assert status == 403
    print("[BLOQUEIO CONFIRMADO] Gerente não pode sobrescrever grade publicada.")

    print("\n--- 7. Administrador/DIVGP. REABRE a grade para permitir correções ---")
    status, reabrir_res = req(headers_admin, "POST", f"/api/grades/{grade_id}/reabrir")
    assert status == 200
    assert reabrir_res["status"] == "Rascunho"
    print(f"Grade reaberta pelo Administrador/DIVGP.! Status atual: '{reabrir_res['status']}'")

    print("\n--- 8. Gerente agora consegue editar novamente a grade reaberta ---")
    status, grade_pos_reabertura = req(headers_gerente, "PUT", f"/api/grades/{grade_id}", {"observacao": "Plantões corrigidos pós reabertura"})
    assert status == 200
    print(f"Edição concluída com sucesso após reabertura! Obs: {grade_pos_reabertura['observacao']}")

    print("\n--- 9. Teste do Calendário de Feriados para Diaristas ---")
    # Cadastrar um feriado para o mês 7/2026 (Ex: 09/07/2026)
    novo_feriado = {
        "nome": "Revolução Constitucionalista",
        "data": "2026-07-09",
        "tipo": "Estadual"
    }
    status, fer_created = req(headers_admin, "POST", "/api/feriados", novo_feriado)
    print(f"Feriado cadastrado: status={status}, nome={fer_created.get('nome')}")

    # Consultar a matriz do mês 7/2026
    status, matrix_julho = req(headers_gerente, "GET", "/api/grades?mes=7&ano=2026")
    assert status == 200
    
    # Encontrar colaboradores diaristas
    diaristas = [c for c in matrix_julho if c.get("is_diarista")]
    print(f"Total de colaboradores encontrados: {len(matrix_julho)}, Diaristas: {len(diaristas)}")
    
    # Verificar o dia 9 (feriado)
    dia_9_info = next((d for d in matrix_julho[0]["dias"] if d["dia"] == 9), None)
    print(f"Informações do Dia 9 (Feriado): {dia_9_info}")
    assert dia_9_info is not None
    assert dia_9_info["is_feriado"] == True
    assert dia_9_info["feriado_nome"] == "Revolução Constitucionalista"
    print("[FERIADO VALIDADO COM SUCESSO] O calendário de feriados é refletido diretamente na matriz para diaristas!")

    print("\n[SUCESSO COMPLETO] Toda a política de bloqueio e governança de grade publicada validada com 100% de sucesso!")

if __name__ == "__main__":
    test_lock_rule()
