import sys
from cx_Freeze import setup, Executable
build_exe_options = {"optimize": 2}
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'
executables = [Executable(script='matcher.pyw',
               base=base,
               targetName="pyMatcher.exe",
               compress=True)]
setup(name='pyMatcher',
      version='1.0',
      description='Python Matcher by xmcp',
      options = {"build_exe": build_exe_options},
      executables=executables)
