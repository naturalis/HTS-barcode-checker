#!/usr/bin/python2.7
'''
this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)


'''
import sys
import os


os.system("wget http://www.cites.org/eng/app/appendices.php")
a = open ("appendices.php", "r")
b = a.read  

cites_lijst = sys.stdin.readlines()

namefile = cites_lijst[0].split(";")

search_name = [p.split()[1] for p in namefile]

#print search_name
for i in namefile:
    if search_name in b :                                               #compare the blast results with the cites list 
        print("found illegal substance in sample :")                #return the match
        print(search_name)
    else:
        print("no hits were found on the cites list")

