# Script para iniciar o sistema
$ErrorActionPreference = 'Stop'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appRoot = Split-Path -Parent $scriptPath

# Ativar ambiente virtual
. "$appRoot\.venv\Scripts\Activate.ps1"

# Iniciar o servidor
Start-Process python -ArgumentList "$appRoot\app.py" -WindowStyle Hidden

# Aguardar servidor iniciar
Start-Sleep -Seconds 2

# Abrir navegador
Start-Process "http://127.0.0.1:5000"