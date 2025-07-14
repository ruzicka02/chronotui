from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Checkbox, Label


class SettingsScreen(ModalScreen):
    CSS = """
    SettingsScreen {
        align: center middle;
        padding: 0 1;
    }

    #settings-container {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 2 4;
        width: 40%;
        height: auto;
        border: thick $background 80%;
        background: $surface;
    }
    #settings-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    """

    def on_key(self, event):
        if event.key in ("escape", "s", "q"):
            self.dismiss()
            event.stop()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Settings", id="settings-title", expand=True),
            Checkbox(
                "Stop all on start", value=self.app.config.get("stop_all_on_start", False), id="stop-all-checkbox"
            ),
            id="settings-container",
        )

    def on_checkbox_changed(self, event):
        if event.checkbox.id == "stop-all-checkbox":
            self.app.config["stop_all_on_start"] = event.value
            self.app.save_config()
