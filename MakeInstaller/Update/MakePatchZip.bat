:: Make Patch Files and compress to zip file
rd /s /q .\Patch

python ..\Compile.py
xcopy /s ..\Compile\*.*  .\Patch\*.*
rd /s /q ..\Compile

xcopy /s ..\..\Resource\*.*     .\Patch\Resource\*.*

python .\CompressPatch.py

pause