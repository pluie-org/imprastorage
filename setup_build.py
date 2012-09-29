import sys
from cx_Freeze import setup, Executable

productName = "ImpraStorage"

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","subprocess","importlib","platform"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
#    base = "Win32GUI"






if 'bdist_msi' in sys.argv:
    sys.argv += ['--initial-target-dir', 'C:\InstallDir\\' + productName]
    sys.argv += ['--install-script', 'install.py']

    exe = Executable(
            script="imprastorage.py",
            base=None,
            targetName="ImpraStorage.exe",
            targetDir="lib",
            shortcutName="ImpraStorage",
        )
    setup(
            name="ImpraStorage.exe",
            version="0.6",
            author="a-Sansara",
            description="ImpraStorage provided a  private imap access to store large files. License GNU GPLv3 Copyright 2012 pluie.org",
            executables=[exe],
            include-files=('./launcher.bat','./launcher.bat')
            scripts=[
                'install.py'
                ]
            ) 
else :

	setup(  name = "ImpraStorage",
	        version = "0.5",
	        description = "mpraStorage provided a  private imap access to store large files",
	        options = {"build_exe": build_exe_options},
	        executables = [Executable("imprastorage.py", base=base)])
