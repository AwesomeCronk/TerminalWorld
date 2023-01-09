import os

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

with ui.runKeyListener():
    mainMenu = ui.menu('Main Menu')
    mainMenu.addItem(ui.menuItem('newGame', 'New Game', ui.menuItem.TYPE_ACTION, [], None))
    mainMenu.addItem(ui.menuItem('sound', 'Sound Volume', ui.menuItem.TYPE_VALUE, [], 15))
    mainMenu.exec()

print(ansi.graphics.setGraphicsMode(ansi.graphics.normal))
