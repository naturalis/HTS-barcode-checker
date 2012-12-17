#!/usr/bin/python2.7
'''
this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)


'''
import os
import sys


good_blast    = sys.stdin.readlines()                               # this receives the titles of the alignments that passed the quality control

a = os.system("wget http://www.cites.org/eng/app/appendices.php")   #retrieve the cites HTML list
results = good_blast

for i in results:
    if results in a :                                               #compare the blast results with the cites list 
        print("found illegal substance in sample :")                #return the match
        print(results)
    else:
        print("no hits were found on the cites list")