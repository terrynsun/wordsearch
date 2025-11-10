#!/usr/bin/env python3

import Levenshtein

import re

from wordlist import Wordlist
import util
from util import Color

def print_low_3s(wl: Wordlist):
    matches = wl.search_regex('...', 0)

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

def v(word):
    mid = len(word) // 2
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
        mid = len(word) // 2
        first = word[:mid]
        last = word[mid:]
        return first == last

    matches = wl.search(match_fn, 50)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    print('\n'.join(ws))

def list_clubs(wl: Wordlist):
    words = ["book", "comedy", "country", "glee", "rotary", "sierra", "auto",
             "booster", "diners", "drama", "fan", "fight", "french", "golf",
             "kennel", "lions", "night", "strip", "wine", "beach"]

    for w in words:
        print(w)
        wl.query_sandwich(w, 40)

        # remove results too short or long
        # filtered_words = [ x for x in filtered_words if len(x) == 12]

        print()

def list_t_to_dos(wl: Wordlist):
    def match_fn(word):
        if 'b' in word:
            new_word = word.replace('b', 'd')
            return wl.contains(new_word)

    matches = wl.search(match_fn, 50)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    print('\n'.join(ws))

def print_upside_downs(wl: Wordlist):
    upside_down_dict = {
        's': 's',
        'i': 'i',
        'o': 'o',
        'n': 'n',
        'x': 'x',
        'z': 'z',
        'h': 'h',

        'm': 'w',
        'w': 'm',
    }
    # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def reverse(word):
        acc = []
        for letter in word:
            if letter not in upside_down_dict:
                return None
            acc.append(upside_down_dict[letter])

        new_word = ''.join(acc[::-1])
        return new_word

    def match_fn(word):
        if len(word) < 4:
            return False

        new_word = reverse(word)
        if not new_word:
            return False
        return wl.contains(new_word, score_threshold=40)

    matches = wl.search(match_fn, 40)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    for w in ws:
        print('{} - {}'.format(w, reverse(w)))

def double_cross(wl: Wordlist):
    regex_str = "sweet.*"

    matches = wl.search_regex(regex_str, 0)
    ws = list(matches.keys())
    for w in ws:
        suffix = w[5:]
        double_word = 'sour' + suffix
        if wl.contains(double_word):
            print(w, double_word)

def just_add_water(wl: Wordlist):
    target_word = 'air'
    regex_str = ".+" + target_word + ".+"

    matches = wl.search_regex(regex_str, 0)
    ws = list(matches.keys())
    for w in ws:
        new = w.replace(target_word, '')
        if wl.contains(new):
            print(Color.highlight(w, target_word, Color.YELLOW), new)

if __name__ == '__main__':
    wl = Wordlist()
    wl.load('../gh/wordlist/')

    # print_matching_halves(wl)
    # print_upside_downs(wl)
    # just_add_water(wl)
