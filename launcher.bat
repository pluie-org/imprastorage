@Echo Off
Set _Title=ImpraStorage 
Set _Height=60
Set _Width=122
Set _BHeight=5000
Set _BWidth=%_Width%
Set _xPos=0
Set _yPos=0
Set _Color=1E
Set /A _BufferSize=_BHeight*0x10000+_BWidth
Set /A _WindowPos=_yPos*0x10000+_xPos
Set /A _WindowSize=_Height*0x10000+_Width
Set _Cmd=Title ^&Prompt ^&Color 0F^&ImpraStorage.exe --run
Call :_OpenCP %_BufferSize% %_Color% %_WindowPos% %_WindowSize% "%_Title%" "%_CMD%"
Goto :EOF
:_OpenCP
Reg Add "HKCU\Console\%~5" /V ScreenBufferSize /T REG_DWORD /D %1 /F
Reg Add "HKCU\Console\%~5" /V ScreenColors /T REG_DWORD /D 0x%2 /F
Reg Add "HKCU\Console\%~5" /V WindowPosition /T REG_DWORD /D %3 /F
Reg Add "HKCU\Console\%~5" /V WindowSize /T REG_DWORD /D %4 /F
Start "%~5" %COMSPEC% /K %6
exit