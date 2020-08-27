
import time
from datetime import datetime
from threading import Thread


class Scheduler:
    def __init__(self, timezone : int = 0, granularity : int = 30):
        self.scheduled = {}
        self.running = True
        self.thread = None
        self.timezone = timezone
        self.granularity = granularity

    def add(self, ID, time, job):
        self.scheduled[ID] = (time, job)

    def remove(self, ID):
        if ID in self.scheduled:
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
                    if now.hour + self.timezone == h and now.minute == m:
                        job(ID)
            last = (now.hour, now.minute)
            # sleep for x seconds
            time.sleep(self.granularity)


