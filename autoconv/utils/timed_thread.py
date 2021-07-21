from threading import Thread
from time import sleep


class TimedThread(Thread):
    def __init__(self, seconds, *args, **kwargs):
        super(TimedThread, self).__init__(*args, **kwargs)
        self._alive = True
        self.waiting_seconds = seconds
        self.is_dead = False

    def __str__(self):
        return f"TimedThread({self.waiting_seconds}):{self.name}"

    def stop(self):
        self._alive = False

    def run(self):
        for _ in range(self.waiting_seconds * 10):
            if not self._alive:
                return
            sleep(0.1)
        super().run()
        self.is_dead = True
