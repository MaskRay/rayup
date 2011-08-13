#!/usr/bin/env python

import sys

def get_first(production, terminals, nonterminals):
    first = {'epsilon' : set(['epsilon'])}
    for token in terminals:
        first[token] = set([token])
    for token in nonterminals:
        first[token] = set()
        for product in production[token]:
            if product == ['epsilon']:
                first[token].add('epsilon')
                break

    while True:
        flag = False
        for token in nonterminals:
            for product in production[token]:
                for token2 in product:
                    tmp = first[token] | first[token2]
                    if first[token] != tmp:
                        first[token] = tmp
                        flag = True
                    if 'epsilon' not in first[token2]:
                        break
                else:
                    first[token2].add('epsilon')
        if not flag: break
    return first

def get_follow(production, terminals, nonterminals, start, first): 
    follow = {'epsilon': set()}
    for token in terminals | nonterminals:
        follow[token] = set()
    follow[start] = set(['$'])
    while True:
        flag = False
        for token in nonterminals:
            for product in production[token]:
                tmp = follow[product[-1]] | follow[token]
                if tmp != follow[product[-1]]:
                    follow[product[-1]] = tmp
                    flag = True
                for i in xrange(len(product)-2, -1, -1):
                    tmp = (follow[product[i]] | first[product[i+1]])
                    if 'epsilon' in tmp:
                        tmp.remove('epsilon')
                    if tmp != follow[product[i]]:
                        follow[product[i]] = tmp
                        flag = True
                    if 'epsilon' in first[product[i+1]]:
                        tmp = follow[product[i]] | follow[product[i+1]]
                        if tmp != follow[product[i]]:
                            follow[product[i]] = tmp
                            flag = True
        if not flag: break
    return follow

def get_production():
    production, start = {}, None
    print '--- Production ---'
    with open('temp', 'r') as file:
        for line in file:
            if line[0] == '#': continue
            items = line.split()
            for i, item in enumerate(items):
                if i == 0:
                    if item not in production:
                        production[item] = []
                    if not start:
                        start = item
                elif i > 1:
                    production[items[0]].append(items[i:])
                    print items[0], '->',
                    for token in items[i:]:
                        print token,
                    print
                    break
    print
    return production, start

def get_predictive_parser(production, terminals, first, follow):
    parser = {}
    for token in production:
        parser[token] = {}
        for token2 in terminals | set(['$']):
            parser[token][token2] = None
    for token, products in production.items():
        for product in products:
            for token2 in product:
                for token3 in first[token2]:
                    if token3 != 'epsilon':
                        if parser[token][token3] and parser[token][token3] != product:
                            sys.stderr.write('error: given context-free language is ambigious.')
                            exit(1)
                        parser[token][token3] = product
                if 'epsilon' not in first[token2]:
                    break
            else:
                for token2 in follow[token]:
                    if token2 != '$':
                        for token3 in first[token2]:
                            if token3 != 'epsilon':
                                if parser[token][token3] and parser[token][token3] != product:
                                    sys.stderr.write('error: given context-free language is ambigious.')
                                    exit(1)
                                parser[token][token3] = product
                if '$' in follow[token]:
                    parser[token]['$'] = product
    return parser

def do_predictive_parse(parser, terminals, start, line):
    print 'do'
    stack, i = ['$', start], 0
    line = line.split() + ['$']
    while len(stack) > 1:
        if stack[-1] == line[i]:
            stack.pop()
            i += 1
        elif stack[-1] in terminals or not parser[stack[-1]][line[i]]:
            sys.stderr.write('error')
            exit(2)
        else:
            tmp = parser[stack[-1]][line[i]]
            print stack[-1], '->', tmp
            stack.pop()
            stack.extend(tmp[::-1])
        while stack[-1] == 'epsilon':
            stack.pop()

def main():
    production, start = get_production()
 
    nonterminals, terminals = set(production), set()
    for value in production.values():
        for tokens in value:
            for token in tokens:
                if token != 'epsilon' and token not in nonterminals:
                    terminals.add(token)

    print '--- terminals ---'
    for token in terminals:
        print token,
    print '\n'

    print '--- nonterminals ---'
    for token in nonterminals:
        print token,
    print '\n'

    first = get_first(production, terminals, nonterminals)
    print '--- FIRST ---'
    for token in terminals | nonterminals:
        print token, ':',
        for token2 in first[token]:
            print token2,
        print
    print

    follow = get_follow(production, terminals, nonterminals, start,
            first)
    print '--- FOLLOW ---'
    for token in terminals | nonterminals:
        print token, ':',
        for token2 in follow[token]:
            print token2,
        print

    print '---predictive parser---'
    parser = get_predictive_parser(production, terminals, first, follow)
    for token in nonterminals:
        for token2 in terminals | set(['$']):
            print token, token2, parser[token][token2]

    while True:
        try:
            do_predictive_parse(parser, terminals, start, raw_input())
        except Exception:
            break

if __name__ == '__main__':
    main()
