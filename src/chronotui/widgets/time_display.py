from time import monotonic
from textual.widgets import Digits
from textual.reactive import reactive
import logging

logger = logging.getLogger(__name__)

class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)
        logger.debug("TimeDisplay mounted and timer set.")

    def update_time(self) -> None:
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        self.start_time = monotonic()
        self.update_timer.resume()
        logger.info("Stopwatch started.")

    def stop(self):
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total
        logger.info("Stopwatch stopped.")

    def reset(self):
        self.total = 0
        self.time = 0
        logger.info("Stopwatch reset.")
