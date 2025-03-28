#!/usr/bin/env python3

import csv
import sys

import util

SCORE = 75

def output_word(word, score):
    print(f"{util.normalize(word)};{score}")

def load_csv(fname):
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile)
        # Read header
        headers = next(reader)
        variant_col = headers.index('Variants')

        for row in reader:
            # Ignore empty lines (they exist in the spreadsheet for convenience)
            if row[0] == '':
                continue

            output_word(row[0], SCORE)
            variants = row[variant_col]
            if variants:
                for v in variants.split(','):
                    output_word(v.strip(), SCORE)

def main(args):
    load_csv(args[0])

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
