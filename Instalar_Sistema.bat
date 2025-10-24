@echo off
echo ================================================
echo    Instalacao do Sistema Controle de Tabacaria
echo ================================================
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Executando como administrador... OK
) else (
    echo Por favor, execute este instalador como administrador!
    echo Clique com o botao direito e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

:: Permitir execução de scripts PowerShell
echo Configurando permissoes do PowerShell...
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force"

:: Executar script de instalação
echo Iniciando instalacao...
powershell -File "%~dp0scripts\setup_client.ps1" -StartApp

:: Se ocorrer algum erro, mostrar e esperar
if %errorLevel% neq 0 (
    echo.
    echo ERRO: A instalacao nao foi concluida corretamente.
    echo Por favor, entre em contato com o suporte.
    pause
    exit /b 1
)

exit /b 0