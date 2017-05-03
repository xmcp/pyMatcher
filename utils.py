from contextlib import contextmanager
import tempfile
import os
import sys
import ctypes

class TempFile:
    def __init__(self,prefix='',suffix='',content=''):
        fd,self.name=tempfile.mkstemp(suffix=suffix,prefix=prefix,text=False)
        os.write(fd,content.encode('utf-8'))
        os.close(fd)
        
    def __del__(self):
        os.remove(self.name)
        
@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)
    
# http://stackoverflow.com/questions/24130623/using-python-subprocess-popen-cant-prevent-exe-stopped-working-prompt
def _setup_windows():
    if sys.platform.startswith("win"):
        SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
        CREATE_NO_WINDOW = 0x08000000    # From Windows API
        return CREATE_NO_WINDOW
    else:
        return 0
        
subprocess_flags=_setup_windows()