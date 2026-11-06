# ==========================================================
# GestorGrade - Script de Envio e Deploy para VM 10.34.0.17
# ==========================================================

$TargetHost = "10.34.0.17"
$TargetUser = "root"
$RemoteDir = "/opt/appgrade"
$Tarball = "appgrade_deploy.tar.gz"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando envio do pacote para $TargetUser@$TargetHost" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 0. Compilar Frontend (Vue 3 / Vite)
if (Test-Path "frontend/package.json") {
    Write-Host "🔨 Compilando o Frontend (Vue 3 / Vite)..." -ForegroundColor Yellow
    Push-Location frontend
    npm run build
    Pop-Location
}

# 1. Gerar pacote atualizado
Write-Host "📦 Gerando pacote atualizado ($Tarball)..." -ForegroundColor Yellow
tar -czf $Tarball --exclude=".git" --exclude=".venv" --exclude=".agents" --exclude="node_modules" --exclude="__pycache__" --exclude="frontend/node_modules" src alembic alembic.ini requirements.txt pyproject.toml .env.example scripts data dados_rh.tsv app.db deploy_vm.sh gestorgrade.service gestorgrade.nginx.conf

# 2. Criar diretório remoto e transferir arquivo
Write-Host "📤 Enviando $Tarball para ${TargetUser}@${TargetHost}:${RemoteDir}..." -ForegroundColor Yellow
ssh "${TargetUser}@${TargetHost}" "mkdir -p $RemoteDir"
scp $Tarball "${TargetUser}@${TargetHost}:${RemoteDir}/"

# 3. Descompactar e executar o script de deploy na VM
Write-Host "⚙️  Executando instalação e inicialização do serviço na VM..." -ForegroundColor Yellow
ssh "${TargetUser}@${TargetHost}" "cd $RemoteDir && tar -xzf $Tarball && chmod +x deploy_vm.sh && ./deploy_vm.sh"

Write-Host "==================================================" -ForegroundColor Green
Write-Host "✨ Processo de Deploy finalizado!" -ForegroundColor Green
Write-Host "🌐 Acesse: http://${TargetHost}:8080" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
