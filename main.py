import sys, termios

from pynput import keyboard
import simpleANSI as ansi

import ux


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


if __name__ == '__main__':
    try:
        setEcho(False)
        keyListener = keyboard.Listener(on_press=ux._onKeyPress, on_release=ux._onKeyRelease)
        keyListener.start()

        mainMenu = ux.menu('Main Menu')
        mainMenu.addItem(ux.menuItem('newGame', 'New Game', ux.menuItem.TYPE_ACTION, (), None))
        mainMenu.addItem(ux.menuItem('sound', 'Sound', ux.menuItem.TYPE_BOOL, ('Off', 'On'), 0))
        mainMenu.addItem(ux.menuItem('volume', 'Sound Volume', ux.menuItem.TYPE_VALUE, (), 15))
        print(mainMenu.exec())

    finally:
        keyListener.stop()
        termios.tcflush(sys.stdin, termios.TCIFLUSH)    # `sys.stdin.flush()` Doesn't seem to do anything
        setEcho(True)
        print(ansi.graphics.setGraphicsMode(ansi.graphics.normal))
