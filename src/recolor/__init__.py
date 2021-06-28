"""
Regular Expression Colorizer.
"""

import sys
import os
import select
import re
import time
import shutil
import fcntl

if sys.version_info[0] == 3:
    from io import StringIO
else:
    from StringIO import StringIO


__version__ = "0.1.0"
__version_info__ = (int(v) for v in __version__.split("."))


RESET = "\033[0m"
UNDER = "\033[4m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BBLACK = "\033[1m\033[30m"
BRED = "\033[1m\033[31m"
BGREEN = "\033[1m\033[32m"
BYELLOW = "\033[1m\033[33m"
BBLUE = "\033[1m\033[34m"
BMAGENTA = "\033[1m\033[35m"
BCYAN = "\033[1m\033[36m"
BWHITE = "\033[1m\033[37m"


colors = {
    "u": UNDER,  # underline
    "k": BLACK,  # Black
    "r": RED,  # Red
    "g": GREEN,  # Green
    "y": YELLOW,  # Yellow
    "b": BLUE,  # Blue
    "m": MAGENTA,  # Magenta
    "c": CYAN,  # Cyan
    "w": WHITE,  # White
    "K": BBLACK,  # Bold Black
    "R": BRED,  # Bold Red
    "G": BGREEN,  # Bold Green
    "Y": BYELLOW,  # Bold Yellow
    "B": BBLUE,  # Bold Blue
    "M": BMAGENTA,  # Bold Magenta
    "C": BCYAN,  # Bold Cyan
    "W": BWHITE,  # Bold White
}

colornames = {
    "u": "underline",
    "k": "black",  # Black
    "r": "red",  # Red
    "g": "green",  # Green
    "y": "yellow",  # Yellow
    "b": "blue",  # Blue
    "m": "magenta",  # Magenta
    "c": "cyan",  # Cyan
    "w": "white",  # White
    "K": "bold black",  # Bold Black
    "R": "bold red",  # Bold Red
    "G": "bold green",  # Bold Green
    "Y": "bold yellow",  # Bold Yellow
    "B": "bold blue",  # Bold Blue
    "M": "bold magenta",  # Bold Magenta
    "C": "bold cyan",  # Bold Cyan
    "W": "bold white",  # Bold White
}

revcolornames = dict((name, key) for key, name in colornames.items())

colorkeys = "rgbcymkwRGBCYMKWu"



class ColorMatch(object):
    def __init__(self, rx, colorkey):
        self.rx = rx
        self.ck = colorkey
        self.ct = colors[colorkey]

    def filter(self, text):
        """Filter a string, adding this object's color to all instances where
        this object matches text in the string."""
        off = 0
        out = StringIO()
        for m in self.rx.finditer(text):
            # Insert the color escapes before and after the matched portion.
            # This is verbose but more efficient than regular concatenation.
            if not m.group():
                continue
            out.write(text[off : m.start()])
            out.write(self.ct)
            out.write(m.group())
            out.write(RESET)
            off = m.end()
        out.write(text[off:])
        ret = out.getvalue()
        out.close()
        return ret

    def __str__(self):
        return colornames[self.ck]


class unbuffered_stream(object):
    def __init__(self, istream):
        self.fd = istream.fileno()
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)
        self.fdlist = [self.fd]
        self.mask = (
            select.POLLIN | select.POLLHUP | select.POLLNVAL | select.POLLERR
        )
        self.poller = select.poll()
        self.poller.register(self.fd, self.mask)
        self.istream = istream
        self.closed = False

    def _get_chars(self):
        """Return all characters available on the input stream at this moment.
        Basically polls the input repeatedly, reading one character at a time
        until the input runs out of characters.
        If no characters are available right now, return the empty string.
        If the stream is closed or encountered an error, return None."""
        if self.closed:
            yield None

        rl, wl, xl = select.select(self.fdlist, self.fdlist, self.fdlist, 1)
        results = self.poller.poll(0)
        event = None
        for pollfd, pevent in results:
            if pollfd == self.fd:
                event = pevent
                break

        if event is not None:
            if event & select.POLLNVAL:
                raise OSError(errno.EINVAL, os.strerror(errno.EINVAL), self.fd)
            elif event & select.POLLIN:
                # yield available data
                yield self.istream.read()
            elif event & (select.POLLHUP | select.POLLERR):
                yield None

        # Nothing available at the moment.
        yield ""

    def __iter__(self):
        """Return an iterator yielding a sequence of unbuffered input
        characters roughly as they become available on the input stream.  The
        stream must support the fileno() operation and polling, and the output
        order is subject to CPU scheduling. The colorizing might be off if a
        pattern would require matching characters which end up split between
        two items. This is mostly for small, simple patterns in an interactive
        program (such as highlighting the prompt in an interactive Python
        session).
        """
        # Get available input characters in chunks.  Whence line is None, the
        # stream has been shutdown or experienced an error
        while True:
            # Don't eat the CPU spinning on empty input.
            time.sleep(0.10)
            for line in self._get_chars():
                # Yield non-empty sequences.
                # Empty sequences may appear when the stream has nothing for us yet
                # but we greedily checked anyway.
                if line is None:
                    break
                if line:
                    yield line
            if line is None:
                break


def select_lines(istream):
    """Return an iterator yielding a sequence of [line-buffered] input lines.
    Note if the input never ends with a new-line, it will never be yielded."""
    line = istream.readline()
    while line:
        yield line
        line = istream.readline()


def color(string="", color=None, reset=True):
    """Color a string with the given color. Keys are from colors or colornames in
    this module. By default, resets the color at the end of the string. Set
    reset=False to let the color seep past this string."""
    if color is None:
        ckey = RESET
    if not string:
        string = ""
    if not isinstance(string, str):
        string = str(string)
    if isinstance(color, str) and len(color) > 0:
        color = color[0]
    if color in revcolornames:
        color = revcolornames[color]
    if color in colors:
        ckey = colors[color]
    else:
        ckey = RESET
    if reset:
        rs = RESET
    else:
        rs = ""
    return ckey + string + rs


def recolor(patterns, istream=None, ostream=None, buffering=True):
    """
    Transform istream to ostream, colorizing lines matching patterns.

    Opts is a list of (color, regex) pairs. Each color should be either a key or
    a value from colornames specifying the coloring for text matching the
    pattern.

    If buffering is False, unbuffer the input stream by using non-blocking reads.
    In this case the stream must have an associated file descriptor which
    supports polling.
    """
    if istream is None:
        istream = sys.stdin
    if ostream is None:
        ostream = sys.stdout

    # list of ColorMatch objects
    matchers = list()
    for flag, regex in patterns:
        if flag in colornames:
            key = flag
        elif flag in revcolornames:
            key = revcolornames[flag]
        else:
            raise ValueError("bad color flag: " + repr(flag))
        rx = re.compile(regex)
        if not rx:
            raise ValueError("bad regex: " + repr(regex))
        matchers.append(ColorMatch(rx, key))

    lines = select_lines(istream)
    if not buffering:
        lines = unbuffered_stream(istream)

    for line in lines:
        for colormatch in matchers:
            line = colormatch.filter(line)

        ostream.write(line)
        ostream.flush()

    return 0
