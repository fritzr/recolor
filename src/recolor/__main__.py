#!/usr/bin/env python
#
#
# Simple sed-like script to filter terminal color escapes into any text stream.
#


import signal
import sys
import os

from recolor import (
    recolor, colors, colornames, colorkeys, RESET, RED, GREEN, CYAN, UNDER
)


def usage(errstr=""):
    fmt = dict()
    for k in colorkeys:
        key = k
        if k.isupper():
            key = "b" + k.lower()
        fmt[key] = colors[k] + colornames[k] + RESET

    fmt["prog"] = RED + os.path.basename(sys.argv[0]) + RESET
    fmt["options"] = GREEN + "OPTIONS" + RESET
    fmt["colorspecs"] = CYAN + "COLORSPECS" + RESET
    fmt["flags"] = UNDER + colorkeys + RESET

    sys.stderr.write(
        """\
Usage: {prog} [{options}] [{colorspecs}...]

Apply color filters to the input according to the {colorspecs}.
Each COLORSPEC is one of [-{flags}] followed by an optional REGEX.

Where the regex is matched in the input it will be colored the corresponding
color. If the regex has a match group (parenthesis), only the [first] group
will be colorized.

{options}:
    -i	interactive mode: do not line-buffer the input

{colorspecs}:
    -r	{r}		-R	{br}		-k	{k}
    -g	{g}		-G	{bg}		-K	{bk}
    -b	{b}		-B	{bb}		-w	{w}
    -c	{c}		-C	{bc}		-W	{bw}
    -y	{y}		-Y	{by}		-u	{u}
    -m	{m}		-M	{bm}
""".format(
            **fmt
        )
    )
    if errstr:
        sys.stderr.write("\n%s\n" % (errstr,))
    sys.stderr.flush()
    sys.exit(1)


# each color gets an optional regex argument
shortopts = "hi" + "::".join(colorkeys) + "::"


def parse_args(args=None):
    """Parse the arguments according to our usage and return (opts, args)
    as getopt would. If args is not given, use sys.argv[1:] by default."""
    if args is None:
        args = sys.argv[1:]
    from getopt import getopt

    return getopt(args, shortopts)


def sigpipe(*args):
    """Called when SIGPIPE is received."""
    sys.stdout.flush()
    sys.stdout.close()
    sys.exit(0)


def main(args=None):
    # catch SIGPIPE and close nicely
    signal.signal(signal.SIGPIPE, sigpipe)

    opts, _ = parse_args(args)
    matchers = list()
    buffering = True
    for opt, arg in opts:
        opt = opt.lstrip("-")
        if len(opt) != 1:
            usage()
        elif opt == "h":
            usage()
        # Interactive mode - use unbuffered (non-blocking) reads
        elif opt == "i":
            buffering = False
        elif opt not in colorkeys:
            getopt.error("invalid color key " + repr(opt))
        else:
            matchers.append((opt, arg))

    return recolor(
        matchers, istream=sys.stdin, ostream=sys.stdout, buffering=buffering
    )


if __name__ == "__main__":
    sys.exit(main())
