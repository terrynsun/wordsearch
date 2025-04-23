#!/usr/bin/env python3

import Levenshtein

import re

from wordlist import Wordlist
import util

def print_low_3s(wl: Wordlist):
    compiled_regex = re.compile("...")
    regex_match_fn = lambda x: compiled_regex.fullmatch(x)

    #matches = self.search(regex_match_fn, 50)
    matches = wl.low_only_search(regex_match_fn)

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

        util.tableize(None, acc, columns=8)
        print()

def v(word):
    mid = len(word)//2
    first = word[:mid]
    last = word[mid:]
    distance = Levenshtein.distance(first, last)
    return distance == 1 and len(word) > 8

# Dilly dally, willy nilly
def print_almost_matching_halves(wl: Wordlist):
    matches = wl.search(v, 50)
    ws = list(matches.keys())
    print('\n'.join(ws))

# yada yada
def print_matching_halves(wl: Wordlist):
    def match_fn(word):
        mid = len(word)//2
        first = word[:mid]
        last = word[mid:]
        return first == last

    matches = wl.search(match_fn, 50)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    print('\n'.join(ws))

def list_clubs(wl: Wordlist):
    words = ["book", "comedy", "country", "glee", "rotary", "sierra", "auto", "booster",
    "diners", "drama", "fan", "fight", "french", "golf", "kennel", "lions", "night",
    "strip", "wine", "beach"]

    for w in words:
        print(w)
        wl.query_sandwich(w, 40)
        print()

if __name__ == '__main__':
    wl = Wordlist()
    wl.load('../wordlist/')

    #print_matching_halves(wl)
    list_clubs(wl)
