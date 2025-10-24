<#
.SYNOPSIS
Script de instalação do Sistema de Controle de Estoque para Tabacaria.

.DESCRIPTION
Este script automatiza a configuração completa do sistema em Windows 11, incluindo:
- Verificação e validação do Python
- Criação do ambiente virtual (.venv)
- Instalação de todas as dependências
- Criação do banco de dados SQLite
- Configuração das pastas necessárias
- Posicionamento correto do logo
- Inicialização opcional do aplicativo

.PARAMETER StartApp
Se fornecido, inicia o aplicativo após a configuração.

.EXAMPLE
.\scripts\setup_client.ps1
    Configura o ambiente sem iniciar o app.

.EXAMPLE
.\scripts\setup_client.ps1 -StartApp
    Configura o ambiente e inicia o app automaticamente.

.NOTES
Requisitos:
- Windows 11
- Python 3.10 ou superior (64-bit recomendado)
- Conexão com internet para baixar pacotes
- PowerShell 5.1 ou superior

Autor: Sistema profissional desenvolvido para gestão de estoque
Data: Outubro 2023
#>

param(
    [switch]$StartApp
)

function Write-Step { param($Text)
    Write-Host "`n📋 $Text" -ForegroundColor Cyan
}

function Write-Success { param($Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Warning { param($Text)
    Write-Host "⚠️ $Text" -ForegroundColor Yellow
}

function Write-Error { param($Text)
    Write-Host "❌ ERROR: $Text" -ForegroundColor Red
}

function ErrExit { param($msg)
    Write-Error $msg
    exit 1
}

# Header bonito
$header = @"

╔═══════════════════════════════════════════╗
║     Instalação - Controle de Tabacaria    ║
║           Sistema Profissional            ║
╚═══════════════════════════════════════════╝

"@
Write-Host $header -ForegroundColor Magenta

# Verificar Windows 11
Write-Step "Verificando sistema operacional"
$osInfo = Get-CimInstance Win32_OperatingSystem
$isWin11 = $osInfo.Caption -match "Windows 11"
if (-not $isWin11) {
    Write-Warning "Sistema não é Windows 11. O sistema pode funcionar, mas foi otimizado para Windows 11."
}

# Verificar PowerShell
Write-Step "Verificando versão do PowerShell"
$psVersion = $PSVersionTable.PSVersion.Major
if ($psVersion -lt 5) {
    ErrExit "PowerShell 5.1 ou superior é necessário. Versão atual: $psVersion"
}

# Verificar Python
$py = Get-Command python -ErrorAction SilentlyContinue
if(-not $py){ ErrExit 'Python not found in PATH. Please install Python 3.10+ and add to PATH.' }
Write-Host "Python detected: $(python --version)"

# Create venv
if(-not (Test-Path '.venv')){
    Write-Host 'Creating virtual environment .venv...' -ForegroundColor Yellow
    python -m venv .venv
} else { Write-Host '.venv already exists, skipping creation.' }

$venvPython = Join-Path -Path '.venv' -ChildPath 'Scripts\python.exe'
if(-not (Test-Path $venvPython)){ ErrExit "venv python not found at $venvPython" }

Write-Host 'Upgrading pip and installing requirements...' -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip | Out-Null
& $venvPython -m pip install -r requirements.txt
if($LASTEXITCODE -ne 0){ ErrExit 'pip install failed. Check errors above.' }

# Create DB from schema.sql
if(-not (Test-Path 'estoque_tabacaria.db')){
    Write-Host 'Creating SQLite database (estoque_tabacaria.db) from schema.sql' -ForegroundColor Yellow
    & $venvPython - <<'PY'
import sqlite3
conn = sqlite3.connect('estoque_tabacaria.db')
with open('schema.sql','r',encoding='utf-8') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print('DB criado com sucesso')
PY
} else { Write-Host 'estoque_tabacaria.db already exists, skipping DB creation.' }

# Create static dirs
Write-Host 'Ensuring static directories exist...' -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "static\barcodes" | Out-Null
New-Item -ItemType Directory -Force -Path "static\Images" | Out-Null

# Move logo if present in Templates
$tplLogo = Join-Path 'Templates' 'Logo_tabacaria.png'
$destLogo = Join-Path 'static\Images' 'Logo_tabacaria.png'
if(Test-Path $tplLogo){
    Write-Host "Found logo at $tplLogo. Moving to $destLogo" -ForegroundColor Green
    Move-Item -Force $tplLogo $destLogo
} elseif(Test-Path 'Logo_tabacaria.png'){
    Write-Host 'Found Logo_tabacaria.png in project root, moving to static\Images' -ForegroundColor Green
    Move-Item -Force 'Logo_tabacaria.png' $destLogo
} else {
    Write-Host 'No logo found in Templates/ or project root. Please place Logo_tabacaria.png in static\Images when available.' -ForegroundColor Yellow
}

Write-Host "\nSetup finished. To run the app:" -ForegroundColor Cyan
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "python app.py" -ForegroundColor Green

if($StartApp){
    Write-Host 'Starting the application...' -ForegroundColor Cyan
    & $venvPython app.py
}
