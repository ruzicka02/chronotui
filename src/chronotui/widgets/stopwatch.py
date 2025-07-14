import logging

from textual.containers import HorizontalGroup
from textual.widgets import Button, Label

from chronotui.widgets.time_display import TimeDisplay

logger = logging.getLogger(__name__)


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def __init__(self, name: str = None, time: float = 0.0, running: bool = False, active: bool = False) -> None:
        super().__init__()
        self.sw_name = name or "Stopwatch"
        self._label_widget = None
        self._init_time = time
        self._init_running = running
        self._init_active = active

    def compose(self):
        label = Label(self.sw_name, id="sw-name")
        self._label_widget = label
        yield label
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        td = TimeDisplay()
        yield td

        # Set initial state after mounting
        def _post_mount():
            try:
                td.set_time(self._init_time)
                if self._init_running:
                    self.add_class("started")
                    td.start()
                if self._init_active:
                    self.add_class("selected")
            except Exception as e:
                logger.warning(f"Failed to set initial state for stopwatch {self.sw_name}: {e}")

        self.call_after_refresh(_post_mount)

    def set_name(self, new_name: str) -> None:
        self.sw_name = new_name
        if self._label_widget is not None:
            self._label_widget.update(new_name)
        logger.info(f"Stopwatch renamed to: {new_name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app = self.app
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
            app.select_stopwatch(self)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
            logger.debug(f"Start pressed for {self.sw_name}")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
            logger.debug(f"Stop pressed for {self.sw_name}")
        elif button_id == "reset":
            time_display.reset()
            logger.debug(f"Reset pressed for {self.sw_name}")
