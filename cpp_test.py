import ctypes

from sources.common import *


def call(li):
    print('Loading DLL...', end='')
    dll = load_dll('test')
    print('OK')

    print('Converting the list to an array...', end='')
    arr = (ctypes.c_int*len(li))(*li)
    print('OK')

    print('Reversing the array with the DLL...', end='')
    dll.rev(len(li), arr)
    print('OK')

    return list(arr)


if __name__ == '__main__':
    while True:
        user_inp = input('Enter some numbers separated by spaces: ')
        li = list(map(int, user_inp.split()))
        print('The numbers in reverse order are:', *call(li))
