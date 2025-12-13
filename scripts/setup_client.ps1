$ErrorActionPreference = "Continue"

Write-Host "Instalando Sistema..." -ForegroundColor Cyan

# Verificar Python
$pyCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "Python OK: $pyCheck" -ForegroundColor Green

# Criar venv
if (-not (Test-Path ".venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao criar venv!" -ForegroundColor Red
        pause
        exit 1
    }
}

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERRO: venv nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}

# Instalar dependencias
Write-Host "Instalando dependencias (pode demorar)..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO na instalacao!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "Dependencias instaladas!" -ForegroundColor Green

# Criar Banco de Dados
if (-not (Test-Path "estoque_tabacaria.db")) {
    Write-Host "Criando banco de dados..." -ForegroundColor Yellow
    $dbScript = @'
import sqlite3
conn = sqlite3.connect("estoque_tabacaria.db")
with open("schema.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("OK")
'@
    & $venvPython -c $dbScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Banco criado!" -ForegroundColor Green
    }
}

# Criar pastas
New-Item -ItemType Directory -Force -Path "static\barcodes" | Out-Null
New-Item -ItemType Directory -Force -Path "static\Images" | Out-Null

# Mover Logo
if (Test-Path "Templates\Logo_tabacaria.png") {
    Move-Item -Force "Templates\Logo_tabacaria.png" "static\Images\Logo_tabacaria.png" -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Instalacao Concluida!" -ForegroundColor Green
Write-Host ""
