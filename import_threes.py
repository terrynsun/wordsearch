#!/usr/bin/env python3

import csv
import sys

import util

def output_word(word: str, score: int) -> None:
    print(f"{util.normalize(word)};{score}")

def load_csv(fname: str) -> None:
    wordlist = {}

    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # First header is just for notes in the doc
        _ = next(reader)

        # Second row gives scores
        scores = next(reader)

        for row in reader:
            for word, score in zip(row, scores):
                if word == '' or score == '':
                    continue

                wordlist[word] = score

    for word, score in sorted(wordlist.items()):
        output_word(word, int(score))

def main(args: list[str]) -> None:
    load_csv(args[0])

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
