import re

from pathlib import Path
from collections import Counter

import util
from util import Color

class Wordlist():
    ## PUBLIC INTERFACE ##
    ######################
    #
    # (Python has no public/private marker. Conventionally you prepend
    # underscores to mark privacy.)

    def __init__(self):
        # self.data is a dict { filename: wordlist }
        # wordlist is a dict { word: score }
        self.data = {}

        # Wordlists are ordered, and they must be searched in this order. Later
        # lists have higher precedence.
        self.filelist = []

    # Loads a list of files (i.e. from command line invocation)
    def load(self, files):
        if type(files) == list:
            for file in files:
                self.load_single_path(file)
        else:
            self.load_single_path(files)

        # We want to search wordlists in a specific order to handle overrides.
        self.filelist.sort()

        print('Files loaded, highest precedence last:')
        for f in self.filelist:
            print(f"- {f}")

        print('')

    # A basic query searches the given word as exact match first, then search
    # for containing substrings.
    def query(self, word):
        normalized_word = util.normalize(word)

        self.match_exact(normalized_word, True)

        self.search_substring(normalized_word)

    SPLIT_ASCII_WORDS = re.compile(r'\W')

    # Regex search using Python's regex search engine
    def query_regex(self, regex: str, score_threshold: int=40):
        compiled_regex = re.compile(regex)
        regex_match_fn = lambda x: compiled_regex.fullmatch(x)

        matches = self.search(regex_match_fn, score_threshold)
        if len(matches) == 0:
            return

        highlights = self.SPLIT_ASCII_WORDS.split(regex)

        util.tableize(highlights, list(matches.keys()))

    # Regex search using Python's regex search engine
    def query_sandwich(self, word: str, score_threshold: int=40):
        if len(word) < 2:
            print("need at least two characters to query sandwich")
            return

        for i in range(1, len(word)):
            prefix, suffix = word[:i], word[i:]
            regex = f"{prefix}.*{suffix}"
            self.query_regex(regex, score_threshold)
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
        for letter in range(ord('a'), ord('z')+1):
            c = chr(letter)
            acc = []
            while len(sorted_matches) > 0 and sorted_matches[0][0] == c:
                acc.append(sorted_matches.pop(0))

            util.tableize('', acc, columns=8)
            print()

    # Print a couple links so you can look up the word easily.
    def explain(self, word):
        util.display_word(word, True)

        word = word.replace(' ', '+')

        print(f"- https://www.google.com/search?q={word}")
        print(f"- https://en.wikipedia.org/w/index.php?title=Special%3ASearch&search={word}")
        print(f"- https://www.etymonline.com/word/{word}")
        print(f"- https://www.merriam-webster.com/dictionary/{word}")
        print(f"- https://www.crosserville.com/search/theme")

    ## FILE MANAGEMENT ##
    #####################

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
                    print(f"{path}: invalid wordlist line: {line}")
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

    ## WORDLIST STUFF ##
    ####################

    # Prints each wordlist score distribution
    def count_scores(self):
        for file in self.filelist:
            c = Counter()

            filelist = self.data[file]
            for _, v in filelist.items():
                c[v] += 1

            print(f"{file}\n{c}\n")

    ## SEARCHING ##
    ###############

    # Search a single word and prints its score in every wordlist it's found in.
    # - Prints word in red if not found, teal if found.
    # - Highest precedence is printed last. Overwritten word lists are printed
    # in grey.
    def match_exact(self, word: str, original=False):
        # [ (score, filename) ]
        results: list = []

        for file in self.filelist:
            filelist = self.data[file]
            if word in filelist:
                score = filelist[word]
                results.append((score, file))

        if len(results) == 0:
            util.display_word(word, original, Color.RED)
            return

        util.display_word(word, original, Color.CYAN)

        # Grey for overwritten lists
        for (score, file) in results[:-1]:
            util.print_result(score, file, Color.GREY)

        # Regular color for final result
        score, file = results[-1]
        util.print_result(score, file)

    # Looks for the word as a substring (not exact match). If there's a wieldy
    # number of results, uses match_exact to print the wordlist results for all
    # of them. Otherwise, if there's a medium number of results, print them.
    # Otherwise, if there's just too many, only give the number of results
    # found.
    def search_substring(self, word: str, score_threshold: int=40):
        substring_match_fn = lambda x: word in x

        matches = self.search(substring_match_fn, score_threshold)

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

    # Searches all wordlists, using a provided match_fn lambda.
    # The original word is also passed in so we can use it to highlight results.
    def search(self, match_fn, score_threshold: int=40):
        matches = {}

        for file in self.filelist:
            filelist = self.data[file]
            for k, v in filelist.items():
                if match_fn(k) and v >= score_threshold:
                    matches[k] = v

        return matches
