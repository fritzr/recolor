# recolor

Regular Expression Color-izer.

Add color to a command's output by matching portions of lines with
regular expressions.

## Installation

May be installed via `pip install recolor`.

## Usage

```
Usage: colorize.py [OPTIONS] [COLORSPECS...]

Apply color filters to the input according to the COLORSPECS.
Each COLORSPEC is one of [-gbcymkwRGBCYMKWu] followed by an optional REGEX.

Where the regex is matched in the input it will be colored the corresponding
color. If the regex has a match group (parenthesis), only the [first] group
will be colorized.

OPTIONS:
    -i	interactive mode: do not line-buffer the input

COLORSPECS:
    -r	red		-R	bold red		-k	black
    -g	green		-G	bold green		-K	bold black
    -b	blue		-B	bold blue		-w	white
    -c	cyan		-C	bold cyan		-W	bold white
    -y	yellow		-Y	bold yellow		-u	underline
    -m	magenta		-M	bold magenta
```

## Examples

TODO
