# Usage

REPL for searching a directory of crossword wordlists. May add other tools as we
go.

## Todo

Bugs:
- Highlight should use a regex w/ captures. Right now it doesn't take into
    account order, and can accidentally highlight the `m` added by the color
    codes.

Behavior:
- Fix ^C behavior: https://stackoverflow.com/a/37380019

New functionality:
- Downscore / upscore / write to file
- Convert personal list to wordlist. Display notes from personal list.
