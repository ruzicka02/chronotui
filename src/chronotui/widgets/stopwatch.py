from textual.containers import HorizontalGroup
from textual.widgets import Button, Label
from widgets.time_display import TimeDisplay
import logging

logger = logging.getLogger(__name__)

class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def __init__(self, name: str = None) -> None:
        super().__init__()
        self.sw_name = name or "Stopwatch"
        self._label_widget = None

    def compose(self):
        label = Label(self.sw_name, id="sw-name")
        self._label_widget = label
        yield label
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()

    def set_name(self, new_name: str) -> None:
        self.sw_name = new_name
        if self._label_widget is not None:
            self._label_widget.update(new_name)
        logger.info(f"Stopwatch renamed to: {new_name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app = self.app
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.start()
            self.add_class("started")
            logger.debug(f"Start pressed for {self.sw_name}")
        elif button_id == "stop":
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.stop()
            self.remove_class("started")
            logger.debug(f"Stop pressed for {self.sw_name}")
        elif button_id == "reset":
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.reset()
            logger.debug(f"Reset pressed for {self.sw_name}")
