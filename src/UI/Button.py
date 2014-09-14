'''
Created on Sep 7, 2014

@author: oli
'''

from PySide.QtGui import QPushButton, QPalette
import PySide.QtCore as QtCore
from icons import PLAY_BUTTON_ICON, STOP_BUTTON_ICON

class Button(QPushButton):

    def __init__(self, qssClass):
        QPushButton.__init__(self)
        self.setProperty("class", qssClass)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)
        
class IconPlaybackButton(Button):
    def __init__(self, icon):
        Button.__init__(self, "playback")
        self.setText(icon)
        
class PlayButton(IconPlaybackButton):
    def __init__(self):
        IconPlaybackButton.__init__(self, PLAY_BUTTON_ICON)

class StopButton(IconPlaybackButton):
    def __init__(self):
        IconPlaybackButton.__init__(self, STOP_BUTTON_ICON)
        