#!/usr/bin/env python3

import sys
import cmd

from wordlist import Wordlist
from util import Color

class Shell(cmd.Cmd):
    intro = 'Welcome.'
    prompt = Color.blue(Color.bold('»»» '))
    file = None

    def __init__(self, wordlist: Wordlist):
        self.wordlist = wordlist
        super(Shell, self).__init__()

    def default(self, arg: str) -> None:
        '''
        Enter a bare word to do a basic query, with full match and substring
        search.

        If this contains a wildcard (period), guess that it should be a regex
        search.
        '''

        if '.' in arg:
            return self.do_r(arg)

        self.wordlist.query(arg)

    def do_e(self, arg: str) -> None:
        '''
        Generate a few links to websites for definitions of the word
        '''
        self.wordlist.explain(arg)

    def do_r(self, arg: str) -> None:
        '''
        Run a regex search. In fullmatch mode; use .* at beginning or end to
        allow partial match.
        '''
        self.wordlist.query_regex(arg)

    def do_s(self, arg: str) -> None:
        '''
        Search for surrounds.
        '''
        self.wordlist.query_sandwich(arg)

    def do_EOF(self, _: str) -> bool:
        print()
        return True

    def precmd(self, line: str) -> str:
        return line

def main(args: list[str]) -> None:
    wl = Wordlist()
    wl.load(args)

    Shell(wl).cmdloop()

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
