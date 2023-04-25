import sys, termios, time

from pynput import keyboard
import simpleANSI as ansi


### ANSI wraps ###

ansiHighlight = ansi.graphics.setGraphicsMode(ansi.graphics.bgWhite + ansi.graphics.fgBlack)
ansiNormal = ansi.graphics.setGraphicsMode(ansi.graphics.normal)

def clearScreen():
    print(
        ansi.graphics.setGraphicsMode(ansi.graphics.normal),
        ansi.clear.entireScreen(),
        end=''
    )

def homeCursor():
    print(
        ansi.cursor.home(),
        end=''
    )


# Modified version of `enable_echo` found at https://blog.hartwork.org/posts/disabling-terminal-echo-in-python/
def setEcho(value):
    iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(sys.stdin)

    if value: lflag |= termios.ECHO
    else: lflag &= ~termios.ECHO

    termios.tcsetattr(
        sys.stdin,
        termios.TCSANOW,
        [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    )


### Keyboard input ###

keyEvents = []

class keyEvent():
    def __init__(self, key, callback, onPress, onRelease):
        self.key = key
        self.callback = callback
        self.onPress = onPress
        self.onRelease = onRelease
        self.active = True
        self.calls = []
        keyEvents.append(self)

    # Called from listener thread, do not call callbacks from listener thread to avoid asynchronous access
    def fire(self, state):
        if self.active:
            if self.onPress and state: self.calls.append(True)
            elif self.onRelease and not state: self.calls.append(False)

def _onKeyPress(key):
    for event in keyEvents:
        if key == event.key: event.fire(True)

def _onKeyRelease(key):
    for event in keyEvents:
        if key == event.key: event.fire(False)


### Menus ###

class menuItem():
    def __init__(self, name: str, text: str, choices, currentChoice):
        self.name = name
        self.text = text

    def _setParent(self, parent):
        self.parent = parent


class menu():
    def __init__(self, name):
        self.name = name
        self.items = []
        self.itemTextPadding = 0
        self.keyEvents = [
            keyEvent(keyboard.Key.up,    self._keyUp,    True, False),
            keyEvent(keyboard.Key.down,  self._keyDown,  True, False),
            keyEvent(keyboard.Key.enter, self._keyEnter, True, False)
        ]
        for event in self.keyEvents: event.active = False

        self.active = False
        self.selectedItemID = 0
        self.result = {}

    def addItem(self, item: menuItem):
        self.items.append(item)
        item._setParent(self)
        self.itemTextPadding = max(self.itemTextPadding, len(item.text))


    # Up one item
    def _keyUp(self, keyState: bool):
        self.selectedItemID -= 1
        self.selectedItemID %= len(self.items)
        self.placeCursor()

    # Down one item
    def _keyDown(self, keyState: bool):
        self.selectedItemID += 1
        self.selectedItemID %= len(self.items)
        self.placeCursor()

    # Select item/option
    def _keyEnter(self, keyState: bool):
        self.items[self.selectedItemID].select()

    # Clear the screen and render the menu
    def redraw(self):
        clearScreen()
        homeCursor()
        print(self.name)
        for item in self.items: print('*', item)

    # Move the cursor to the appropriate position
    def placeCursor(self):
        firstItemLine = 2

        # Need to figure out choices

        print(ansi.cursor.moveTo(1, firstItemLine + self.selectedItemID), end='', flush=True)

    def exec(self):
        # We must assume that all unnecessary key events are disabled before exec'ing a menu because
        # some may need to stay enabled
        for event in self.keyEvents: event.active = True

        self.redraw()
        self.placeCursor()

        self.active = True
        while self.active:
            for event in self.keyEvents:
                for call in event.calls:
                    event.callback(call)
                event.calls = []
            time.sleep(0.1)

        for event in self.keyEvents: event.active = False

        return self.result


class actionMenuItem(menuItem):
    def __init__(self, name: str, text: str):
        menuItem.__init__(self, name, text, (), None)

    def __str__(self):
        return self.text
    
    def select(self):
        self.parent.result[self.name] = 'select'
        self.parent.active = False

class boolMenuItem(menuItem):
    def __init__(self, name: str, text: str, choices=('False', 'True'), currentChoice=False):
        # `choices` is iterable containing the False and True choices
        # `currentChoice` is False, or True
        menuItem.__init__(self, name, text, choices, currentChoice)

        self.choices = choices
        self.currentChoice = currentChoice

    def __str__(self):
        return '{} | {}'.format(
            self.text.ljust(self.parent.itemTextPadding),
            self.choices[self.currentChoice]
        )
    
    def select(self):
        self.currentChoice = not self.currentChoice
        self.parent.result[self.name] = self.currentChoice
        self.parent.redraw()
        self.parent.placeCursor()
    
class choiceMenuItem(menuItem):
    def __init__(self, name: str, text: str, choices=(), currentChoice=0):
        # `choices` is iterable containing the 0/False and 1/True choices
        # `currentChoice` is 0/False, or 1/True
        menuItem.__init__(self, name, text, choices, currentChoice)

        self.choices = choices
        self.currentChoice = currentChoice

    def __str__(self):
        return '{} | {}'.format(
            self.text.ljust(self.parent.itemTextPadding),
            ' - '.join([('<' + option + '>') if o == self.currentChoice else option for o, option in enumerate(self.choices)])
        )

class valueMenuItem(menuItem):
    def __init__(self, name: str, text: str, value='***'):
        menuItem.__init__(self, name, text, (), value)

        self.value = value

    def __str__(self):
        return '{} | {}'.format(
            self.text.ljust(self.parent.itemTextPadding),
            self.value
        )
