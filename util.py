from typing import Any
import re
from typing import Callable

def regex_match_bool(regex_str: str) -> Callable[[str], bool]:
    compiled_regex = re.compile(regex_str)

    return lambda s: compiled_regex.fullmatch(s) is not None

# Normalize words, i.e. lowercase and strip spaces.
def normalize(word: str) -> str:
    word = word.lower()
    word = word.replace(' ', '')
    return word

# Print word and its length with optional coloring(s).
def display_word(word: str, bold: bool = False, color: int | None = None
                 ) -> None:
    normalized_word = normalize(word)
    s = f"{normalized_word} ({len(normalized_word)})"

    colors = []
    if bold:
        colors.append(Color.BOLD)

    if color:
        colors.append(color)

    print(Color.fmt(s, *colors))

# Print a result from a wordlist, i.e. score and filename pair.
def print_result(score: int, filename: str, color: int | None = None) -> None:
    print(Color.fmt(f"{score:2d}: {filename}", color))

def split_array(a: list[Any], n: int) -> list[list[Any]]:
    k, m = divmod(len(a), n)
    cur = 0
    ret: list[list[Any]] = []

    for i in range(n):
        row = a[cur:cur + k]
        cur += k

        if i < m:
            row.append(a[cur])
            cur += 1

        ret.append(row)

    return ret

# Print a list of words in columns
def tableize(highlight_word: str | list | None, matches: list[str],
             num_columns: int = 4) -> None:
    if len(matches) == 0:
        return

    # highlight one or more words; if highlight_word is a string, turn it into
    # an array
    to_highlight = []
    if isinstance(highlight_word, str):
        to_highlight = [highlight_word]
    elif isinstance(highlight_word, list):
        to_highlight = highlight_word

    columns = split_array(matches, num_columns)

    wordlengths = [[len(x) for x in col] for col in columns]
    col_lengths = [max(x) + 2 for x in wordlengths if len(x) > 0]

    # Pad to column len & color original word
    def tablefmt(word: str, col_len: int) -> str:
        padded_word = str.ljust(word, col_len)
        return Color.highlight_many(padded_word, to_highlight, Color.YELLOW)

    for i in range(len(columns[0])):
        row_words = [col[i] for col in columns if len(col) > i]
        row = [tablefmt(w, l) for (w, l) in zip(row_words, col_lengths)]
        print(''.join(row))

# Helper class containing color constants and some colorizing functions
class Color:
    BLACK = 30
    # RED = 31
    # Nonstandard: ANSI calls 91 "bright red" but the solarized scheme is a
    # muted red
    RED = 91
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    # Nonstandard: ANSI calls 91 "bright cyan" but the solarized scheme is grey
    GREY = 96

    BOLD = 1
    UNDER = 4

    RESET = '\033[0m'

    @staticmethod
    def fmt(s: str, *args: int) -> str:
        if len(args) == 0 or args[0] is None:
            return s

        fmtstring = ''.join([f"\033[{n}m" for n in args])
        return f"{fmtstring}{s}\033[0m"

    @staticmethod
    def highlight(full: str, substr: str, *args: int) -> str:
        if substr not in full:
            return full

        index = full.find(substr)
        length = len(substr)

        prefix = full[:index]
        suffix = full[index + length:]

        return f"{prefix}{Color.fmt(substr, *args)}{suffix}"

    @staticmethod
    def highlight_many(full: str, substrs: list[str], *args: int) -> str:
        # This is currently like O(n^2 * m)
        word = full

        for substr in substrs:
            word = Color.highlight(word, substr, *args)

        return word

    @staticmethod
    def bold(s: str) -> str:
        return Color.fmt(s, Color.BOLD)

    @staticmethod
    def red(s: str) -> str:
        return Color.fmt(s, Color.RED)

    @staticmethod
    def green(s: str) -> str:
        return Color.fmt(s, Color.GREEN)

    @staticmethod
    def blue(s: str) -> str:
        return Color.fmt(s, Color.BLUE)

    @staticmethod
    def grey(s: str) -> str:
        return Color.fmt(s, Color.GREY)
