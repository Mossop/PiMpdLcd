import os, sys

from shared import *

if os.name == "nt":
    from ctypes import windll, Structure, c_short, byref, create_unicode_buffer
    from ctypes.wintypes import WORD, DWORD, WCHAR, LPCWSTR

    SHORT = c_short

    class COORD(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("X", SHORT),
            ("Y", SHORT)]

    class SMALL_RECT(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("Left", SHORT),
            ("Top", SHORT),
            ("Right", SHORT),
            ("Bottom", SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD)]

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
    SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
    FillConsoleOutputCharacter = windll.kernel32.FillConsoleOutputCharacterW
    FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
    SetConsoleTitle = windll.kernel32.SetConsoleTitleW
    GetConsoleOriginalTitle = windll.kernel32.GetConsoleOriginalTitleW

    class Console:
        RED = 4
        GREEN = 2
        BLUE = 1

        fp = None
        handle = None
        default = None
        pos = 0

        def __init__(self, fp):
            self.fp = fp
            self.handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(self.handle, byref(csbi))
            self.default = csbi.wAttributes

        def _translate_color(self, color):
            newcolor = BLACK
            if color & RED:
                newcolor = newcolor + self.RED
            if color & GREEN:
                newcolor = newcolor + self.GREEN
            if color & BLUE:
                newcolor = newcolor + self.BLUE
            return newcolor

        def _get_position(self):
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(self.handle, byref(csbi))
            return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y

        def _set_position(self, x, y):
            coord = COORD()
            coord.X = x
            coord.Y = y
            SetConsoleCursorPosition(self.handle, coord)

        def go_to_pos(self, pos):
            if pos > self.pos:
                self.go_down(pos - self.pos)
            elif self.pos > pos:
                self.go_up(self.pos - pos)

        def go_linehome(self):
            x, y = self._get_position()
            self._set_position(0, y)

        def go_left(self, chars):
            if chars > 0:
                x, y = self._get_position()
                self._set_position(x - chars, y)

        def go_right(self, chars):
            if chars > 0:
                x, y = self._get_position()
                self._set_position(x + chars, y)

        def go_up(self, lines):
            if lines > 0:
                x, y = self._get_position()
                self._set_position(x, y - lines)
                self.pos -= lines

        def go_down(self, lines):
            if lines > 0:
                x, y = self._get_position()
                self._set_position(x, y + lines)
                self.pos += lines

        def clear(self):
            origin = COORD()
            origin.X = 0
            origin.Y = 0
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(self.handle, byref(csbi))
            size = csbi.dwSize.X * csbi.dwSize.Y;
            chars = DWORD()
            FillConsoleOutputCharacter(self.handle, WCHAR(' '), size, origin, byref(chars))
            FillConsoleOutputAttribute(self.handle, self.default, size, origin, byref(chars))
            self._set_position(0, 0)
            self.pos = 0

        def reset_color(self):
            SetConsoleTextAttribute(self.handle, self.default)

        def set_color(self, foreground):
            color = self._translate_color(foreground) | 8
            SetConsoleTextAttribute(self.handle, color)

        def set_title(self, text):
            SetConsoleTitle(LPCWSTR(text))

        def clear_title(self):
            title = create_unicode_buffer(1024)
            GetConsoleOriginalTitle(title, 1024)
            SetConsoleTitle(title)
else:
    class Console:
        fp = None
        pos = 0

        def __init__(self, fp):
            self.fp = fp

        def go_to_pos(self, pos):
            if pos > self.pos:
                self.go_down(pos - self.pos)
            elif self.pos > pos:
                self.go_up(self.pos - pos)

        def go_linehome(self):
            self.go_left(79)

        def go_left(self, chars):
            if chars > 0:
                self.fp.write("\033[%sD" % chars)

        def go_right(self, chars):
            if chars > 0:
                self.fp.write("\033[%sC" % chars)

        def go_up(self, lines):
            if lines > 0:
                self.fp.write("\033[%sA" % lines)
                self.pos -= lines

        def go_down(self, lines):
            if lines > 0:
                self.fp.write("\033[%sB" % lines)
                self.pos += lines

        def clear(self):
            self.fp.write("\033[H\033[2J")
            self.pos = 0

        def reset_color(self):
            self.fp.write("\033[0m")

        def set_color(self, foreground):
            self.fp.write("\033[")
            self.fp.write("1;")
            self.fp.write(str(foreground + 30))
            self.fp.write("m")

        def set_title(self, text):
            self.fp.write("\033]0;%s\007" % text)

        def clear_title(self):
            self.set_title("")

class OutputDevice(Console):
    def __init__(self):
        Console.__init__(self, sys.stdout)
        self._color = RED
        self.set_color(WHITE)
        print("+" + "".ljust(WIDTH, "-") + "+")
        print("|" + "".ljust(WIDTH) + "|")
        print("|" + "".ljust(WIDTH) + "|")
        print("+" + "".ljust(WIDTH, "-") + "+")
        self.off()

    def color(self, color):
        self._color = color

    def on(self):
        self.active = True
        self.display("", "")

    def off(self):
        self.active = False
        self.go_up(3)
        self.go_right(1)
        self.set_color(WHITE)
        print("".ljust(WIDTH, "#"))
        self.go_right(1)
        print("".ljust(WIDTH, "#"))
        self.go_down(1)
        self.reset_color()

    def display(self, line1 = None, line2 = None):
        if not self.active:
            self.on()

        self.go_up(3)
        self.go_right(1)
        self.set_color(self._color)
        if line1 is not None:
            print(str(line1)[:WIDTH].ljust(WIDTH))
            self.go_right(1)
        else:
            self.go_down(1)
        if line2 is not None:
            print(str(line2)[:WIDTH].ljust(WIDTH))
            self.go_right(1)
        else:
            self.go_down(1)
        self.go_down(1)
        self.go_left(1)
        self.reset_color()
