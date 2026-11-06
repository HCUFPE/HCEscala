#!/usr/bin/env bash
set -e

# ==========================================================
# GestorGrade - Script de Deploy Automatizado (FastAPI + Vue 3)
# ==========================================================

# Identifica automaticamente o diretório onde o script está localizado
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="gestorgrade"

echo "=================================================="
echo "🚀 Iniciando Deploy do GestorGrade em $APP_DIR"
echo "=================================================="

# 1. Ajustar repositórios do Debian (desabilitar CD-ROM residual) e instalar pacotes
echo "📦 [1/6] Verificando pacotes do sistema (Python, venv, curl)..."
if command -v apt-get &> /dev/null; then
    # Comentar repositório de CD-ROM residual do instalador Debian
    if [ -f /etc/apt/sources.list ]; then
        sed -i '/cdrom:/s/^/#/' /etc/apt/sources.list || true
    fi
    if [ -d /etc/apt/sources.list.d ]; then
        sed -i '/cdrom:/s/^/#/' /etc/apt/sources.list.d/*.list 2>/dev/null || true
    fi
    apt-get update -y || true
    apt-get install -y python3 python3-pip python3-venv curl || true
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip python3-virtualenv curl || true
fi

cd "$APP_DIR"

# 2. Configurar ambiente virtual Python
echo "🐍 [2/6] Configurando ambiente virtual Python..."
if [ ! -d "$APP_DIR/.venv" ]; then
    python3 -m venv "$APP_DIR/.venv"
fi

# 3. Instalar dependências Python
echo "📥 [3/6] Instalando dependências do Python..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 4. Criar arquivo .env se não existir
echo "⚙️  [4/6] Verificando arquivo de configuração .env..."
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/.env.example" ]; then
        cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        echo "  ℹ️ Arquivo .env criado a partir de .env.example"
    else
        cat << 'EOF' > "$APP_DIR/.env"
ENV=production
LOG_LEVEL=info
APP_DB_URL=sqlite+aiosqlite:///app.db
JWT_SECRET=supersecretkey_gestorgrade_hcupe_2026
JWT_EXP_HOURS=24
REFRESH_TOKEN_EXP_DAYS=30
AD_URL=ldap://ebserhnet.gov.br
AD_BASEDN=DC=ebserhnet,DC=gov,DC=br
EOF
        echo "  ℹ️ Arquivo .env padrão criado."
    fi
fi

# 5. Executar migrações do banco de dados (Alembic)
echo "🗄️  [5/6] Executando migrações do banco de dados..."
"$APP_DIR/.venv/bin/alembic" upgrade head || true

# 6. Gerar e configurar o serviço Systemd com o caminho correto
echo "🔄 [6/6] Configurando serviço Systemd ($SERVICE_NAME)..."
cat << EOF > "/etc/systemd/system/${SERVICE_NAME}.service"
[Unit]
Description=GestorGrade - Sistema de Gestão de Escalas e Grades (FastAPI + Vue 3)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8080 --workers 4
Restart=always
RestartSec=5
Environment="ENV=production"
Environment="PORT=8080"
EnvironmentFile=-${APP_DIR}/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

sleep 3

# 7. Verificar status do serviço
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo "=================================================="
    echo "✅ GestorGrade iniciado com SUCESSO!"
    echo "📍 Porta da Aplicação: 8080"
    echo "🌐 Acesse no seu navegador: http://10.34.0.17:8080"
    echo "📊 Status do serviço: systemctl status ${SERVICE_NAME}"
    echo "📋 Logs em tempo real: journalctl -u ${SERVICE_NAME} -f"
    echo "=================================================="
else
    echo "❌ Erro ao iniciar o serviço ${SERVICE_NAME}. Verifique os logs:"
    journalctl -u "${SERVICE_NAME}" -n 20 --no-pager
    exit 1
fi
