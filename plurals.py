#!/usr/bin/env python3

from pluralizer import Pluralizer

from wordlist import Wordlist

# Prints words that are ranked at 50 where plurals are ranked at 40 or less
# STWL only right no
def find_missing_plurals():
    full_wordlist = Wordlist()
    full_wordlist.load('../gh/wordlist/000_peter_broda_full.txt')
    full_wordlist.load('../gh/wordlist/01_XwiWordList.txt')

    stwl = Wordlist()
    stwl.load('../gh/wordlist/00_spreadthewordlist.txt')

    pluralizer = Pluralizer()

    compiled_regex = re.compile(".+")
    regex_match_fn = lambda x: compiled_regex.fullmatch(x)
    matches = stwl.search(regex_match_fn, 50)
    sorted_matches = sorted(list(matches.keys()))

    for word in sorted_matches:
        new_word = None
        if pluralizer.is_singular(word):
            new_word = pluralizer.plural(word)
        elif pluralizer.is_plural(word):
            new_word = pluralizer.singular(word)

        if not new_word:
            continue

        stwl_contains, stwl_score = stwl.score(new_word, score_threshold=0)
        full_contains, _ = full_wordlist.score(new_word, score_threshold=0)

        # Skip small words (for now)
        if len(new_word) > 4:
            continue

        # If it's in STWL but higher than 50, it's already there.
        # If it's in STWL but lower than 50, it's valid.
        if stwl_contains:
            if stwl_score < 50:
                print(f'{new_word};50')
        # If it's not in STWL, it can be in any of the other lists at any score.
        elif full_contains:
            print(f'{new_word};50')
        # Else, it might not be a real word.

if __name__ == '__main__':
    find_missing_plurals()
