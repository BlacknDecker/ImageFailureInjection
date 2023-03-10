import time


# Source: https://stackoverflow.com/a/5849861
class TimerOneLine(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print(f"[{self.name}] - Elapsed: {time.time() - self.tstart} seconds")
        else:
            print(f"Elapsed: {time.time() - self.tstart} seconds")

