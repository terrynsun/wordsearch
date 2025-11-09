import re
import os

import sys
from pathlib import Path

import util
from util import Color

class Wordlist():
    # PUBLIC INTERFACE #
    ####################
    #
    # (Python has no public/private marker. Conventionally you prepend
    # underscores to mark privacy.)

    def __init__(self) -> None:
        # self.data is a dict { filename: wordlist }
        # wordlist is a dict { word: score }
        self.data: dict[str, dict[str, int]] = {}

        # Wordlists are ordered, and they must be searched in this order. Later
        # lists have higher precedence.
        self.filelist: list[str] = []

    # Loads a list of files (i.e. from command line invocation)
    def load(self, files):
        if type(files) is list:
            for file in files:
                self.load_single_path(file)
        else:
            self.load_single_path(files)

        # We want to search wordlists in a specific order to handle overrides.
        self.filelist.sort()

        print('Files loaded, highest precedence last:', file=sys.stderr)
        for f in self.filelist:
            print(f"- {f}", file=sys.stderr)

        print('', file=sys.stderr)

    def ignore(self, filename):
        if filename in self.filelist:
            self.filelist.remove(filename)

    # INTERFACE #
    #############
    # Functions called from the REPL or list.py

    def query(self, word: str) -> None:
        """A basic query searches the given word as exact match first, then
        searches for entries that contain word as a substring.
        """
        normalized_word = util.normalize(word)

        # Prints matching wordlists, and scores.
        results = self.match_exact(normalized_word, True)
        self.print_wordlist_matches(word, results)

        # Prints entries as a table.
        substr_results = self.search_substring(normalized_word)

        num_columns: int = 4

        term_size: os.terminal_size = os.get_terminal_size()
        max_num_results = term_size.lines * num_columns
        # Subtract 2 to account for space between columns
        max_word_length = int(term_size.columns / num_columns - 2)

        self.print_result_table(substr_results, word, 40, num_columns,
                                max_num_results, max_word_length)

    SPLIT_ASCII_WORDS = re.compile(r'\W')

    def query_regex(self, regex: str, score_minimum: int = 40):
        """Regex search using Python's regex search engine"""
        compiled_regex = re.compile(regex)
        regex_match_fn = lambda x: compiled_regex.fullmatch(x)

        matches = self.search(regex_match_fn, score_minimum)
        if len(matches) == 0:
            return

        long_matches = filter(lambda word: len(word) > 8 and len(word) < 15, matches)

        highlights = self.SPLIT_ASCII_WORDS.split(regex)

        util.tableize(highlights, list(long_matches))

    def query_sandwich(self, word: str, score_minimum: int = 40):
        if len(word) < 2:
            print("need at least two characters to query sandwich")
            return

        # track seen words so we don't report them repeatedly
        seen: set[str] = set()

        for i in range(1, len(word)):
            prefix, suffix = word[:i], word[i:]
            regex = f"{prefix}.+{suffix}"

            compiled_regex = re.compile(regex)
            regex_match_fn = lambda x: compiled_regex.fullmatch(x)

            matches = self.search(regex_match_fn, score_minimum).keys()

            # remove result if it contains the original word
            filtered_words = [x for x in matches
                              if word not in x and x not in seen]

            seen.update(matches)

            if len(filtered_words) == 0:
                continue

            filtered_words.sort(key=lambda x: len(x))

            util.tableize([prefix, suffix], list(filtered_words))

            print()

    def list_3s(self):
        compiled_regex = re.compile("...")
        regex_match_fn = lambda x: compiled_regex.fullmatch(x)

        matches = self.search(regex_match_fn, 50)

        sorted_matches = sorted(list(matches.keys()))

        # remove words that don't start with letters
        while sorted_matches[0][0] != 'a':
            sorted_matches.pop(0)

        # split by first letter
        for letter in range(ord('a'), ord('z') + 1):
            c = chr(letter)
            acc = []
            while len(sorted_matches) > 0 and sorted_matches[0][0] == c:
                acc.append(sorted_matches.pop(0))

            util.tableize(None, acc, columns=8)
            print()

    def score(self, word: str, score_minimum=0):
        """Return whether a word exists, and its score.

        Used for wordlist comparison/plural generation."""
        max_score = 0
        contains = False

        for file in self.filelist:
            filelist = self.data[file]
            if word in filelist and filelist[word] >= score_minimum:
                max_score = filelist[word]
                contains = True

        return contains, max_score

    def explain(self, word):
        """Print a couple links so you can look up the word easily."""
        util.display_word(word, True)

        word = word.replace(' ', '+')

        print(f"- https://www.google.com/search?q={word}")
        print(f"- https://en.wikipedia.org/w/index.php?title=Special%3ASearch&search={word}")
        print(f"- https://www.etymonline.com/word/{word}")
        print(f"- https://www.merriam-webster.com/dictionary/{word}")
        print("- https://www.crosserville.com/search/theme")

    # OUTPUT #
    ##########
    def print_wordlist_matches(self, word: str,
                               results: list[tuple[int, str]],
                               bold: bool = False) -> None:
        # - Prints word in red if not found, teal if found.
        # - Highest precedence is printed last. Overwritten word lists are
        # printed in grey.
        if len(results) == 0:
            util.display_word(word, bold, Color.RED)
            return

        util.display_word(word, bold, Color.CYAN)

        # Grey for overwritten lists
        for (score, file) in results[:-1]:
            util.print_result(score, file, Color.GREY)

        # Regular color for final result
        score, file = results[-1]
        util.print_result(score, file)

    def print_result_table(self, matches: dict[str, int], original_word: str,
                           score_minimum: int = 40,
                           num_columns: int | None = None,
                           max_result_count: int | None = None,
                           max_word_length: int | None = None) -> None:
        # TODO: better way to filter?
        if max_word_length:
            matches = {k: v for k, v in matches.items()
                       if len(k) < max_word_length}

        if len(matches) == 0:
            print('')
            return

        # Too many words, just report number of matches.
        if max_result_count and len(matches) > max_result_count:
            print(f"\n& omitting {len(matches)} other words with {Color.green(original_word)} as substring ({score_minimum}+)")
            return

        # Prints table of matching words
        if len(matches) > 10:
            print(f"\n& found {len(matches)} other words with {Color.green(original_word)} as substring ({score_minimum}+):")
            util.tableize(original_word, list(matches.keys()))
            return

        print('')
        print('-------')

        # Extended results (prints the score as well)
        results = sorted(matches.items(), key=lambda x: (x[1], x[0]))
        for match, score in results:
            print(f"{score} {Color.highlight(match, original_word, Color.YELLOW)} ({len(match)})")

    # FILE MANAGEMENT #
    ###################
    @staticmethod
    def parse_wordlist_file(path):
        name = path.parts[-1]

        words = {}

        with open(path) as f:
            for line in f:
                line = line.strip()
                split = line.split(';')

                # If there's a malformed line, print error and ignore.
                if len(split) < 2:
                    print(f"{path}: invalid line: {line}", file=sys.stderr)
                    continue

                word = split[0]
                score = split[1]
                # Currently dropping any comments

                normalized_word = util.normalize(word)
                words[normalized_word] = int(score)

        return name, words

    # This can follow a directory one level down and parse its files. It loads
    # one path, which can be a directory or a single file. But it doesn't
    # recurse more than once.
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

    # SEARCHING #
    #############
    # TODO unused variable, lint check
    def match_exact(self, word: str, original=False) -> list[tuple[int, str]]:
        """For a single word, return every list it's in and its score."""
        # [ (score, filename) ]
        results: list[tuple[int, str]] = []

        for file in self.filelist:
            filelist = self.data[file]
            if word in filelist:
                score = filelist[word]
                results.append((score, file))

        return results

    def search_substring(self, word: str, score_minimum: int = 40) -> dict[str, int]:
        substring_match_fn = lambda x: word in x

        matches = self.search(substring_match_fn, score_minimum)

        # Remove original word so we don't print it later
        if word in matches:
            del matches[word]

        return matches

    def search(self, match_fn, score_minimum: int = 40,
               score_maximum: int | None = None) -> dict[str, int]:
        """Searches all wordlists, using a provided match_fn lambda."""
        matches = {}

        # Checks against each file, instead of a compiled list.
        # Thus, if the score meets the criteria in ANY list, it will be
        # reported, even if it's later overriden.
        for file in self.filelist:
            filelist = self.data[file]
            for k, v in filelist.items():
                if match_fn(k):
                    if v < score_minimum:
                        continue

                    if score_maximum and v > score_maximum:
                        continue

                    matches[k] = v

        return matches
