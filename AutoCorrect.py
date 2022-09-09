from ctypes import *



listToArray = lambda li: (c_double*len(li))(*li)


arrayToList = lambda array,length: [array[i] for i in range   (0, length)]