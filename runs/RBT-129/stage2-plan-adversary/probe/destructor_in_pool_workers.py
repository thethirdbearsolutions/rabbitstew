import ctypes, os, sys
from concurrent.futures import ProcessPoolExecutor
L = ctypes.CDLL(os.path.abspath("libdestructor.so"))
def job(i):
    L.work(); return os.getpid()
if __name__ == "__main__":
    L.work()
    with ProcessPoolExecutor(2) as p:
        print(sorted(set(p.map(job, range(10)))))
