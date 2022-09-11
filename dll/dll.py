import ctypes

from common import *


def load_dll(name: str) -> ctypes.CDLL:
    """
    加载动态链接库。
    """
    if os.name == 'nt':
        return ctypes.CDLL(get_res('dlls', name+'.dll'), winmode=0)
    else:
        return ctypes.cdll.LoadLibrary(get_res('dlls', name+'.so'))
