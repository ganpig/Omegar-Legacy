@echo off
pipenv run pyinstaller Omegar.spec
move /y dist\Omegar.exe .
rd /s /q dist
rd /s /q build