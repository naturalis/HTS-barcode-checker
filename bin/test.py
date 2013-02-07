#!/usr/bin/python2.7

import sys

name = sys.stdin.readline()
sys.stdout.write('Message to {name}'.format(name = name))
print("done")