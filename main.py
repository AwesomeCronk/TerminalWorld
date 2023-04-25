import sys, termios

from pynput import keyboard
import simpleANSI as ansi

import ui


def setBGColor(r, g, b):
    return ansi.graphics.setGraphicsMode(ansi.graphics.bgColor, ansi.graphics.mode16Bit, r, g, b)

def setFGColor(r, g, b):
    return ansi.graphics.setGraphicsMode(ansi.graphics.fgColor, ansi.graphics.mode16Bit, r, g, b)


tileSize = (6, 3)

tileGrass = (
    setBGColor(30, 145, 30),
    setFGColor(0, 90, 0),
    (
        ' ; ! `',
        ': ; l ',
        ' , ` ;'
    )
)

tiles = {
    'grass': tileGrass
}

def drawTile(name, x, y):
    tile = tiles[name]

    print(tile[0], tile[1], sep='', end='')
    for l, line in enumerate(tile[2]):
        print(ansi.cursor.moveTo(x + 1, y + 1 + l), end='')
        print(line, end='')


# print(os.get_terminal_size())

# drawTile('grass', 5, 5)




if __name__ == '__main__':
    try:
        ui.setEcho(False)
        keyListener = keyboard.Listener(on_press=ui._onKeyPress, on_release=ui._onKeyRelease)
        keyListener.start()

        mainMenu = ui.menu('Main Menu')
        mainMenu.addItem(
            ui.actionMenuItem(
                'newGame',
                'New Game'
            )
        )
        mainMenu.addItem(
            ui.boolMenuItem(
                'sound',
                'Sound',
                choices=('Off', 'On'),
                currentChoice=False
            )
        )
        mainMenu.addItem(
            ui.valueMenuItem(
                'volume',
                'Sound Volume',
                value=15
            )
        )
        mainMenu.addItem(
            ui.choiceMenuItem(
                'gameMode',
                'Game Mode',
                choices=('Easy', 'Medium', 'Hard', 'Asian'),
                currentChoice=0
            )
        )

        result = mainMenu.exec()

        ui.clearScreen()
        ui.homeCursor()

        print('Results:\n{}'.format(result))

    finally:
        keyListener.stop()
        termios.tcflush(sys.stdin, termios.TCIFLUSH)    # `sys.stdin.flush()` Doesn't seem to do anything
        ui.setEcho(True)
