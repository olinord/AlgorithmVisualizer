import math
import sys

from sdlApp import App

def RunApp():
    "Setup and run the app"


    app = App("GameIdea")
    if not app.SetupApp(800, 600):
        return

    app.Run()

    return 0

if __name__ == "__main__":
    RunApp()