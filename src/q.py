# Copyright 2012 Google Inc.  All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at: http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distrib-
# uted under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied.  See the License for
# specific language governing permissions and limitations under the License.

# FILE MODIFIED BY Anselm Kiefner 2023

"""Quick and dirty debugging output for tired programmers.

All output goes to /tmp/q, which you can watch with this shell command:

    tail -f /tmp/q

If TMPDIR is set, the output goes to $TMPDIR/q.

To print the value of foo, insert this into your program:

    import q; q(foo)

To print the value of something in the middle of an expression, insert
"q()", "q/", or "q|".  For example, given this statement:

    file.write(prefix + (sep or '').join(items))

...you can print out various values without using any temporary variables:

    file.write(prefix + q(sep or '').join(items))  # prints (sep or '')
    file.write(q/prefix + (sep or '').join(items))  # prints prefix
    file.write(q|prefix + (sep or '').join(items))  # prints the arg to write

To trace a function's arguments and return value, insert this above the def:

    import q
    @q

To start an interactive console at any point in your code, call q.d():

    import q; q.d()
"""

import ast
import code
import functools
import inspect
import re
import sys
from datetime import datetime
from pathlib import Path
from pydoc import TextRepr
from time import time

__author__ = "Ka-Ping Yee <ping@zesty.ca>"

# WARNING: Horrible abuse of sys.modules, __call__, __div__, __or__, inspect,
# sys._getframe, and more!  q's behaviour changes depending on the text of the
# source code near its call site.  Don't ever do this in real code!

ESCAPE_SEQUENCES = ["\x1b[0m"] + ["\x1b[3%dm" % i for i in range(1, 7)]
NORMAL, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = ESCAPE_SEQUENCES

BASESTRING_TYPES = (str, bytes)
TEXT_TYPES = (str,)

path = Path(sys.argv[0]).parents[0]
path = path / "logs"
path.mkdir(exist_ok=True)
OUTPUT_PATH = path / "watnu.log"
OUTPUT_PATH.touch()


class FileWriter(object):
    """An object that appends to or overwrites a single file."""

    def __init__(self, path):
        self.path = path

    def write(self, mode, content):
        if "b" not in mode:
            mode = f"{mode}b"
        if isinstance(content, BASESTRING_TYPES) and isinstance(content, TEXT_TYPES):
            content = content.encode("utf-8")
        with open(self.path, mode) as f:
            f.write(content)


class Writer:
    """Abstract away the output pipe, timestamping, and color support."""

    def __init__(self, file_writer, color=False):
        self.color = color
        self.file_writer = file_writer
        self.gap_seconds = 2
        self.start_time = time()
        self.last_write = 0

    def write(self, chunks):
        """Writes out a list of strings as a single timestamped unit."""
        if not self.color:
            chunks = [x for x in chunks if not x.startswith("\x1b")]
        content = "".join(chunks)

        now = time()
        prefix = "%4.1fs " % ((now - self.start_time) % 100)
        indent = " " * len(prefix)
        if self.color:
            prefix = self.YELLOW + prefix + self.NORMAL
        if now - self.last_write >= self.gap_seconds:
            prefix = "\n" + prefix
        self.last_write = now

        output = prefix + content.replace("\n", "\n" + indent)
        self.file_writer.write("a", output + "\n")


class Stanza:
    """Abstract away indentation and line-wrapping."""

    def __init__(self, indent=0, width=280 - 7):
        self.chunks = [" " * indent]
        self.indent = indent
        self.column = indent
        self.width = width

    def newline(self):
        if len(self.chunks) > 1:
            self.column = self.width

    def add(self, items, sep="", wrap=True):
        """Adds a list of strings that are to be printed on one line."""
        items = list(map(str, items))
        size = sum(len(x) for x in items if not x.startswith("\x1b"))
        if wrap and self.column > self.indent and self.column + len(sep) + size > self.width:
            self.chunks.append(sep.rstrip() + "\n" + " " * self.indent)
            self.column = self.indent
        else:
            self.chunks.append(sep)
            self.column += len(sep)
        self.chunks.extend(items)
        self.column += size


class Q(object):
    # The debugging log will go to this file; temporary files will also have
    # this path as a prefix, followed by a timestamp excel-style as name.
    # if sys.platform.startswith("win"):
    #     home = os.getenv('HOME')
    #     tmp = os.path.join(HOME, 'tmp')
    #     if not os.path.exists(tmp):
    #         os.mkdir(tmp)
    #     OUTPUT_PATH = os.path.join(tmp, 'q')
    # else:
    #     OUTPUT_PATH = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'q')

    def __init__(self):
        self.writer = Writer(FileWriter(OUTPUT_PATH))
        self.indent = 0
        # in_console tracks whether we're in an interactive console.
        # We use it to display the caller as "<console>" instead of "<module>".
        self.in_console = False

        self.writer.write(
            f"""==========================
{excel_style_datetime(datetime.now())}
==========================
"""
        )

    def unindent(self, lines):
        """Removes any indentation that is common to all of the given lines."""
        indent = min(len(re.match(r"^ *", line).group()) for line in lines)
        return [line[indent:].rstrip() for line in lines]

    def safe_repr(self, value):
        result = TextRepr().repr(value)
        if isinstance(value, BASESTRING_TYPES) and len(value) > 80:
            # If the string is big, save it to a file for later examination.
            if isinstance(value, TEXT_TYPES):
                value = value.encode("utf-8")
            path = OUTPUT_PATH.parents[0] / ("%08d.txt" % excel_style_datetime(datetime.now()))
            FileWriter(path).write("w", value)
            result += f" (file://{str(path)})"
        return result

    def get_call_exprs(self, line):
        """Gets the argument expressions from the source of a function call."""
        line = line.lstrip()
        try:
            tree = ast.parse(line)
        except SyntaxError:
            return None
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                offsets = [arg.col_offset for arg in node.args]
                if node.keywords:
                    line = line[: node.keywords[0].value.col_offset]
                    line = re.sub(r"\w+\s*=\s*$", "", line)
                else:
                    line = re.sub(r"\s*\)\s*$", "", line)
                offsets.append(len(line))
                return [line[offsets[i] : offsets[i + 1]].rstrip(", ") for i in range(len(node.args))]

    def show(self, func_name, values, labels=None):
        """Prints out nice representations of the given values."""
        s = Stanza(self.indent)
        if func_name == "<module>" and self.in_console:
            func_name = "<console>"
        s.add([f"{func_name}: "])
        reprs = map(self.safe_repr, values)
        sep = ""
        if labels:
            for label, repr in zip(labels, reprs):
                s.add([f"{label}=", CYAN, repr, NORMAL], sep)
                sep = ", "
        else:
            for repr in reprs:
                s.add([CYAN, repr, NORMAL], sep)
                sep = ", "
        self.writer.write(s.chunks)

    def trace(self, func):
        """Decorator to print out a function's arguments and return value."""

        def wrapper(*args, **kwargs):
            # Print out the call to the function with its arguments.
            s = Stanza(self.indent)
            s.add([GREEN, func.__name__, NORMAL, "("])
            s.indent += 4
            sep = ""
            for arg in args:
                s.add([CYAN, self.safe_repr(arg), NORMAL], sep)
                sep = ", "
            for name, value in sorted(kwargs.items()):
                s.add([f"{name}=", CYAN, self.safe_repr(value), NORMAL], sep)
                sep = ", "
            s.add(")", wrap=False)
            self.writer.write(s.chunks)

            # Call the function.
            self.indent += 2
            try:
                result = func(*args, **kwargs)
            except:
                # Display an exception.
                self.indent -= 2
                etype, evalue, etb = sys.exc_info()
                info = inspect.getframeinfo(etb.tb_next, context=3)
                s = Stanza(self.indent)
                s.add([RED, "!> ", self.safe_repr(evalue), NORMAL])
                s.add(["at ", info.filename, ":", info.lineno], " ")
                lines = self.unindent(info.code_context)
                firstlineno = info.lineno - info.index
                fmt = f"%{len(str(firstlineno + len(lines)))}d"
                for i, line in enumerate(lines):
                    s.newline()
                    s.add(
                        [
                            i == info.index and MAGENTA or "",
                            fmt % (i + firstlineno),
                            i == info.index and "> " or ": ",
                            line,
                            NORMAL,
                        ]
                    )
                self.writer.write(s.chunks)
                raise

            # Display the return value.
            self.indent -= 2
            s = Stanza(self.indent)
            s.add([GREEN, "-> ", CYAN, self.safe_repr(result), NORMAL])
            self.writer.write(s.chunks)
            return result

        return functools.update_wrapper(wrapper, func)

    def __call__(self, *args):
        """If invoked as a decorator on a function, adds tracing output to the
        function; otherwise immediately prints out the arguments."""
        info = inspect.getframeinfo(sys._getframe(1), context=9)

        lines = info.code_context[: info.index + 1] if info.code_context else [""]
        # If we see "@q" on a single line, behave like a trace decorator.
        for line in lines:
            if line.strip() in ("@q", "@q()") and args:
                return self.trace(args[0])

        # Otherwise, search for the beginning of the call expression; once it
        # parses, use the expressions in the call to label the debugging
        # output.
        for i in range(1, len(lines) + 1):
            labels = self.get_call_exprs("".join(lines[-i:]).replace("\n", ""))
            if labels:
                break
        self.show(info.function, args, labels)
        return args and args[0]

    def __truediv__(self, arg):  # a tight-binding operator
        """Prints out and returns the argument."""
        info = inspect.getframeinfo(sys._getframe(1))
        self.show(info.function, [arg])
        return arg

    __or__ = __truediv__  # a loose-binding operator
    __name__ = "Q"  # App Engine's import hook dies if this isn't present

    def d(self, depth=1):
        """Launches an interactive console at the point where it's called."""
        info = inspect.getframeinfo(sys._getframe(1))
        self.actually_log(info, "Interactive console opened")
        frame = sys._getframe(depth)
        env = frame.f_globals.copy()
        env.update(frame.f_locals)
        self.indent += 2
        self.in_console = True
        code.interact(f"Python console opened by q.d() in {info.function}", local=env)
        self.in_console = False
        self.indent -= 2

        self.actually_log(info, "Interactive console closed")

    def actually_log(self, info, msg):
        result = Stanza(self.indent)
        result.add([f"{info.function}: "])
        result.add([MAGENTA, msg, NORMAL])
        self.writer.write(result.chunks)

        return result


def excel_style_datetime(now: datetime) -> float:
    """
    Build a float representing the current time in the excel format.
    First 4 digits are the year, the next two are the month, the next two are the day followed
    by a decimal point, then time in fraction of the day.

    Args:
        now (datetime): datetime instance to be converted

    Returns:
        float: Excel style datetime
    """
    return int(f"{now.year:04d}{now.month:02d}{now.day:02d}") + round(
        (now.hour * 3600 + now.minute * 60 + now.second) / 86400, 6
    )


q = Q()

q.__dict__.update(dict(globals()))
sys.modules["q"] = q