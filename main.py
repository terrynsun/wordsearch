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

    def default(self, arg: str):
        self.wordlist.query(arg)

    def do_g(self, arg: str):
        self.wordlist.google(arg)

    def do_r(self, arg: str):
        self.wordlist.search_regex(arg)

    def do_EOF(self, _: str):
        print()
        return True

    def precmd(self, line: str):
        return line

def main(args):
    wl = Wordlist()
    wl.load_files(args)

    Shell(wl).cmdloop()

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("expected wordlist files to load")
        exit(1)

    main(args[1:])
