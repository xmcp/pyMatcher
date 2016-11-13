import sys
import os,shutil
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

print('===== CLEANING UP =====')

shutil.copyfile('matcher.pyw','build/exe.win32-3.4/matcher.pyw')
shutil.copytree('tkdnd2.8','build/exe.win32-3.4/tkdnd2.8')

os.remove('build/exe.win32-3.4/unicodedata.pyd')
os.remove('build/exe.win32-3.4/_hashlib.pyd')
shutil.rmtree('build/exe.win32-3.4/tcl/encoding')
shutil.rmtree('build/exe.win32-3.4/tcl/tzdata')
shutil.rmtree('build/exe.win32-3.4/tcl/msgs')
shutil.rmtree('build/exe.win32-3.4/tk/demos')
shutil.rmtree('build/exe.win32-3.4/tk/images')
shutil.rmtree('build/exe.win32-3.4/tk/msgs')

os.rename('build/exe.win32-3.4','build/pyMatcher-exe.win32-3.4')

print('===== DONE =====')
