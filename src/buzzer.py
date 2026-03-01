import os
import ctypes

lib = ctypes.CDLL("./libbuzzer_iopl.so")
lib.beep.argtypes = [ctypes.c_int, ctypes.c_int]
lib.beep.restype = None

def beep(freq: int, duration_ms: int):
    if os.geteuid() != 0:
        raise PermissionError("Must be root to access I/O ports")
    lib.beep(freq, duration_ms)

if __name__ == "__main__":
    beep(2000, 500)
