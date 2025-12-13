@echo off
chcp 65001 >nul

echo ========================================
echo 🔐 BACKUP AUTOMÁTICO - Gestão Financeira
echo ========================================
echo.

REM ---------------------------------------------------------
REM 1. Ir para a pasta correta do projeto
REM ---------------------------------------------------------
cd /d "C:\Users\kleiv\Music\App - Simplifica Finanças"

REM ---------------------------------------------------------
REM 2. Ativar o ambiente virtual
REM ---------------------------------------------------------
if exist ".venv\Scripts\activate.bat" (
    echo 🔄 Ativando ambiente virtual...
    call ".venv\Scripts\activate.bat"
) else (
    echo ⚠️ Ambiente virtual NÃO encontrado!
)

echo.
echo 📦 Iniciando backup automático...
echo.

REM ---------------------------------------------------------
REM 3. Executar o script de backup
REM ---------------------------------------------------------
python "backup_automatico.py" --auto

echo.
echo ========================================
echo ✅ PROCESSO CONCLUÍDO
echo ========================================
echo.

pause
