@echo off
title JM Tabacaria - Sistema de Gestao
mode con: cols=80 lines=30
color 0B
cls

echo.
echo ========================================================================
echo.
echo                    **  JM TABACARIA  **
echo                   Sistema de Controle
echo.
echo ========================================================================
echo.
echo              Bem-vindo ao sistema de gestao!
echo.
echo   Este programa vai preparar tudo automaticamente.
echo   Aguarde enquanto fazemos a configuracao...
echo.
echo ========================================================================
echo.

timeout /t 2 /nobreak >nul

:: Verificar se ja esta instalado
if exist ".venv\" (
    echo [OK] Sistema ja configurado anteriormente.
    echo.
    goto :INICIAR
)

echo ========================================================================
echo                    PRIMEIRA CONFIGURACAO
echo ========================================================================
echo.
echo   Precisamos instalar alguns componentes.
echo   Isso acontece apenas na PRIMEIRA vez.
echo.
echo   Pode levar alguns minutos...
echo   Por favor, aguarde.
echo.
echo ========================================================================
echo.

:: Verificar admin para primeira instalacao
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    cls
    echo.
    echo ========================================================================
    echo                        ATENCAO IMPORTANTE!
    echo ========================================================================
    echo.
    echo   Para a primeira instalacao, e necessario permissao de Administrador.
    echo.
    echo   FECHE esta janela e faca o seguinte:
    echo.
    echo   1. Clique com o botao DIREITO neste arquivo
    echo   2. Escolha "Executar como administrador"
    echo   3. Clique em SIM quando o Windows perguntar
    echo.
    echo ========================================================================
    echo.
    pause
    exit /b 1
)

:: Configurar permissoes
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force" >nul 2>&1

:: Executar instalacao
echo   Instalando componentes...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\setup_client.ps1"

if %errorLevel% neq 0 (
    color 0C
    echo.
    echo ========================================================================
    echo                           ERRO NA INSTALACAO
    echo ========================================================================
    echo.
    echo   Algo deu errado durante a instalacao.
    echo   Entre em contato com o suporte tecnico.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Instalacao concluida com sucesso!
echo.

:INICIAR
echo ========================================================================
echo                        INICIANDO SISTEMA
echo ========================================================================
echo.
echo   O sistema vai abrir em alguns segundos...
echo   Uma janela azul vai aparecer com o endereco para acessar pelo celular.
echo.
echo   IMPORTANTE: Mantenha esta janela aberta enquanto usa o sistema!
echo.
echo ========================================================================
echo.

timeout /t 3 /nobreak >nul

:: Iniciar o sistema
start "JM Tabacaria - Servidor" powershell -ExecutionPolicy Bypass -NoExit -Command "cd '%~dp0'; .\.venv\Scripts\Activate.ps1; cls; Write-Host ''; Write-Host '========================================================================' -ForegroundColor Green; Write-Host '                    JM TABACARIA - SISTEMA ATIVO' -ForegroundColor Green; Write-Host '========================================================================' -ForegroundColor Green; Write-Host ''; Write-Host '  O sistema esta funcionando!' -ForegroundColor Cyan; Write-Host ''; Write-Host '  MANTENHA ESTA JANELA ABERTA enquanto usa o sistema.' -ForegroundColor Yellow; Write-Host '  Para fechar, pressione Ctrl+C ou feche esta janela.' -ForegroundColor Yellow; Write-Host ''; Write-Host '========================================================================' -ForegroundColor Green; Write-Host ''; python app.py"

timeout /t 2 /nobreak >nul
cls
echo.
echo ========================================================================
echo                      SISTEMA INICIADO!
echo ========================================================================
echo.
echo   O navegador vai abrir automaticamente.
echo   Uma janela AZUL mostra o endereco para acessar pelo celular.
echo.
echo   Para FECHAR o sistema:
echo   - Feche a janela azul (PowerShell)
echo   - Ou pressione Ctrl+C na janela azul
echo.
echo   Voce pode fechar ESTA janela agora.
echo.
echo ========================================================================
echo.
pause
exit
