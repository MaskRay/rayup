#!/usr/bin/env python3
#
#   Copyright (C) 2010, 2011 MaskRay (emacsray at gmail dot com)
#                               http://code.google.com/p/rayup/
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   ------------------------------------------------------------------------------
#
#   topcoder-data-parser
#           Parse "Examples" of Problem Statement or "System Test Results" of "Problem Statistics" into tests (some .in & .out files)

from sys import stdin, stdout, stderr
from optparse import OptionParser
import os, re

def parser(t, f):
    inStr = False
    inNum = False
    ex = []
    block = [ex]
    for ch in t:
        if ch == '"':
            if not inStr:
                block[-1].append('')
            inStr = not inStr
        elif inStr:
            block[-1][-1] += ch
        elif ch in '-.0123456789':
            if inNum:
                block[-1][-1] += ch
            else:
                block[-1].append(ch)
                inNum = True
        else:
            inNum = False
            if ch == '{':
                block[-1].append([])
                block.append(block[-1][-1])
            elif ch == '}':
                block.pop()
    for obj in ex:
        if type(obj) == str:
            print(obj, file=f)
        else:
            print(len(obj), file=f)
            for e in obj:
                print(e, file=f)

def parseWeb(lines, options):
    s = ''
    for line in lines:
        line = line.strip()
        match = re.match('''(\d+)\)''', line)
        if match:
            testid = match.groups()[0]
            f = open('%s/%s.%s.in' % (options.path, options.classname, testid), 'w')
            continue
        match = re.match('Returns: (.*)', line)
        if match:
            parser(s, f)
            s = ''
            f = open('%s/%s.%s.out' % (options.path, options.classname, testid), 'w')
            parser(match.groups()[0], f)
            f.close()
            continue
        if 'f' in dir() and not f.closed:
            s += line

def parseArchive(lines, options):
    dataid = 0
    for line in lines:
        tokens = list(filter(lambda x: x.strip() != '', line.split('\t')))
        if len(tokens) != 3: continue
        with open('%s/%s.%d.in' % (options.path, options.classname, dataid), 'w') as f:
            parser(tokens[0], f)
        with open('%s/%s.%d.out' % (options.path, options.classname, dataid), 'w') as f:
            parser(tokens[1], f)
        dataid += 1

if __name__ == '__main__':
    def main():
        usage = '''usage: %prog CLASS [DIR]
        CLASS    - class name
        DIR      - where to contain these parsed data (default '/tmp')'''
        optionparser = OptionParser(usage=usage)
        (options, args) = optionparser.parse_args()
        if len(args) < 1 or len(args) > 2:
            optionparser.print_usage()
            exit(1)
        if len(args) < 2:
            args.append('/tmp')
        options.classname = args[0]
        options.path = os.path.expanduser(args[1])

        flag = False
        lines = stdin.readlines()
        for line in lines:
            if re.match('''\d\)''', line):
                flag = True
                break
        if flag:
            parseWeb(lines, options)
        else:
            parseArchive(lines, options)
        
    main()
