import os, sys, time, signal, fcntl, subprocess
sys.path.insert(0, os.getcwd())
from rabbitstew.ecology import hold_run, RUN_LOCK
d = "/tmp/claude-0/lockprobe"; os.makedirs(d, exist_ok=True)
def held():
    r = subprocess.run([sys.executable, "-c", f"import fcntl,os;fd=os.open('{d}/{RUN_LOCK}',os.O_RDWR|os.O_CREAT);\ntry:\n fcntl.lockf(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);print('free')\nexcept OSError:print('held')"], capture_output=True, text=True)
    return r.stdout.strip()
# (b) same process: a second open+close of the lock file drops the lock
fd = hold_run(d, None); print("after hold_run:", held())
fd2 = os.open(os.path.join(d, RUN_LOCK), os.O_RDONLY); os.close(fd2); print("after an unrelated open+close in the holder:", held())
os.close(fd)
# same process: a second hold_run does not block
a = hold_run(d, None); t = time.time(); b = hold_run(d, None); print(f"second hold_run in same process returned in {time.time()-t:.3f}s (no exclusion)"); os.close(b); print("after closing the second:", held()); os.close(a)
# (a) a holder with forked children: SIGKILL the holder only, children survive
pid = os.fork()
if pid == 0:
    hold_run(d, None)
    kids = [os.fork() for _ in range(2)]
    if 0 in kids:
        time.sleep(30); os._exit(0)
    time.sleep(30); os._exit(0)
time.sleep(1); print("holder with forked children alive:", held())
os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0); time.sleep(0.2)
print("holder SIGKILLed, its forked children still alive:", held())
