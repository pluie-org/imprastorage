@echo off
TITLE ImpraStorage (GNU GPLv3)
set cmd=''
set /P cmd=imprastorage %=%
set acmd=%cmd:"='%
imprastorage.exe %cmd%
cmd.bat
