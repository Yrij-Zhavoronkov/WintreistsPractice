@echo off
call ..\venv\Scripts\activate
for %%F in (*.ui) do (
    python -m PyQt6.uic.pyuic "%%F" -o "%%~nF.py"
)
deactivate