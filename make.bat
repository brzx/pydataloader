@echo off

pushd %~dp0

echo Command file for building iLoad

python setupMain.py py2exe

echo make executable file finish

xcopy "logging.json" .\dist /I/D/Y
xcopy "Issue List.txt" .\dist /I/D/Y
xcopy "html" .\dist\html /I/D/Y/E

del /F/S/Q build
rd /S/Q build

python rename.py

cd makelib
python makelib.py

cd ..
python mvlib.py

echo build finish

goto end

:help

:end
popd
