# Arquivo que contém comandos para serviço Windows
$ServiceName = "TabacariaEstoque"
$DisplayName = "Sistema de Controle de Tabacaria"
$Description = "Sistema de gestão de estoque para tabacaria"

# Caminho do executável e argumentos
$BinPath = "powershell.exe"
$Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSScriptRoot\start_sistema.ps1`""

# Criar novo serviço
New-Service -Name $ServiceName `
            -DisplayName $DisplayName `
            -Description $Description `
            -BinPath "$BinPath $Arguments" `
            -StartupType Automatic