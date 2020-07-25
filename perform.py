
# uses https://github.com/dbader/schedule
import schedule

import time
from threading import Thread

class Perform:
    def __init__(self):
        self._job = None
        th = Thread(target=self._run)
        th.start()

    def _run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def scheduler(self, time):
        self.cancel()
        return schedule.every().day.at(time).do

    def cancel(self):
        schedule.clear()

    def stop(self):
        pass

