@echo off
for /r %%F in (*.ui) do (
  python -m PyQt6.uic.pyuic "%%F" -o "%%~dpnF.py"
)
for /r %%F in (*.qrc) do (
  pyside6-rcc "%%F" | sed "0,/PySide6/s//PyQt6/" > "%%~dpnF.py"
)