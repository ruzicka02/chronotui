"""
Time tracking app. Originally inspired from https://textual.textualize.io/tutorial/
"""

from app import StopwatchApp

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, filename="chronotui.log",)
    app = StopwatchApp()
    app.run()