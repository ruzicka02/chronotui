from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmScreen(ModalScreen[bool]):
    CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    Button {
        width: 100%;
    }
    """

    def __init__(self, stopwatch_name: str, action_name: str, confirm_key: str):
        super().__init__()
        self.stopwatch_name = stopwatch_name
        self.action_name = action_name
        self.confirm_key = confirm_key

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"{self.action_name.capitalize()} stopwatch '{self.stopwatch_name}'?", id="question"),
            Button(self.action_name.capitalize(), variant="error", id="confirm-btn"),
            Button("Cancel", variant="primary", id="cancel-btn"),
            id="dialog",
        )

    def on_mount(self) -> None:
        # Focus the Confirm button by default
        self.query_one("#confirm-btn", Button).focus()

    def on_key(self, event) -> None:
        pressed_key = event.key
        # stops key event propagation
        event.stop()

        confirm_btn = self.query_one("#confirm-btn", Button)
        cancel_btn = self.query_one("#cancel-btn", Button)
        focused = self.focused
        if pressed_key in ["right", "l"]:
            if focused is confirm_btn:
                cancel_btn.focus()
        elif pressed_key in ["left", "h"]:
            if focused is cancel_btn:
                confirm_btn.focus()
        elif pressed_key in ["enter", "space"]:
            if focused:
                self.on_button_pressed(Button.Pressed(button=focused))
        elif pressed_key in [self.confirm_key]:
            if focused is confirm_btn:
                self.on_button_pressed(Button.Pressed(button=confirm_btn))
        elif pressed_key in ["escape", "c", "q"]:
            self.on_button_pressed(Button.Pressed(button=cancel_btn))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
