#!/usr/bin/python2.7
'''
this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)


'''
import sys
import os
import logging

logging.basicConfig(level = logging.INFO)
list_checked_blast_results = sys.stdin.readlines()
flag = sys.argv[1]

if flag == '-l':
    filepath = sys.argv[2]
    a = open('{filepath}'.format(filepath = filepath), 'r')
else:
    try:
        a = open ("appendices.php", "r")
    except:
        logging.info('no local copy cites list, downloading from cites.org')
        os.system("wget http://www.cites.org/eng/app/appendices.php")
        a = open ("appendices.php", "r")

html = a.readlines()

logging.info('starting cites_check')
namefile = list_checked_blast_results[0].split(";;")
search_name=[]
for line in namefile:
    a = line.find(' ')
    namelinea = line[:a]
    line = line[a+1:]
    b = line.find(' ')
    namelineb = line[:b]
    line = namelinea + ' ' + namelineb
    search_name.append(line)
#print(search_name)

names_cites_list = []
for line in html:
    a = line.find('<i>')
    b = line.find('</i>')
    name = line[a+3:b]
    if name != '':
        names_cites_list.append(name)
#print(names_cites_list)
    
c = []
length = len(search_name)
for name in search_name:
    if name in names_cites_list:                                               #compare the blast results with the cites list 
        c.append(name)
    else:
        pass

if len(c) != 0:
    print("found illegal substance in sample :")
    for line in c:
        print(line)
else:
    print("no hits were found on the cites list")
logging.info('finished cites_check')