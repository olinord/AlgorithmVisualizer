'''
Created on Sep 7, 2014

@author: oli
'''
from qtpy import QtCore, QtGui
import qtawesome as qta
import fontAwesome as fa

class Button(QtGui.QPushButton):

    def __init__(self, qssClass):
        QtGui.QPushButton.__init__(self)
        self.setProperty("class", qssClass)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)


class IconPlaybackButton(Button):
    def __init__(self, icon):
        Button.__init__(self, "playback")
        self.setText(icon)
        self.setFont(qta.font('fa', 12))


class PlayButton(IconPlaybackButton):
    def __init__(self):
        IconPlaybackButton.__init__(self, fa.fa_play)


class StopButton(IconPlaybackButton):
    def __init__(self):
        IconPlaybackButton.__init__(self, fa.fa_stop)
