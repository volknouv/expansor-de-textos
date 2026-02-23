@echo off
:: Altera a pagina de codigos para UTF-8 para exibir acentos corretamente
chcp 65001 >nul

echo ===================================================
echo   Configurando o Expansor de Textos...
echo ===================================================

:: Captura o caminho absoluto da pasta atual onde o instalar.bat esta
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "SCRIPT_PY=%BASE_DIR%expansor.py"

echo.
echo [1/4] Criando o ambiente virtual (venv)...
python -m venv "%VENV_DIR%"

echo.
echo [2/4] Instalando dependencias do requirements.txt...
"%PIP_EXE%" install -r "%BASE_DIR%requirements.txt"

echo.
echo [3/4] Criando os atalhos .bat com caminhos absolutos...

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

:: Criando set.bat
echo @echo off > "%BASE_DIR%set.bat"
echo start "" "%VENV_DIR%\Scripts\pythonw.exe" "%SCRIPT_PY%" set >> "%BASE_DIR%set.bat"

echo.
echo [4/4] Criando o desinstalar.bat (Kamikaze)...

:: Criando desinstalar.bat
echo @echo off > "%BASE_DIR%desinstalar.bat"
echo chcp 65001 ^>nul >> "%BASE_DIR%desinstalar.bat"
echo echo =================================================== >> "%BASE_DIR%desinstalar.bat"
echo echo   Desinstalando o Super Expansor... >> "%BASE_DIR%desinstalar.bat"
echo echo =================================================== >> "%BASE_DIR%desinstalar.bat"
echo echo. >> "%BASE_DIR%desinstalar.bat"
echo echo Parando processos em segundo plano... >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0stop.bat" call "%%~dp0stop.bat" >> "%BASE_DIR%desinstalar.bat"
echo echo. >> "%BASE_DIR%desinstalar.bat"
echo echo Apagando todos os arquivos, venv e a pasta base... >> "%BASE_DIR%desinstalar.bat"
echo cd /d "%%~dp0.." >> "%BASE_DIR%desinstalar.bat"
:: O comando abaixo cria um processo independente que espera 2 segundos e apaga a pasta inteira
echo start /b cmd /c "timeout /t 2 ^>nul ^& rd /s /q ""%%~dp0""" >> "%BASE_DIR%desinstalar.bat"
echo exit >> "%BASE_DIR%desinstalar.bat"

echo.
echo ===================================================
echo   Tudo pronto! 
echo ===================================================
pause
