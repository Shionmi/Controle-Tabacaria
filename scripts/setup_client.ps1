$ErrorActionPreference = "Continue"

# Garantir que estamos no diretório correto (raiz do projeto)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appRoot = Split-Path -Parent $scriptPath
Set-Location $appRoot

Write-Host "Instalando Sistema..." -ForegroundColor Cyan
Write-Host "Diretorio: $appRoot" -ForegroundColor Gray

# Verificar se arquivos essenciais existem
if (-not (Test-Path "$appRoot\requirements.txt")) {
    Write-Host "ERRO: requirements.txt nao encontrado em $appRoot" -ForegroundColor Red
    Write-Host "Arquivos no diretorio:" -ForegroundColor Yellow
    Get-ChildItem $appRoot | Select-Object -ExpandProperty Name
    pause
    exit 1
}

if (-not (Test-Path "$appRoot\schema.sql")) {
    Write-Host "ERRO: schema.sql nao encontrado em $appRoot" -ForegroundColor Red
    pause
    exit 1
}

# Verificar Python
$pyCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "Python OK: $pyCheck" -ForegroundColor Green

# Criar venv
$venvPath = "$appRoot\.venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao criar venv!" -ForegroundColor Red
        pause
        exit 1
    }
}

$venvPython = "$venvPath\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERRO: venv nao encontrado em $venvPython!" -ForegroundColor Red
    pause
    exit 1
}

# Instalar dependencias
Write-Host "Instalando dependencias (pode demorar)..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r "$appRoot\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO na instalacao!" -ForegroundColor Red
    Write-Host "Tentando novamente com verbose..." -ForegroundColor Yellow
    & $venvPython -m pip install -r "$appRoot\requirements.txt"
    pause
    exit 1
}
Write-Host "Dependencias instaladas!" -ForegroundColor Green

# Criar Banco de Dados
$dbPath = "$appRoot\estoque_tabacaria.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "Criando banco de dados..." -ForegroundColor Yellow
    $dbScript = @"
import sqlite3
conn = sqlite3.connect('$($dbPath.Replace('\', '\\'))')
with open('$($appRoot.Replace('\', '\\'))\\schema.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print('OK')
"@
    & $venvPython -c $dbScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Banco criado!" -ForegroundColor Green
    }
}

# Criar pastas
$barcodesPath = "$appRoot\static\barcodes"
$imagesPath = "$appRoot\static\Images"

New-Item -ItemType Directory -Force -Path $barcodesPath | Out-Null
New-Item -ItemType Directory -Force -Path $imagesPath | Out-Null

# Mover Logo (se existir no lugar errado)
$oldLogo = "$appRoot\Templates\Logo_tabacaria.png"
$newLogo = "$imagesPath\Logo_tabacaria.png"
if ((Test-Path $oldLogo) -and -not (Test-Path $newLogo)) {
    Move-Item -Force $oldLogo $newLogo -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Instalacao Concluida!" -ForegroundColor Green
Write-Host ""
