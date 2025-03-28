#!/usr/bin/env python3

import csv
import sys

import util

def output_word(word, score):
    print(f"{util.normalize(word)};{score}")

def load_csv(fname):
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile)
        # Header is just for notes in the doc
        _ = next(reader)

        # Second row gives scores
        scores = next(reader)

        for row in reader:
            for word, score in zip(row, scores):
                if word == '' or score == '':
                    continue

                output_word(word, score)

def main(args):
    load_csv(args[0])

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
