import ctypes
from timeit import timeit


utils = ctypes.cdll.LoadLibrary('./libutils.so')

factorial = utils.factorial
factorial.argtypes = (ctypes.c_int,)
factorial.restype = ctypes.c_int

def py_factorial(n):
    assert isinstance(n, int)
    if n <= 0:
        return 1
    return py_factorial(n-1) * n

if __name__ == "__main__":
    number = 100000
    print('Python 版本100000次的factorial(10)时间')
    print(timeit('py_factorial(10)', number=number, globals=globals()))
    print('C 版本100000次的factorial(10)时间')
    print(timeit('factorial(10)', number=number, globals=globals()))

