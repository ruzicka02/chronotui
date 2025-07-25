import logging

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

    def compose(self) -> ComposeResult:
        settings = [
            ("Stop all on start", "stop_all_on_start", False),
            ("Pop-up confirmation screens", "confirmation_screens", True),
        ]
        yield Vertical(
            Label("Settings", id="settings-title", expand=True),
            *[
                Checkbox(label, value=self.app.config.get(key, default), id=f"setting-{key}")
                for label, key, default in settings
            ],
            id="settings-container",
        )

    def on_mount(self) -> None:
        # Focus the first checkbox by default
        checkboxes = list(self.query(Checkbox))
        if checkboxes:
            checkboxes[0].focus()

    def on_key(self, event) -> None:
        pressed_key = event.key

        checkboxes = list(self.query(Checkbox))
        focused = self.focused

        if pressed_key in ["escape", "s", "q"]:
            event.stop()
            self.dismiss()
            return
        if not checkboxes or focused not in checkboxes:
            return
        idx = checkboxes.index(focused)
        if pressed_key in ["down", "j"]:
            event.stop()
            if idx < len(checkboxes) - 1:
                checkboxes[idx + 1].focus()
        elif pressed_key in ["up", "k"]:
            event.stop()
            if idx > 0:
                checkboxes[idx - 1].focus()

    def on_checkbox_changed(self, event):
        # All setting checkboxes have id 'setting-<key>'
        if event.checkbox.id and event.checkbox.id.startswith("setting-"):
            key = event.checkbox.id.removeprefix("setting-")
            self.app.config[key] = event.value
            self.app.save_config()
            logging.info(f"Settings updated: {key} = {event.value}")
