#!/usr/bin/env python3

import csv
import sys

import util

SCORE = 75

def output_word(word, score, notes):
    if notes != '':
        print(f"{word};{score};{notes}")
    else:
        print(f"{word};{score}")

def load_csv(fname):
    wordlist = {}

    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # Read header
        headers = next(reader)
        variant_col = headers.index('Variants')
        notes_col = headers.index('Notes')

        for row in reader:
            word = util.normalize(row[0])
            # Ignore empty lines (they exist in the spreadsheet for convenience)
            if word == '':
                continue

            notes = row[notes_col]

            wordlist[word] = (SCORE, notes)

            variants = row[variant_col]
            if variants:
                for v in variants.split(','):
                    wordlist[util.normalize(v)] = (SCORE, notes)

    for word, (score, notes) in sorted(wordlist.items()):
        output_word(word, score, notes)

def main(args):
    load_csv(args[0])

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
