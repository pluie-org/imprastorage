@Echo Off
:: This first title is used to store the registry setting
:: You can use it for the title of the First window, or change
:: The Title of both windows after opening
Set _Title=ImpraStorage
:: Set Height in lines, Width in characters. Buffer width is set
:: to the same value as the window width
Set _Height=60
Set _Width=122
Set _BHeight=5000
Set _BWidth=%_Width%
:: Set position of the Top left corner in pixels
:: Position is relative to the Top left corner of the screen
Set _xPos=0
Set _yPos=0
:: Color values are the same as for the Color command
Set _Color=1E
:: Calculate hex values needed in the registry
Set /A _BufferSize=_BHeight*0x10000+_BWidth
Set /A _WindowPos=_yPos*0x10000+_xPos
Set /A _WindowSize=_Height*0x10000+_Width
:: This command will be passed to the Prompt to change the Title and Prompt
:: The ampersand must be escaped
:: Set _Cmd=Title Send^&Prompt $T$G
:: Call :_OpenCP %_BufferSize% %_Color% %_WindowPos% %_WindowSize% "%_Title%" "%_CMD%"

:: Increase the _yPos value so 2nd window is below the first.
:: 12 is the height in pixels for the font being used.
:: 40 is a value to allow for the height of the Title Bar. Adjust as needed

::Set /A _yPos=_yPos+_Height*12+40
::Set /A _WindowPos=_yPos*0x10000+_xPos


:: 0 = Black  8 = Gray
:: 1 = Blue	  9 = Light Blue
:: 2 = Green  A = Light Green
:: 3 = Aqua   B = Light Aqua
:: 4 = Red    C = Light Red
:: 5 = Purple D = Light Purple
:: 6 = Yellow E = Light Yellow
:: 7 = White  F = Bright White

:: This command will be passed to the Prompt to change the Title, Prompt, and Color
Set _Cmd=Title ImpraStorage^&Prompt $T$G^&Color 0F
Call :_OpenCP %_BufferSize% %_Color% %_WindowPos% %_WindowSize% "%_Title%" "%_CMD%"
Goto :EOF
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Subroutines
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:_OpenCP
Reg Add "HKCU\Console\%~5" /V ScreenBufferSize /T REG_DWORD /D %1 /F
Reg Add "HKCU\Console\%~5" /V ScreenColors /T REG_DWORD /D 0x%2 /F
Reg Add "HKCU\Console\%~5" /V WindowPosition /T REG_DWORD /D %3 /F
Reg Add "HKCU\Console\%~5" /V WindowSize /T REG_DWORD /D %4 /F
Start "%~5" %COMSPEC% /K %6
:: Only one single command line is needed to receive user input
FOR /F "tokens=*" %%A IN ('TYPE CON') DO SET INPUT=%%A
:: Use quotes if you want to display redirection characters as well
ECHO You typed: "%INPUT%"
