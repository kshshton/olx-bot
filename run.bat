@echo off

for /f "tokens=1,* delims==" %%a in ('type .env') do set "%%a=%%b"

call "%VENV_PATH%\Scripts\activate.bat"

cd %BOT_FOLDER_PATH%
cd src

python main.py

deactivate

exit