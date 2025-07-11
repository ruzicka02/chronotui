import logging
from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Center
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Input
from chronotui.widgets.stopwatch import Stopwatch

logger = logging.getLogger(__name__)


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

    @work
    async def action_change_name(self) -> None:
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        logger.info(f"Name change requested for stopwatch: {self.selected_stopwatch.sw_name}")

        class NameInputScreen(ModalScreen[str]):
            def compose(self) -> ComposeResult:
                yield Center(
                    Input(value=self.app.selected_stopwatch.sw_name, placeholder="Enter new name", id="name-input")
                )

            def on_input_submitted(self, event: Input.Submitted) -> None:
                new_name = self.query_one(Input).value
                self.dismiss(new_name)

        new_name = await self.push_screen_wait(NameInputScreen())
        logger.info(f"Proposed name: {new_name}")

        if new_name is not None and new_name.strip():
            self.selected_stopwatch.set_name(new_name)
            logger.info(f"Stopwatch renamed to: {new_name}")

    def action_reset_selected(self) -> None:
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        sw = self.selected_stopwatch
        time_display = sw.query_one("TimeDisplay")
        time_display.reset()
        sw.remove_class("started")
        logger.info(f"Stopwatch reset: {sw.sw_name}")

    def action_toggle_selected(self) -> None:
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        sw = self.selected_stopwatch
        time_display = sw.query_one("TimeDisplay")
        if "started" in sw.classes:
            time_display.stop()
            sw.remove_class("started")
            logger.info(f"Stopwatch stopped: {sw.sw_name}")
        else:
            time_display.start()
            sw.add_class("started")
            logger.info(f"Stopwatch started: {sw.sw_name}")

    def action_select_up(self) -> None:
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
        yield Header()
        yield Footer()
        sw1 = Stopwatch("Stopwatch 1")
        sw2 = Stopwatch("Stopwatch 2")
        sw3 = Stopwatch("Stopwatch 3")
        self.selected_stopwatch = sw1
        sw1.add_class("selected")
        yield VerticalScroll(sw1, sw2, sw3, id="timers")

    def action_add_stopwatch(self) -> None:
        timers = list(self.query("Stopwatch"))
        new_name = f"Stopwatch {len(timers) + 1}"
        new_stopwatch = Stopwatch(new_name)
        self.query_one("#timers").mount(new_stopwatch)
        self.select_stopwatch(new_stopwatch)
        new_stopwatch.scroll_visible()
        logger.info(f"Stopwatch added: {new_name}")

    def action_delete_stopwatch(self) -> None:
        timers = self.query("Stopwatch")
        if timers:
            to_remove = self.selected_stopwatch if hasattr(self, "selected_stopwatch") else timers.last()
            next_selected = None
            for sw in timers:
                if sw is to_remove:
                    break
                next_selected = sw
            if not next_selected:
                idx = list(timers).index(to_remove)
                if idx + 1 < len(timers):
                    next_selected = list(timers)[idx + 1]
            to_remove.remove()
            logger.info(f"Stopwatch deleted: {to_remove.sw_name}")
            if next_selected:
                self.select_stopwatch(next_selected)
            else:
                self.selected_stopwatch = None

    def select_stopwatch(self, stopwatch):
        for sw in self.query("Stopwatch"):
            sw.remove_class("selected")
        stopwatch.add_class("selected")
        self.selected_stopwatch = stopwatch
        logger.debug(f"Stopwatch selected: {stopwatch.sw_name}")

    def action_toggle_dark(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"
        logger.info(f"Theme toggled: {self.theme}")
