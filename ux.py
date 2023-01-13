import sys, time

from pynput import keyboard
import simpleANSI as ansi


ansiHighlight = ansi.graphics.setGraphicsMode(ansi.graphics.bgWhite + ansi.graphics.fgBlack)
ansiNormal = ansi.graphics.setGraphicsMode(ansi.graphics.normal)

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

    # Called from listener thread, do not call callbacks from listener thread because then things happen at unpredictable times
    def fire(self, state):
        if self.active:
            if self.onPress and state: self.calls.append(True)
            elif self.onRelease and not state: self.calls.append(False)

def _onKeyPress(key):
    for event in keyEvents:
        if event.key == key: event.fire(True)

def _onKeyRelease(key):
    for event in keyEvents:
        if event.key == key: event.fire(False)


### Menus ###

class menuItem():
    TYPE_ACTION = 0     # options is ignored, currentOption is ignored
    TYPE_BOOL = 1       # options is iterable containing the 0/False and 1/True options, currentOption is 0, 1, False, or True
    TYPE_OPTIONS = 2    # options is iterable containing all options, currentOption is index of options
    TYPE_VALUE = 3      # options is ignored, currentOption is value (string-representable, will return a string in results)

    def __init__(self, name: str, text: str, type: int, options, currentOption):
        self.name = name
        self.text = text
        self.type = type
        self.options = options
        self.currentOption = currentOption
        self.padding = len(text)

    def __str__(self):
        line = self.text.ljust(self.padding)
        if self.type == menuItem.TYPE_BOOL:
            line += ' | {}'.format(self.options[self.currentOption])
        elif self.type == menuItem.TYPE_VALUE:
            line += ' | {}'.format(self.currentOption)
        elif self.type == menuItem.TYPE_OPTIONS:
            line += ' | {}'.format(' - '.join([(ansiHighlight + option + ansiNormal) if o == self.currentOption else option for o, option in enumerate(self.options)]))
        return line

class menu():
    def __init__(self, name):
        self.name = name
        self.items = []
        self.itemPadding = 0
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
        self.selectedItemID = 0
        self.selectedOptionID = 0
        self.result = {}

    def addItem(self, item: menuItem):
        self.items.append(item)
        self.itemPadding = max(self.itemPadding, item.padding)
        for item in self.items: item.padding = self.itemPadding

    # Left one option
    def _keyLeft(self, keyState: bool):
        if self.selectingOption: self.selectedOptionID = (self.selectedOptionID - 1) % len(self.options)
        self.placeCursor()

    # Right one option
    def _keyRight(self, keyState: bool):
        if self.selectingOption: self.selectedOptionID = (self.selectedOptionID + 1) % len(self.options)
        self.placeCursor()

    # Up one item
    def _keyUp(self, keyState: bool):
        if self.selectingItem: self.selectedItemID = (self.selectedItemID - 1) % len(self.items)
        self.placeCursor()

    # Down one item
    def _keyDown(self, keyState: bool):
        if self.selectingItem: self.selectedItemID = (self.selectedItemID + 1) % len(self.items)
        self.placeCursor()

    # Select item/option
    def _keyEnter(self, keyState: bool):
        if self.selectingItem:
            selectedItem = self.items[self.selectedItemID]
            if selectedItem.type == menuItem.TYPE_ACTION:
                self.result[selectedItem.name] = 'call'
                self.active = False
                return
            elif selectedItem.type == menuItem.TYPE_BOOL:
                selectedItem.currentOption = 1 - selectedItem.currentOption
                self.result[selectedItem.name] = selectedItem.currentOption
                self.redraw()
                self.placeCursor()
            elif selectedItem.type == menuItem.TYPE_OPTIONS:
                # `_keyLeft` and `_keyRight` will take care of selecting options,
                # then `_keyEnter` will finalize the selection and store the result
                self.selectingItem = False
                self.selectingOption = True
                self.placeCursor()
            elif selectedItem.type == menuItem.TYPE_VALUE:
                pass
                # Move cursor to beginning of value
                # Flush stdin
                # Enable echo
                # Disable menu key events
                # `input()` text
                # Disable echo
                # Enable menu key events

    # Clear the screen and render the menu
    def redraw(self):
        print(
            ansi.graphics.setGraphicsMode(ansi.graphics.normal),
            ansi.clear.entireScreen(),
            ansi.cursor.home(),
            end=''
        )
        print(self.name)
        for item in self.items: print('*', item)

    # Move the cursor to the appropriate position
    def placeCursor(self):
        firstItemLine = 2
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
        return self.result
