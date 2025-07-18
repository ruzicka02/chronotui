import datetime
import json
import logging
import os
import sys

import platformdirs
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, HelpPanel

from chronotui.config.defaults import ALLOWED_THEMES, DEFAULT_CONFIG
from chronotui.widgets.confirm_screen import ConfirmScreen
from chronotui.widgets.settings_screen import SettingsScreen
from chronotui.widgets.stopwatch import Stopwatch

logger = logging.getLogger(__name__)
file_logging = "-l" in sys.argv or "--log" in sys.argv


def main():
    logging.basicConfig(
        level=logging.INFO if file_logging else logging.ERROR,
        filename="chronotui.log" if file_logging else None,
    )
    app = StopwatchApp()
    app.title = "ChronoTUI"
    app.sub_title = "Track your time with style"
    app.run()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("q", "save_and_quit", "Quit"),
        ("space", "toggle_selected", "Start/Stop"),
        ("r", "reset_selected", "Reset"),
        ("a", "add_stopwatch", "Add timer"),
        ("d", "delete_stopwatch", "Delete timer"),
        ("n", "change_name", "reName timer"),
        ("t", "configure_theme", "Theme"),
        ("s", "configure_settings", "Settings"),
        Binding("?", "toggle_help_panel", "Keybindings", show=True),
        Binding("up", "select_up", "Up", show=False),
        Binding("down", "select_down", "Down", show=False),
        Binding("j", "select_down", "Down", show=False),
        Binding("k", "select_up", "Up", show=False),
        Binding("S", "save_stopwatches", "Save Stopwatches", show=False),
        Binding("L", "load_stopwatches", "Load Stopwatches", show=False),
        # duplicate of reName, keep until another usecase for `c` appears
        Binding("c", "change_name", "Change timer name", show=False),
    ]

    SAVE_PATH = platformdirs.user_data_dir("chronotui")
    SAVE_FILE = os.path.join(SAVE_PATH, "session.json")

    CONFIG_PATH = platformdirs.user_config_dir("chronotui")
    CONFIG_FILE = os.path.join(CONFIG_PATH, "config.json")

    def action_toggle_help_panel(self) -> None:
        """Toggle the keys panel. The base Textual class can show or hide, but not toggle with one key."""
        try:
            self.query_one(HelpPanel).remove()
        except NoMatches:
            self.mount(HelpPanel())

    def load_config(self):
        """Load configuration from CONFIG_FILE or set defaults."""
        config = DEFAULT_CONFIG.copy()
        if os.path.isfile(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                config.update(loaded)
                logger.info(f"Config loaded from {self.CONFIG_FILE}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            logger.info("No config file found, using defaults.")
        logger.debug(f"Loaded configuration: {config}")
        self.config = config

    def process_config(self) -> None:
        """Process the loaded configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded. Call load_config() first.")

        # load theme
        if "theme" not in self.config:
            raise ValueError("Theme not set in config.")
        if self.config["theme"] not in ALLOWED_THEMES:
            raise ValueError(f"Invalid theme: {self.config['theme']}")
        self.theme = self.config["theme"]

        # load stop_all_on_start
        if "stop_all_on_start" not in self.config:
            raise ValueError("stop_all_on_start not set in config.")
        if not isinstance(self.config["stop_all_on_start"], bool):
            raise ValueError("stop_all_on_start must be a boolean.")
        # does not do any processing, here it's just a value check

        # load confirmation_screens
        if "confirmation_screens" not in self.config:
            raise ValueError("confirmation_screens not set in config.")
        if not isinstance(self.config["confirmation_screens"], bool):
            raise ValueError("confirmation_screens must be a boolean.")

        logger.info(f"Processed config: {self.config}")

    def save_config(self):
        """Save current configuration to CONFIG_FILE."""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Config saved to {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def on_mount(self) -> None:
        os.makedirs(self.SAVE_PATH, exist_ok=True)
        os.makedirs(self.CONFIG_PATH, exist_ok=True)
        self.load_config()
        self.process_config()
        # Autoload state on app start
        await self.action_load_stopwatches()

    async def action_load_stopwatches(self) -> None:
        """Load stopwatches state from SAVE_FILE and restore them."""
        try:
            with open(self.SAVE_FILE, "r") as f:
                data = json.load(f)
            stopwatches = data["stopwatches"] if isinstance(data, dict) and "stopwatches" in data else data
            last_modified = data.get("last_modified") if isinstance(data, dict) else None
        except Exception as e:
            logger.error(f"Failed to load stopwatches: {e}")
            return

        # Calculate time delta if clocks were running
        time_delta = 0
        if last_modified:
            try:
                saved_time = datetime.datetime.fromisoformat(last_modified)
            except Exception as e:
                logger.warning(f"Could not parse last_modified: {e}")
                saved_time = None
            if saved_time:
                now = datetime.datetime.now(saved_time.tzinfo) if saved_time.tzinfo else datetime.datetime.now()
                time_delta = (now - saved_time).total_seconds()

        # Remove all existing stopwatches, and wait until they really are removed
        await self.query("Stopwatch").remove()

        new_stopwatches = []
        selected_stopwatch = None
        for sw_data in stopwatches:
            name = sw_data.get("name", "Stopwatch")
            sw_time = sw_data.get("time", 0)
            running = sw_data.get("running", False)
            active = sw_data.get("active", False)
            # If running, add time delta
            if running and time_delta > 0:
                sw_time += time_delta
            sw = Stopwatch(name, time=sw_time, running=running, active=active)
            self.query_one("#timers").mount(sw)
            logger.info(f"Loading stopwatch: {name}")
            new_stopwatches.append(sw)
            if active:
                selected_stopwatch = sw
        self.selected_stopwatch = (
            selected_stopwatch if selected_stopwatch else (new_stopwatches[0] if new_stopwatches else None)
        )
        logger.info(f"Selected stopwatch: {self.selected_stopwatch.sw_name if self.selected_stopwatch else 'None'}")
        logger.info(f"Stopwatches loaded from {self.SAVE_FILE}")

    def action_save_stopwatches(self) -> None:
        stopwatches = []
        for sw in self.query("Stopwatch"):
            # Try to get the time from the TimeDisplay widget
            try:
                time_display = sw.query_one("TimeDisplay")
                time_value = getattr(time_display, "time", None)
                logger.info(f"Getting time for stopwatch: {sw.sw_name}, {time_value}")
                if time_value is None and hasattr(time_display, "get_time"):
                    time_value = time_display.get_time()
            except Exception:
                logger.warning(f"Failed to get time for stopwatch {sw.sw_name}")
                time_value = None
            sw_data = {
                "name": getattr(sw, "sw_name", None),
                "time": time_value,
                "running": "started" in sw.classes,
                "active": "selected" in sw.classes,
            }
            stopwatches.append(sw_data)

        result = {
            "stopwatches": stopwatches,
            "last_modified": datetime.datetime.now().isoformat(),
        }

        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Stopwatches saved to {self.SAVE_FILE}")
        except Exception as e:
            logger.error(f"Failed to save stopwatches: {e}")

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

    @work
    async def action_reset_selected(self) -> None:
        if not hasattr(self, "selected_stopwatch") or self.selected_stopwatch is None:
            return
        sw = self.selected_stopwatch
        # Confirmation logic
        if self.config.get("confirmation_screens", True):
            confirmed = await self.push_screen_wait(
                ConfirmScreen(stopwatch_name=getattr(sw, "sw_name", "Stopwatch"), action_name="reset", confirm_key="r")
            )
            if not confirmed:
                logger.info("Reset cancelled by user.")
                return
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
            if self.config.get("stop_all_on_start", False):
                self.action_stop_all_stopwatches()
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

    @work
    async def action_delete_stopwatch(self) -> None:
        timers = self.query("Stopwatch")
        if not timers:
            return
        to_remove = self.selected_stopwatch if hasattr(self, "selected_stopwatch") else None
        if not to_remove:
            logger.warning("No stopwatch selected for deletion.")
            return

        # Confirmation logic
        if self.config.get("confirmation_screens", True):
            confirmed = await self.push_screen_wait(
                ConfirmScreen(
                    stopwatch_name=getattr(to_remove, "sw_name", "Stopwatch"), action_name="delete", confirm_key="d"
                )
            )
            if not confirmed:
                logger.info("Delete cancelled by user.")
                return

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

    def action_configure_theme(self) -> None:
        self.search_themes()

    async def action_save_and_quit(self) -> None:
        # Autosave state and config on quit
        self.action_save_stopwatches()

        # Ideally I would do this on theme change, but I don't know how to override the change from the built it select list
        self.config["theme"] = self.theme

        self.save_config()
        self.exit()

    def action_stop_all_stopwatches(self) -> None:
        """Stop all running stopwatches."""
        for sw in self.query("Stopwatch"):
            if "started" in sw.classes:
                time_display = sw.query_one("TimeDisplay")
                time_display.stop()
                sw.remove_class("started")
                logger.info(f"Stopped stopwatch: {sw.sw_name}")
        logger.info("All stopwatches stopped.")

    def action_configure_settings(self) -> None:
        self.push_screen(SettingsScreen())
