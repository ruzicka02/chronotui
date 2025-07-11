"""
Time tracking app. Originally inspired from https://textual.textualize.io/tutorial/
"""

from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        app = self.app
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            # If not selected, select this stopwatch first
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            if hasattr(app, "selected_stopwatch") and app.selected_stopwatch is not self:
                app.select_stopwatch(self)
            time_display.reset()

    def __init__(self, name: str = None) -> None:
        super().__init__()
        self.sw_name = name or "Stopwatch"
        self._label_widget = None

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        from textual.widgets import Label
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


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("m", "toggle_dark", "Mode (dark/light)"),
        ("a", "add_stopwatch", "Add"),
        ("d", "delete_stopwatch", "Delete selected"),
        ("r", "reset_selected", "Reset selected"),
        ("c", "change_name", "Change timer name"),
        ("q", "quit", "Quit"),
        ("up", "select_up", "Select Up"),
        ("down", "select_down", "Select Down"),
        ("j", "select_down", "Select Down"),
        ("k", "select_up", "Select Up"),
        ("space", "toggle_selected", "Start/Stop Selected"),
    ]
    async def action_change_name(self) -> None:
        """Open a dialog to change the selected stopwatch's name."""
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        from textual.widgets import Input
        from textual.containers import Center
        from textual.screen import ModalScreen


        class NameInputScreen(ModalScreen[str]):
            def compose(self) -> ComposeResult:
                # Pre-fill with current name
                yield Center(Input(value=self.app.selected_stopwatch.sw_name, placeholder="Enter new name", id="name-input"))

            def on_input_submitted(self, event: Input.Submitted) -> None:
                self.dismiss(event.value)

        # Show modal and get result
        new_name = await self.push_screen(NameInputScreen())
        if new_name is not None and new_name.strip():
            self.selected_stopwatch.set_name(new_name)
    def action_reset_selected(self) -> None:
        """Reset the selected stopwatch."""
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        sw = self.selected_stopwatch
        time_display = sw.query_one(TimeDisplay)
        time_display.reset()
        sw.remove_class("started")
    def action_toggle_selected(self) -> None:
        """Start or stop the selected stopwatch with spacebar."""
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        sw = self.selected_stopwatch
        time_display = sw.query_one(TimeDisplay)
        if "started" in sw.classes:
            time_display.stop()
            sw.remove_class("started")
        else:
            time_display.start()
            sw.add_class("started")
    def action_select_up(self) -> None:
        """Select the previous stopwatch in the list."""
        timers = list(self.query("Stopwatch"))
        if not timers or not hasattr(self, "selected_stopwatch"):
            return
        try:
            idx = timers.index(self.selected_stopwatch)
        except ValueError:
            return
        if idx > 0:
            self.select_stopwatch(timers[idx - 1])

    def action_select_down(self) -> None:
        """Select the next stopwatch in the list."""
        timers = list(self.query("Stopwatch"))
        if not timers or not hasattr(self, "selected_stopwatch"):
            return
        try:
            idx = timers.index(self.selected_stopwatch)
        except ValueError:
            return
        if idx + 1 < len(timers):
            self.select_stopwatch(timers[idx + 1])

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        # Create stopwatches and select the first one by default
        sw1 = Stopwatch("Stopwatch 1")
        sw2 = Stopwatch("Stopwatch 2")
        sw3 = Stopwatch("Stopwatch 3")
        self.selected_stopwatch = sw1
        sw1.add_class("selected")
        yield VerticalScroll(sw1, sw2, sw3, id="timers")

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        # Name as "Stopwatch N" where N is next available number
        timers = list(self.query("Stopwatch"))
        new_name = f"Stopwatch {len(timers) + 1}"
        new_stopwatch = Stopwatch(new_name)
        self.query_one("#timers").mount(new_stopwatch)
        self.select_stopwatch(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_delete_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            to_remove = self.selected_stopwatch if hasattr(self, "selected_stopwatch") else timers.last()
            next_selected = None
            # Try to select previous, or next, or None
            for sw in timers:
                if sw is to_remove:
                    break
                next_selected = sw
            if not next_selected:
                # If no previous, try next
                idx = list(timers).index(to_remove)
                if idx + 1 < len(timers):
                    next_selected = list(timers)[idx + 1]
            to_remove.remove()
            if next_selected:
                self.select_stopwatch(next_selected)
            else:
                self.selected_stopwatch = None
    def select_stopwatch(self, stopwatch: Stopwatch) -> None:
        """Select the given stopwatch and update visual state."""
        # Remove 'selected' class from all
        for sw in self.query("Stopwatch"):
            sw.remove_class("selected")
        stopwatch.add_class("selected")
        self.selected_stopwatch = stopwatch

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()