import urllib.request
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth.auth import auth_handler

def test_gerencias_and_divgp_panel():
    base_url = "http://127.0.0.1:8080"

    # Token 1: DIVGP / Admin Geral
    token_admin = auth_handler.create_access_token({"username": "admin.divgp", "groups": ["GLO-SEC-HCPE-SETISD"]})
    headers_admin = {"Authorization": f"Bearer {token_admin}", "Content-Type": "application/json"}

    # Token 2: Gerente de Setor
    token_setor = auth_handler.create_access_token({"username": "gerente.setor.cirurgia", "groups": ["Users"]})
    headers_setor = {"Authorization": f"Bearer {token_setor}", "Content-Type": "application/json"}

    # Token 3: Gerente de Unidade
    token_unidade = auth_handler.create_access_token({"username": "gerente.unidade.uti", "groups": ["Users"]})
    headers_unidade = {"Authorization": f"Bearer {token_unidade}", "Content-Type": "application/json"}

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

    print("\n--- 1. DIVGP cadastra Gerente de Setor e Gerente de Unidade ---")
    # Buscar setores e unidades disponíveis
    status, setores = req(headers_admin, "GET", "/api/setores")
    assert status == 200
    setor_id = setores[0]["id"] if setores else 1

    status, unidades = req(headers_admin, "GET", "/api/unidades")
    assert status == 200
    unidade_id = unidades[0]["id"] if unidades else 1

    # Cadastrar Gerente de Setor
    payload_setor = {
        "usuario": "gerente.setor.cirurgia",
        "nome": "Dr. Carlos Gerente Setor",
        "nivel": "SETOR",
        "setor_id": setor_id,
        "ativo": True
    }
    status, g_setor = req(headers_admin, "POST", "/api/gerencias", payload_setor)
    assert status == 200
    print(f"Gerente de Setor criado com sucesso: ID={g_setor['id']}, Nível='{g_setor['nivel']}', Setor='{g_setor.get('setor', {}).get('nome')}'")

    # Cadastrar Gerente de Unidade
    payload_unidade = {
        "usuario": "gerente.unidade.uti",
        "nome": "Enf. Roberta Chefe UTI",
        "nivel": "UNIDADE",
        "unidade_id": unidade_id,
        "ativo": True
    }
    status, g_unid = req(headers_admin, "POST", "/api/gerencias", payload_unidade)
    assert status == 200
    print(f"Gerente de Unidade criada com sucesso: ID={g_unid['id']}, Nível='{g_unid['nivel']}', Unidade='{g_unid.get('unidade', {}).get('nome')}'")

    print("\n--- 2. Resolução de Escopo Hierárquico (/api/gerencias/me) ---")
    # Testar escopo do Gerente de Setor
    status, scope_setor = req(headers_setor, "GET", "/api/gerencias/me")
    assert status == 200
    print(f"Escopo Gerente de Setor: Nível={scope_setor['nivel']}, Unidades acessíveis={scope_setor['unidade_ids']}")
    assert scope_setor["nivel"] == "SETOR"
    assert isinstance(scope_setor["unidade_ids"], list)

    # Testar escopo do Gerente de Unidade
    status, scope_unid = req(headers_unidade, "GET", "/api/gerencias/me")
    assert status == 200
    print(f"Escopo Gerente de Unidade: Nível={scope_unid['nivel']}, Unidades acessíveis={scope_unid['unidade_ids']}")
    assert scope_unid["nivel"] == "UNIDADE"
    assert scope_unid["unidade_ids"] == [unidade_id]

    # Testar escopo do Administrador DIVGP
    status, scope_admin = req(headers_admin, "GET", "/api/gerencias/me")
    assert status == 200
    print(f"Escopo DIVGP / Admin: is_admin={scope_admin['is_admin']}, Nível={scope_admin['nivel']}")
    assert scope_admin["is_admin"] == True

    print("\n--- 3. Teste de Permissões: Usuário não-admin tentando cadastrar gerência -> Deve retornar 403 ---")
    status, err_g = req(headers_setor, "POST", "/api/gerencias", payload_unidade)
    print(f"Status tentativa não-admin: {status} | Resposta: {err_g}")
    assert status == 403

    print("\n--- 4. Teste do Painel Institucional DIVGP (/api/divgp/status-unidades) ---")
    status, divgp_status = req(headers_admin, "GET", "/api/divgp/status-unidades?mes=7&ano=2026")
    assert status == 200
    sumario = divgp_status["sumario"]
    print(f"Sumário DIVGP: Total Unidades={sumario['total_unidades']}, 100% Homologadas={sumario['unidades_100']}, Com Pendências={sumario['unidades_pendentes']}, Conformidade Geral={sumario['percentual_geral']}%")
    assert "total_unidades" in sumario
    assert "unidades" in divgp_status
    print(f"Primeira unidade no painel: {divgp_status['unidades'][0]['unidade_nome']} | Status={divgp_status['unidades'][0]['status_homologacao']} | Progresso={divgp_status['unidades'][0]['percentual_conclusao']}%")

    print("\n--- 5. Teste de Colaboradores Faltantes (/api/divgp/faltantes) ---")
    status, faltantes = req(headers_admin, "GET", f"/api/divgp/faltantes?unidade_id={unidade_id}&mes=7&ano=2026")
    assert status == 200
    print(f"Total de colaboradores com pendências na unidade {unidade_id}: {len(faltantes)}")
    if faltantes:
        print(f"Exemplo de faltante: {faltantes[0]['nome']} ({faltantes[0]['matricula']}) - Status Grade: '{faltantes[0]['grade_status']}'")

    print("\n--- 6. Teste de Segurança: Usuário não-admin tentando acessar Painel DIVGP -> Deve retornar 403 ---")
    status, err_divgp = req(headers_setor, "GET", "/api/divgp/status-unidades?mes=7&ano=2026")
    print(f"Status acesso não-admin a /api/divgp/status-unidades: {status} | Resposta: {err_divgp}")
    assert status == 403

    print("\n[TESTES FINALIZADOS COM SUCESSO] Todos os requisitos de gestão de gerentes, visibilidade hierárquica e painel DIVGP validados com 100% de sucesso!")

if __name__ == "__main__":
    test_gerencias_and_divgp_panel()
