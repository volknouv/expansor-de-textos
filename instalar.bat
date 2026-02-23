@echo off
:: Altera a pagina de codigos para UTF-8 para exibir acentos corretamente
chcp 65001 >nul

echo ===================================================
echo   Configurando o Expansor de Textos...
echo ===================================================

:: Captura o caminho absoluto da pasta atual
set "BASE_DIR=%~dp0"
:: Nome especifico para o venv para evitar conflitos
set "VENV_DIR=%BASE_DIR%venv_expansor"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "SCRIPT_PY=%BASE_DIR%expansor.py"

echo.
echo [1/4] Criando o ambiente virtual (venv_expansor)...
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
echo [4/4] Criando o desinstalar.bat ...

:: Criando desinstalar.bat
echo @echo off > "%BASE_DIR%desinstalar.bat"
echo chcp 65001 ^>nul >> "%BASE_DIR%desinstalar.bat"
echo echo =================================================== >> "%BASE_DIR%desinstalar.bat"
echo echo   Desinstalando o Expansor de Textos... >> "%BASE_DIR%desinstalar.bat"
echo echo =================================================== >> "%BASE_DIR%desinstalar.bat"
echo echo. >> "%BASE_DIR%desinstalar.bat"
echo echo Parando processos em segundo plano... >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0stop.bat" call "%%~dp0stop.bat" >> "%BASE_DIR%desinstalar.bat"
echo echo. >> "%BASE_DIR%desinstalar.bat"
echo echo Removendo todos os arquivos do projeto... >> "%BASE_DIR%desinstalar.bat"

:: Deleta os arquivos do projeto original
echo if exist "%%~dp0expansor.py" del /f /q "%%~dp0expansor.py" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0requirements.txt" del /f /q "%%~dp0requirements.txt" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0modelos.json" del /f /q "%%~dp0modelos.json" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0.gitignore" del /f /q "%%~dp0.gitignore" >> "%BASE_DIR%desinstalar.bat"

:: Deleta o proprio instalar.bat
echo if exist "%%~dp0instalar.bat" del /f /q "%%~dp0instalar.bat" >> "%BASE_DIR%desinstalar.bat"

:: Deleta os arquivos .bat gerados
echo if exist "%%~dp0start.bat" del /f /q "%%~dp0start.bat" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0stop.bat" del /f /q "%%~dp0stop.bat" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0status.bat" del /f /q "%%~dp0status.bat" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0set.bat" del /f /q "%%~dp0set.bat" >> "%BASE_DIR%desinstalar.bat"

:: Remove a pasta do venv e o cache do python
echo if exist "%%~dp0venv_expansor" rd /s /q "%%~dp0venv_expansor" >> "%BASE_DIR%desinstalar.bat"
echo if exist "%%~dp0__pycache__" rd /s /q "%%~dp0__pycache__" >> "%BASE_DIR%desinstalar.bat"

:: O truque magico DEFINITIVO para apagar a si mesmo sem falhas
echo echo Limpeza concluida. O desinstalador se auto-destruira agora. >> "%BASE_DIR%desinstalar.bat"
echo timeout /t 2 /nobreak ^>nul >> "%BASE_DIR%desinstalar.bat"
echo (goto) 2^>nul ^& del "%%~f0" >> "%BASE_DIR%desinstalar.bat"

echo.
echo ===================================================
echo   Tudo pronto! 
echo ===================================================
pause
