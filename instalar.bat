@echo off
:: Altera a página de códigos para UTF-8 para exibir acentos corretamente
chcp 65001 >nul

echo ===================================================
echo   Configurando o Super Expansor...
echo ===================================================

:: Captura o caminho absoluto da pasta atual onde o instalar.bat está
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "SCRIPT_PY=%BASE_DIR%expansor.py"

echo.
echo [1/3] Criando o ambiente virtual (venv)...
python -m venv "%VENV_DIR%"

echo.
echo [2/3] Instalando dependencias do requirements.txt...
"%PIP_EXE%" install -r "%BASE_DIR%requirements.txt"

echo.
echo [3/3] Criando os atalhos .bat com caminhos absolutos...

:: Criando start.bat
echo @echo off > "%BASE_DIR%start.bat"
echo "%PYTHON_EXE%" "%SCRIPT_PY%" start >> "%BASE_DIR%start.bat"
echo pause >> "%BASE_DIR%start.bat"

:: Criando stop.bat
echo @echo off > "%BASE_DIR%stop.bat"
echo "%PYTHON_EXE%" "%SCRIPT_PY%" stop >> "%BASE_DIR%stop.bat"
echo pause >> "%BASE_DIR%stop.bat"

:: Criando status.bat
echo @echo off > "%BASE_DIR%status.bat"
echo "%PYTHON_EXE%" "%SCRIPT_PY%" status >> "%BASE_DIR%status.bat"
echo pause >> "%BASE_DIR%status.bat"

:: Criando set.bat (sem pause para abrir direto a interface)
echo @echo off > "%BASE_DIR%set.bat"
echo start "" "%VENV_DIR%\Scripts\pythonw.exe" "%SCRIPT_PY%" set >> "%BASE_DIR%set.bat"

echo.
echo ===================================================
echo   Tudo pronto! 
echo   Os arquivos start.bat, stop.bat, status.bat e
echo   set.bat foram criados na sua pasta.
echo ===================================================
pause
