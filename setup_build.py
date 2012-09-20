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
            targetName="ImpraStorage.exe"
        )
    setup(
            name="ImpraStorage.exe",
            version="0.5",
            author="Me",
            description="Copyright 2012",
            executables=[exe],
            scripts=[
                'install.py'
                ]
            ) 
else :

	setup(  name = "ImpraStorage",
	        version = "0.5",
	        description = "ImpraStorage an imap private access storage",
	        options = {"build_exe": build_exe_options},
	        executables = [Executable("imprastorage.py", base=base)])
