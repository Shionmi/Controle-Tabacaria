@echo off
echo Iniciando Sistema de Controle de Tabacaria...
start /min powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0scripts\start_sistema.ps1"
exit