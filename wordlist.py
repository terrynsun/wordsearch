import re

from pathlib import Path

import util
from util import Color

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
        self.filelist.sort()

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
    def search_substring(self, word: str, score_threshold: int=40):
        substring_match_fn = lambda x: word in x

        self.search(word, substring_match_fn, score_threshold)

    # Regex search using Python's regex search engine
    def search_regex(self, regex: str, score_threshold: int=40):
        compiled_regex = re.compile(regex)
        regex_match_fn = lambda x: compiled_regex.match(x)

        self.search('', regex_match_fn, score_threshold)

    def search(self, word, match_fn, score_threshold: int=40):
        matches = {}

        for file in self.filelist:
            filelist = self.data[file]
            for k, v in filelist.items():
                if match_fn(k) and v >= score_threshold:
                    matches[k] = v

        # Remove original word so we don't print it later
        if word in matches:
            del matches[word]

        if len(matches) == 0:
            print('')
            return

        # Too many words, just report number of matches.
        if len(matches) > 200:
            print(f"\n& found {len(matches)} other words with {Color.green(word)} as substring ({score_threshold}+)")
            return

        # Prints table of matching words
        if len(matches) > 10:
            print(f"\n& found {len(matches)} other words with {Color.green(word)} as substring ({score_threshold}+):")
            util.tableize(word, list(matches.keys()))
            return

        print('')
        print('-------')

        # Extended results (prints the score as well)
        results = sorted(matches.items(), key=lambda x: (x[1], x[0]))
        for match, score in results:
            print(f"{score} {Color.highlight(match, word, Color.YELLOW)} ({len(match)})")

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
        print(f"- https://www.crosserville.com/search/theme")

