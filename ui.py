import time
from contextlib import contextmanager

from pynput import keyboard
import simpleANSI as ansi


ansiHighlight = ansi.graphics.setGraphicsMode(ansi.graphics.bgWhite + ansi.graphics.fgBlack)
ansiNormal = ansi.graphics.setGraphicsMode(ansi.graphics.normal)

### Keyboard input ###
keyEvents = []

class keyEvent():
    def __init__(self, key, callback, onPress, onRelease):
        self.key = key,
        self.callback = callback
        self.onPress = onPress
        self.onRelease = onRelease
        self.active = True
        self.calls = []
        keyEvents.append(self)

    # Called from listener thread, do not call callbacks from listener thread because then things happen at unpredictable times
    def fire(self, state):
        if self.active:
            print('fired {}'.format(self.callback))
            if self.onPress and state: self.calls.append(True)
            elif self.onRelease and not state: self.calls.append(False)

def _onKeyPress(key):
    print(key)
    for event in keyEvents:
        print(event.key)
        if event.key == key: event.fire(True)
        else: print('Did not fire {}'.format(event.callback))

def _onKeyRelease(key):
    for event in keyEvents:
        if event.key == key: event.fire(False)

@contextmanager
def runKeyListener():
    try:
        keyListener = keyboard.Listener(on_press=_onKeyPress, on_release=_onKeyRelease)
        keyListener.start()
        yield keyListener
    finally:
        keyListener.stop()


### Menu items ###
class menu():
    def __init__(self, name):
        self.name = name
        self.items = []
        self.keyEvents = [
            keyEvent(keyboard.Key.left,  self._keyLeft,  True, False),
            keyEvent(keyboard.Key.right, self._keyRight, True, False),
            keyEvent(keyboard.Key.up,    self._keyUp,    True, False),
            keyEvent(keyboard.Key.down,  self._keyDown,  True, False),
            keyEvent(keyboard.Key.enter, self._keyEnter, True, False)
        ]
        for event in self.keyEvents: event.active = False

        self.active = False
        self.selectingItem = True
        self.selectingOption = False
        self.selectedItem = 0
        self.selectedOption = 0

    def addItem(self, item):
        self.items.append(item)

    def _keyLeft(self, keyState):
        if self.selectingOption: self.selectedOption = (self.selectedOption - 1) % len(self.options)
        self.refresh()

    def _keyRight(self, keyState):
        if self.selectingOption: self.selectedOption = (self.selectedOption + 1) % len(self.options)
        self.refresh()

    def _keyUp(self, keyState):
        if self.selectingItem: self.selectedItem = (self.selectedItem - 1) % len(self.items)
        self.items[1].options[0] += 1
        self.refresh()

    def _keyDown(self, keyState):
        if self.selectingItem: self.selectedItem = (self.selectedItem + 1) % len(self.items)
        self.refresh()

    def _keyEnter(self, keyState):
        self.active = False

    def refresh(self):
        print(
            ansi.graphics.setGraphicsMode(ansi.graphics.normal),
            ansi.clear.entireScreen(),
            ansi.cursor.home(),
            end=''
        )
        print(self.name)
        for item in self.items: print('*', item)
        firstItemLine = 2
        print(ansi.cursor.moveTo(0, firstItemLine + self.selectedItem), end='')

    # We must assume that all unnecessary key events are disabled before exec'ing a menu because
    # some may need to stay enabled
    def exec(self):
        for event in self.keyEvents: event.active = True
        self.refresh()
        self.active = True
        while self.active:
            for event in self.keyEvents:
                for call in event.calls:
                    event.callback(call)
            time.sleep(0.1)

class menuItem():
    TYPE_ACTION = 0
    TYPE_BOOL = 1
    TYPE_VALUE = 2
    TYPE_OPTIONS = 3

    def __init__(self, name, text, type, options=(), currentOption=None):
        self.name = name
        self.text = text
        self.type = type
        self.options = options
        self.currentOption = currentOption

    def __str__(self):
        line = self.text
        if self.type == menuItem.TYPE_BOOL:
            if self.currentOption is None:
                line += ' ({}, {})'.format(*self.options[0:2])
            else:
                line += ' ({}, {})'.format(*[(ansiHighlight + option + ansiNormal) if bool(o) == self.currentOption else option for o, option in enumerate(self.options[0:2])])
        elif self.type == menuItem.TYPE_VALUE:
            if self.currentOption is None:
                line += ' (?)'
            else:
                line += ' ({})'.format(self.currentOption)
        elif self.type == menuItem.TYPE_OPTIONS:
            line += ' ({})'.format(', '.join([(ansiHighlight + option + ansiNormal) if o == self.currentOption else option for o, option in enumerate(self.options)]))
        return line
                    


