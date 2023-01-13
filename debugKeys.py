# This script just prints what each key is called

import sys, termios, time

from pynput import keyboard


run = True


def _onPress(key):
    print(key)

def _onRelease(key):
    global run
    if key == keyboard.Key.esc:
        run = False
        return False

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

def clearStdin():
    termios.tcflush(sys.stdin, termios.TCIFLUSH)
    # sys.stdin.flush()   # Doesn't seem to do anything


if __name__ == '__main__':
    print('Press keys to see what pynput shows them as. Hit Esc to exit.')
    try:
        setEcho(False)
        listener = keyboard.Listener(on_press=_onPress, on_release=_onRelease)
        listener.start()
        while run: time.sleep(0.1)
    finally:
        listener.stop()
        print('Listener stopped')
        clearStdin()
        setEcho(True)
        print('Echo reenabled')
