@echo off
chcp 65001 >nul
echo ========================================
echo 📅 AGENDADOR DE BACKUP AUTOMÁTICO
echo ========================================
echo.

echo Este script criará uma tarefa agendada no Windows
echo para executar backups automáticos diariamente.
echo.

set /p HORA="Digite a hora para o backup diário (0-23): "
set /p MINUTO="Digite o minuto (0-59): "

echo.
echo Criando tarefa agendada...
echo.

REM Obtém o diretório atual
set CURRENT_DIR=%cd%

REM Cria tarefa agendada
schtasks /create /tn "Backup_Gestao_Financeira" /tr "%CURRENT_DIR%\executar_backup.bat" /sc daily /st %HORA%:%MINUTO% /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ TAREFA CRIADA COM SUCESSO!
    echo ========================================
    echo.
    echo 📅 Backup será executado diariamente às %HORA%:%MINUTO%
    echo.
    echo Para gerenciar a tarefa:
    echo - Abra o "Agendador de Tarefas" do Windows
    echo - Procure por "Backup_Gestao_Financeira"
    echo.
    echo Para remover a tarefa:
    echo   schtasks /delete /tn "Backup_Gestao_Financeira" /f
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ ERRO AO CRIAR TAREFA
    echo ========================================
    echo.
    echo Execute este arquivo como Administrador!
    echo.
)

pause