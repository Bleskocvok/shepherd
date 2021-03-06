
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

    def get_time(self):
        now = self.now()
        return '{}:{}'.format(now[0], str(now[1]).rjust(2, '0'))

    def now(self):
        t = datetime.now().time()
        return ((t.hour + self.timezone) % 24, t.minute)

    def _run(self):
        last = (-1, -1)
        while self.running:
            now = self.now()
            lh, lm = last
            if lm != now[0] and lm != now[1]:
                for ID, entry in self.scheduled.items():
                    t, job = entry
                    h, m = t
                    if now[0] == h and now[1] == m:
                        job(ID)
            last = (now[0], now[1])
            # sleep for x seconds
            time.sleep(self.granularity)


