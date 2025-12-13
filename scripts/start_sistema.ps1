# Script para iniciar o sistema
$ErrorActionPreference = 'Stop'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appRoot = Split-Path -Parent $scriptPath

# --- CONFIGURAÇÃO DO NGROK (ACESSO PÚBLICO) ---
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CONFIGURAÇÃO DE ACESSO REMOTO (ngrok)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ngrokConfigFile = "$appRoot\.ngrok_token"

# Verificar se já tem token salvo
if (-not (Test-Path $ngrokConfigFile)) {
    Write-Host "Para permitir acesso pelo celular de qualquer lugar," -ForegroundColor Yellow
    Write-Host "precisamos configurar o ngrok (tunnel publico)." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "PASSO 1: Acesse https://dashboard.ngrok.com/signup" -ForegroundColor White
    Write-Host "PASSO 2: Crie uma conta gratuita (pode usar GitHub)" -ForegroundColor White
    Write-Host "PASSO 3: Copie seu authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host ""
    
    $token = Read-Host "Cole aqui seu ngrok authtoken"
    
    if ($token -and $token.Trim() -ne "") {
        # Salvar token em arquivo oculto
        $token.Trim() | Out-File -FilePath $ngrokConfigFile -Encoding utf8
        Write-Host ""
        Write-Host "Token salvo com sucesso!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Token nao fornecido. Sistema funcionara apenas localmente." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    $token = Get-Content $ngrokConfigFile -Raw
    $token = $token.Trim()
    Write-Host "Token ngrok ja configurado!" -ForegroundColor Green
    Write-Host ""
}

# Configurar ngrok se tiver token
if ($token -and $token.Trim() -ne "") {
    Write-Host "Configurando ngrok..." -ForegroundColor Cyan
    try {
        & "$appRoot\.venv\Scripts\ngrok.exe" config add-authtoken $token 2>&1 | Out-Null
        Write-Host "Ngrok configurado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "Aviso: Erro ao configurar ngrok: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- FIREWALL CHECK ---
$ruleName = "JM Tabacaria Port 5000"
$rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if (-not $rule) {
    Write-Host "Liberando acesso no Firewall..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Any -ErrorAction Stop | Out-Null
        Write-Host "Firewall configurado!" -ForegroundColor Green
    } catch {
        Write-Host "AVISO: Execute como Administrador para liberar o acesso mobile." -ForegroundColor Yellow
    }
}

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
    Write-Host ""
    Write-Host "Sistema já está rodando!" -ForegroundColor Green
    
    # Obter IP mesmo se já estiver rodando
    try {
        $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual' } | Where-Object { $_.IPAddress -notmatch '^169\.254\.' -and $_.IPAddress -notmatch '^127\.' } | Select-Object -ExpandProperty IPAddress | Select-Object -First 1
        if (-not $ip) {
            $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^127\.' } | Select-Object -ExpandProperty IPAddress | Select-Object -First 1
        }
    } catch {
        $ip = "127.0.0.1"
    }
    if (-not $ip) { $ip = "127.0.0.1" }
    
    Write-Host ""
    Write-Host "ACESSE NO CELULAR:" -ForegroundColor Yellow
    Write-Host "http://$($ip):5000" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "Pressione qualquer tecla para fechar..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
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
    # Obter IP Local (Método mais robusto)
    try {
        # Tenta obter o IP da interface que tem gateway padrão (internet/rede local)
        $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual' } | Where-Object { $_.IPAddress -notmatch '^169\.254\.' -and $_.IPAddress -notmatch '^127\.' } | Select-Object -ExpandProperty IPAddress | Select-Object -First 1
        
        if (-not $ip) {
            # Fallback: pega o primeiro IP não-loopback
            $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^127\.' } | Select-Object -ExpandProperty IPAddress | Select-Object -First 1
        }
    } catch {
        $ip = "127.0.0.1"
    }

    if (-not $ip) { $ip = "127.0.0.1" }

    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "   JM TABACARIA - SISTEMA INICIADO" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "Acesse no PC: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ACESSE NO CELULAR:" -ForegroundColor Yellow
    Write-Host "http://$($ip):5000" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANTE: Celular e PC devem estar no MESMO Wi-Fi!" -ForegroundColor Yellow
    Write-Host "Se nao funcionar, execute este arquivo como ADMINISTRADOR" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Mantenha esta janela aberta enquanto usa o sistema." -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para fechar." -ForegroundColor Cyan
    Write-Host ""

    # Tentar abrir como App no Chrome
    $chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    $chromePath86 = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if (Test-Path $chromePath) {
        Start-Process $chromePath -ArgumentList "--app=http://localhost:5000"
    } elseif (Test-Path $chromePath86) {
        Start-Process $chromePath86 -ArgumentList "--app=http://localhost:5000"
    } else {
        Start-Process "http://localhost:5000"
    }

    # Manter o script rodando
    Write-Host "Servidor rodando..." -ForegroundColor Green
    while ($true) {
        Start-Sleep -Seconds 60
    }
} else {
    Write-Host "ERRO: O servidor não respondeu a tempo." -ForegroundColor Red
    [System.Windows.Forms.MessageBox]::Show(
        "Erro ao iniciar o servidor. Por favor, tente novamente ou contate o suporte.",
        "Erro de Inicialização",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    if ($pythonProcess) { Stop-Process -Id $pythonProcess.Id -Force }
    exit 1
}