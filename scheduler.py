
import time
from datetime import datetime
from threading import Thread


class Scheduler:
    def __init__(self):
        self.scheduled = {}
        self.running = True
        self.thread = None

    def add(self, ID, time, job):
        self.scheduled[ID] = (time, job)

    def remove(self, ID):
        self.scheduled.pop(ID)

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
        self.thread = None

    def run(self):
        self.running = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self):
        last = (-1, -1)
        while self.running:
            now = datetime.now().time()
            lh, lm = last
            if lm != now.hour and lm != now.minute:
                for ID, entry in self.scheduled.items():
                    t, job = entry
                    h, m = t
                    if now.hour == h and now.minute == m:
                        job(ID)
            last = (now.hour, now.minute)
            # sleep for 30 seconds, finer granularity not needed
            time.sleep(30)


