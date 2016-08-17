import ctypes
from ctypes.util import find_library


utils = ctypes.cdll.LoadLibrary('./libutils.so')

factorial = utils.factorial
factorial.argtypes = (ctypes.c_int,)
factorial.restype = ctypes.c_int

_swap  = utils.swap
_swap.argtypes = (ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))


def swap(x, y):
    a = ctypes.c_int(x)
    b = ctypes.c_int(y)
    _swap(a, b)
    return a.value, b.value


if __name__ == "__main__":
    # 直接调用c的printf
    clib = ctypes.cdll.LoadLibrary(find_library('c'))
    clib.printf(b'hello world\n')

    print('factorial of 4 is %s !' % factorial(4))
    print('factorial of 5 is %s !' % factorial(5))

    x, y = 10, 20
    print('x is %s and y is %s' % (x, y))
    x, y = swap(x, y)
    print('after swap')
    print('x is %s and y is %s' % (x, y))
