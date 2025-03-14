import math

# Normalize words, i.e. lowercase and strip spaces.
def normalize(word: str):
    word = word.lower()
    word = word.replace(' ', '')
    return word

# Print word and its length with optional coloring(s).
def display_word(word: str, bold=False, color=None):
    s = f"{word} ({len(word)})"

    colors = []
    if bold:
        colors.append(Color.BOLD)

    if color:
        colors.append(color)

    print(Color.fmt(s, *colors))

# Print a result from a wordlist, i.e. score and filename pair.
def print_result(score: int, filename: str, color=None):
    print(Color.fmt(f"{score:2d}: {filename}", color))

# https://stackoverflow.com/a/2135920
def split_array(a, n):
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

# Print a list of words in columns
def tableize(highlight_word, matches, columns=4):
    if len(matches) == 0:
        return

    # highlight one or more words; if highlight_word is a string, turn it into
    # an array
    to_highlight = [highlight_word] if type(highlight_word) == str else highlight_word

    columns = split_array(matches, columns)

    wordlengths = [ [ len(x) for x in col ] for col in columns ]
    col_lengths = [ max(x)+2 for x in wordlengths if len(x) > 0 ]

    # Pad to column len & color original word
    def tablefmt(word, col_len):
        padded_word = str.ljust(word, col_len)
        return Color.highlight_many(padded_word, to_highlight, Color.YELLOW)

    for i in range(len(columns[0])):
        row_words = [ col[i] for col in columns if len(col) > i ]
        row = [ tablefmt(w, l) for (w, l) in zip(row_words, col_lengths) ]
        print(''.join(row))

# Helper class containing color constants and some colorizing functions
class Color:
    BLACK = 30
    # RED = 31
    # Nonstandard: ANSI calls 91 "bright red" but the solarized scheme uses a muted red
    RED = 91
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    # Nonstandard: ANSI calls 91 "bright cyan" but the solarized scheme uses a grey
    GREY = 96

    BOLD = 1
    UNDER = 4

    RESET = '\033[0m'

    @staticmethod
    def fmt(s: str, *args):
        if len(args) == 0 or args[0] == None:
            return s

        fmtstring = ''.join([ f"\033[{n}m" for n in args ])
        return f"{fmtstring}{s}\033[0m"

    @staticmethod
    def highlight(full: str, substr: str, *args):
        if substr not in full:
            return full

        index = full.find(substr)
        length = len(substr)

        prefix = full[:index]
        suffix = full[index+length:]

        return f"{prefix}{Color.fmt(substr, *args)}{suffix}"

    @staticmethod
    def highlight_many(full: str, substrs: list[str], *args):
        # This is currently like O(n^2 * m)
        word = full

        for substr in substrs:
            word = Color.highlight(word, substr, *args)

        return word

    @staticmethod
    def bold(s: str):
        return Color.fmt(s, Color.BOLD)

    @staticmethod
    def red(s: str):
        return Color.fmt(s, Color.RED)

    @staticmethod
    def green(s: str):
        return Color.fmt(s, Color.GREEN)

    @staticmethod
    def blue(s: str):
        return Color.fmt(s, Color.BLUE)

    @staticmethod
    def grey(s: str):
        return Color.fmt(s, Color.GREY)
