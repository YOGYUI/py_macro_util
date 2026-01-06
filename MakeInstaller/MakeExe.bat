set PROJ_NAME=MACRO

:: Remove existing build result
rd /s /q .\dist
rd /s /q .\build

python file_version_info.py
pyinstaller.exe MakeExe.spec
:: Compile
python Compile.py

:: Copy Core Files
xcopy /s .\Compile\*.*      .\dist\%PROJ_NAME%\
xcopy /s ..\Resource\*.*    .\dist\%PROJ_NAME%\Resource\

:: Remove existing core files
rd /s /q .\Compile

pause
