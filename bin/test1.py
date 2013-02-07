#!/usr/bin/python2.7

import subprocess

process = subprocess.Popen(['python', 'test.py'], shell=False, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

process.stdin.write("alex\n")
output = process.stdout.readlines()
a = "".join(output)

print(a)
