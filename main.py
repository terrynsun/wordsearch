#!/usr/bin/env python3

import sys
import cmd
import math
from pathlib import Path

import util

class Wordlist():
    def __init__(self):
        self.data = {}
        self.filelist = []

    @staticmethod
    def parse_wordlist_file(path):
        name = path.parts[-1]

        words = {}

        with open(path) as f:
            for line in f:
                # Fails if a file doesn't contain this format.
                split = line.strip().split(';')
                if len(split) < 2:
                    print("invalid wordlist line:", line)
                    continue

                word = split[0]
                score = split[1]
                # Currently dropping any comments

                normalized_word = util.normalize(word)
                words[normalized_word] = int(score)

        return name, words

    # This can follow a directory one level down and parse its files. It loads
    # one path, not a single file. But it doesn't recurse more than once.
    def load_single_path(self, path):
        file = Path(path)

        if file.is_file():
            name, file_list = Wordlist.parse_wordlist_file(file)
            self.filelist.append(name)
            self.data[name] = file_list

        elif file.is_dir():
            for child in file.iterdir():
                name, file_list = Wordlist.parse_wordlist_file(child)
                self.filelist.append(name)
                self.data[name] = file_list

        else:
            print(f"file not found: {path}")
            exit(1)

    # Loads a list of files (i.e. from command line invocation)
    def load_files(self, files):
        for file in files:
            self.load_single_path(file)

        # We want to search wordlists in a specific order to handle overrides.
        # Special case STWL so it's lowest priority.
        self.filelist.sort(key=lambda x: '0' if x == 'spreadthewordlist.txt' else x)

        print('Files loaded, highest precedence last:')
        for f in self.filelist:
            print(f"- {f}")
        print('')

    # Print word and its length with optional coloring(s).
    def print_word(self, word: str, bold=False, color=None):
        s = f"{word} ({len(word)})"

        colors = []
        if bold:
            colors.append(Color.BOLD)

        if color:
            colors.append(color)

        print(Color.fmt(s, *colors))

    # Print a result from a wordlist, i.e. score and filename pair.
    def print_result(self, score: int, filename: str, color=None):
        print(Color.fmt(f"{score:2d}: {filename}", color))

    # Search a single word and print results.
    # - Prints word in red if not found, teal if found.
    # - Highest precedence is printed last. Overwritten word lists are printed
    # in grey.
    def match_exact(self, word: str, original=False):
        results = []
        for file in self.filelist:
            filelist = self.data[file]
            if word in filelist:
                score = filelist[word]
                results.append((score, file))

        if len(results) == 0:
            self.print_word(word, original, Color.RED)
            return
        else:
            self.print_word(word, original, Color.CYAN)

        for (score, file) in results[:-1]:
            self.print_result(score, file, Color.GREY)

        score, file = results[-1]
        self.print_result(score, file)

    # Looks for the word as a substring (not exact match). If there's a wieldy
    # number of results, uses match_exact to print the wordlist results for all
    # of them. Otherwise, if there's a medium number of results, print them.
    # Otherwise, if there's just too many, only give the number of results
    # found.
    def search_substring(self, word: str):
        matches = {}

        for file in self.filelist:
            filelist = self.data[file]
            for k, v in filelist.items():
                if word in k and v >= 40:
                    matches[k] = v

        # Remove original word so we don't print it later
        if word in matches:
            del matches[word]

        if len(matches) == 0:
            print('')
            return

        if len(matches) > 100:
            print(f"\n& found {len(matches)} other words with {Color.green(word)} as substring (40+ only)")
            return

        if len(matches) > 10:
            print(f"\n& found {len(matches)} other words with {Color.green(word)} as substring (40+ only):")
            Wordlist.tableize(word, list(matches.keys()))
            return

        print('')
        print('-------')

        results = sorted(matches.items(), key=lambda x: (x[1], x[0]))
        for match, score in results:
            print(f"{score} {Color.highlight(match, word, Color.YELLOW)} ({len(match)})")

    @staticmethod
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

    # Searches the given word as exact match first, then search for containing
    # substrings.
    def query(self, word):
        normalized_word = util.normalize(word)

        self.match_exact(normalized_word, True)

        self.search_substring(normalized_word)

    # Print a couple links so you can look up the word easily.
    def google(self, word):
        self.print_word(word, True)

        word = word.replace(' ', '+')

        print(f"- https://www.google.com/search?q={word}")
        print(f"- https://en.wikipedia.org/w/index.php?title=Special%3ASearch&search={word}")
        print(f"- https://www.etymonline.com/word/{word}")
        print(f"- https://www.merriam-webster.com/dictionary/{word}")

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

class Shell(cmd.Cmd):
    intro = 'Welcome.'
    prompt = Color.blue(Color.bold('»»» '))
    file = None

    def __init__(self, wordlist: Wordlist):
        self.wordlist = wordlist
        super(Shell, self).__init__()

    def default(self, arg: str):
        self.wordlist.query(arg)

    def do_g(self, arg: str):
        self.wordlist.google(arg)

    def do_EOF(self, _: str):
        print()
        return True

    def precmd(self, line: str):
        return line

def main(args):
    wl = Wordlist()
    wl.load_files(args)

    Shell(wl).cmdloop()

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
