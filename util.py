import math

# Normalize words, i.e. lowercase and strip spaces.
def normalize(word: str):
    word = word.lower()
    word = word.replace(' ', '')
    return word

# Print word and its length with optional coloring(s).
def print_word(word: str, bold=False, color=None):
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

# Print a list of words in columns
def tableize(word, matches, columns=4):
    chunk_size = math.ceil(len(matches)/columns)
    columns = [ matches[i*chunk_size:(i+1)*chunk_size] for i in range(0, columns) ]
    wordlengths = [ [ len(x) for x in col ] for col in columns ]
    col_lengths = [ max(x)+2 for x in wordlengths ]

    # Justify to column & color original word
    fmt = lambda s, l: Color.highlight(str.ljust(s, l), word, Color.YELLOW)

    for i in range(0, chunk_size):
        row_words = [ col[i] for col in columns if len(col) > i ]
        row = [ fmt(w, l) for (w, l) in zip(row_words, col_lengths) ]
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
    def highlight(s: str, substr: str, *args):
        index = s.find(substr)
        length = len(substr)

        prefix = s[:index]
        suffix = s[index+length:]

        return f"{prefix}{Color.fmt(substr, *args)}{suffix}"

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
