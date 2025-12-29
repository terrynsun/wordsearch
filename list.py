#!/usr/bin/env python3

from wordlist import Wordlist
import util
from util import Color

def print_low_3s(wl: Wordlist) -> None:
    matches = wl.search_regex('...', 0, 40)

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

        util.tableize(None, acc, num_columns=8)
        print()

# import Levenshtein
# def v(word: str) -> bool:

#     mid = len(word) // 2
#     first = word[:mid]
#     last = word[mid:]
#     distance = Levenshtein.distance(first, last)
#     return distance == 1 and len(word) > 8

# Dilly dally, willy nilly
# def print_almost_matching_halves(wl: Wordlist) -> None:
#     matches = wl.search(v, 50)
#     ws = list(matches.keys())
#     print('\n'.join(ws))

# yada yada
def print_matching_halves(wl: Wordlist) -> None:
    def match_fn(word: str) -> bool:
        mid = len(word) // 2
        first = word[:mid]
        last = word[mid:]
        return first == last

    matches = wl.search(match_fn, 50)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    print('\n'.join(ws))

def list_screens(wl: Wordlist) -> None:
    words = ['blue', 'green', 'full', 'flat', 'silk', 'split', 'sun', 'touch',
             'window', 'lock', 'big']

    for w in words:
        print(w)
        wl.query_sandwich(w, 40)

        # remove results too short or long
        # filtered_words = [x for x in filtered_words
        # if len(x) < 10 or len(x) > 16]

        print()

def list_clubs(wl: Wordlist) -> None:
    words = ["book", "comedy", "country", "glee", "rotary", "sierra", "auto",
             "booster", "diners", "drama", "fan", "fight", "french", "golf",
             "kennel", "lions", "night", "strip", "wine", "beach"]

    for w in words:
        print(w)
        wl.query_sandwich(w, 40)

        # remove results too short or long
        # filtered_words = [ x for x in filtered_words if len(x) == 12]

        print()

def list_t_to_dos(wl: Wordlist) -> None:
    def match_fn(word: str) -> bool:
        if 'b' in word:
            new_word = word.replace('b', 'd')
            return wl.contains(new_word)
        return False

    matches = wl.search(match_fn, 50)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    print('\n'.join(ws))

def print_upside_downs(wl: Wordlist) -> None:
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

    def reverse(word: str) -> str:
        acc = []
        for letter in word:
            if letter not in upside_down_dict:
                return ''
            acc.append(upside_down_dict[letter])

        new_word = ''.join(acc[::-1])
        return new_word

    def match_fn(word: str) -> bool:
        if len(word) < 4:
            return False

        new_word = reverse(word)
        if not new_word:
            return False
        return wl.contains(new_word, score_minimum=40)

    matches = wl.search(match_fn, 40)
    ws = list(matches.keys())
    ws = sorted(ws, key=lambda x: len(x))
    for w in ws:
        print('{} - {}'.format(w, reverse(w)))

def double_cross(wl: Wordlist) -> None:
    regex_str = "hot.*"

    matches = wl.search_regex(regex_str, 0)
    ws = list(matches.keys())
    for w in ws:
        suffix = w[3:]
        double_word = 'sour' + suffix
        if wl.contains(double_word):
            print(w, double_word)

def just_add_water(wl: Wordlist) -> None:
    target_word = 'air'
    regex_str = ".+" + target_word + ".+"

    matches = wl.search_regex(regex_str, 0)
    ws = list(matches.keys())
    for w in ws:
        new = w.replace(target_word, '')
        if wl.contains(new):
            print(Color.highlight(w, target_word, Color.YELLOW), new)

def hotandsour(wl: Wordlist, w1: str, w2: str) -> None:
    w1_len = len(w1)
    regex_w1 = f"{w1}.+"
    matches_w1 = wl.search_regex(regex_w1, 50)
    w1_suffixes = [w[w1_len:] for w in matches_w1.keys() if len(w) > w1_len + 2]

    w2_len = len(w2)
    regex_w2 = f"{w2}.+"
    matches_w2 = wl.search_regex(regex_w2, 50)
    w2_suffixes = [w[w2_len:] for w in matches_w2.keys() if len(w) > w2_len + 2]

    # These endings are conjugations/declensions, not other words, so we omit
    # them.
    common_endings = ['ing', 'ings', 'son', 'ness', 'edon', 'ingon', 'sof',
                      'ish', 'est', 'ingup', 'iest', 'edup', 'ies', 'sup',
                      'ier']

    words = []
    for w1_word in w1_suffixes:
        for w2_word in w2_suffixes:
            if w1_word in common_endings or w2_word in common_endings:
                continue

            new_word = w1_word + w2_word
            contains, score = wl.score(new_word)
            if contains and score > 40:
                words.append((w1_word, w2_word, new_word, len(new_word)))

    words.sort(key=lambda t: len(t[2]))
    print('\n'.join([f'{t[3]} {t[2]}\t// {w1} {t[0]} + {w2} {t[1]}'
                     for t in words]))

def eggdrop(wl: Wordlist) -> None:
    target_word = 'egg'
    regex_str = ".*" + target_word + ".*"

    matches = wl.search_regex(regex_str, 0)
    ws = list(matches.keys())
    print('\n'.join(ws))

if __name__ == '__main__':
    wl = Wordlist()
    wl.load('../gh/wordlist/')
    wl.query_sandwich('open')
    # list_screens(wl)

    # hotandsour(wl, 'hot', 'sour')
    # hotandsour(wl, 'thick', 'thin')
