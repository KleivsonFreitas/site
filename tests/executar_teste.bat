@echo off
chcp 65001 >nul
echo ========================================
echo 🧪 EXECUTANDO TESTES AUTOMATIZADOS
echo ========================================
echo.

REM Ativa ambiente virtual se existir
if exist .venv\Scripts\activate.bat (
    echo 🔄 Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
)

echo.
echo 📋 Executando 15 testes automatizados...
echo.

python tests\test_app.py

echo.
echo ========================================
echo ✅ EXECUÇÃO CONCLUÍDA
echo ========================================
echo.
pause