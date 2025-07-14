from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class DeleteConfirmScreen(ModalScreen[bool]):
    CSS = """
    DeleteConfirmScreen {
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

    def __init__(self, stopwatch_name: str):
        super().__init__()
        self.stopwatch_name = stopwatch_name

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Delete stopwatch '{self.stopwatch_name}'?", id="question"),
            Button("Delete", variant="error", id="confirm-delete"),
            Button("Cancel", variant="primary", id="cancel-delete"),
            id="dialog",
        )

    def on_mount(self) -> None:
        # Focus the Delete button by default
        self.query_one("#confirm-delete", Button).focus()

    def on_key(self, event) -> None:
        delete_btn = self.query_one("#confirm-delete", Button)
        cancel_btn = self.query_one("#cancel-delete", Button)
        focused = self.focused
        if event.key in ("right"):
            if focused is delete_btn:
                cancel_btn.focus()
        elif event.key in ("left"):
            if focused is cancel_btn:
                delete_btn.focus()
        elif event.key in ("d"):
            # Allow 'd' to confirm delete
            if focused is delete_btn:
                self.on_button_pressed(Button.Pressed(button=delete_btn))
        event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-delete":
            self.dismiss(True)
        else:
            self.dismiss(False)
