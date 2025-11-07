# Script para iniciar o sistema
$ErrorActionPreference = 'Stop'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appRoot = Split-Path -Parent $scriptPath

# Função para verificar se o servidor está respondendo
function Test-ServerResponse {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000" -UseBasicParsing -TimeoutSec 1
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Verificar se já está rodando
if (Test-ServerResponse) {
    Write-Host "Sistema já está rodando. Abrindo no navegador..."
    Start-Process "http://127.0.0.1:5000"
    exit 0
}

# Ativar ambiente virtual
try {
    . "$appRoot\.venv\Scripts\Activate.ps1"
} catch {
    [System.Windows.Forms.MessageBox]::Show(
        "Erro ao iniciar o sistema. Por favor, execute o Instalar_Sistema.bat primeiro.",
        "Erro de Inicialização",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Iniciar o servidor
$pythonProcess = Start-Process -FilePath "python" -ArgumentList "$appRoot\app.py" -WindowStyle Hidden -PassThru

# Aguardar servidor iniciar (máximo 30 segundos)
$maxAttempts = 30
$attempts = 0
do {
    Start-Sleep -Seconds 1
    $attempts++
    if ($attempts -eq 1) {
        Write-Host "Iniciando sistema..."
    }
} until ((Test-ServerResponse) -or ($attempts -ge $maxAttempts))

if (Test-ServerResponse) {
    # Abrir navegador
    Start-Process "http://127.0.0.1:5000"
} else {
    [System.Windows.Forms.MessageBox]::Show(
        "Erro ao iniciar o servidor. Por favor, tente novamente ou contate o suporte.",
        "Erro de Inicialização",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    if ($pythonProcess) { Stop-Process -Id $pythonProcess.Id -Force }
    exit 1
}