#!/usr/bin/python2.7
'''
this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)

Created on 7 Jan. 2013

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl
'''

#import the modules os to handle downloading, sys for input and output, logging for
#user information and BeautifulSoup for html parsing 
import sys, os, logging, argparse, re
from bs4 import BeautifulSoup

logging.basicConfig(level = logging.INFO)
list_checked_blast_results = sys.stdin.readlines()
name_file = []

try:
    php_doc = open ("appendices.php", "r")
except:
    logging.info('no local copy cites appendices, downloading from cites.org')
    os.system("wget http://www.cites.org/eng/app/appendices.php")
    php_doc = open ("appendices.php", "r")

logging.info('starting cites_check')
soup = BeautifulSoup(php_doc)

logging.info('parsing html')
list_cites = soup.find_all(['i','b','em'])
logging.info('finished parsing html') 


for defenition in list_checked_blast_results:
    name_file.append(defenition.split(';;'))


search_name=[]
for line in name_file:
    for line in line:
        c = line.find('"')
        lineb = line[c:]
        a = line.find(' ')
        namelinea = line[:a]
        line = line[a+1:]
        b = line.find(' ')
        namelineb = line[:b]
        lineb =lineb.strip('"')
        line = namelinea + ' ' + namelineb + ',' + lineb + '\n'
        search_name.append(line)
        

c = []
for name in search_name:
    for entry in list_cites:
        b = name.find(',')
        nameb = name[:b]
        a = entry.find(nameb)
        if a != -1:
            if name not in c:            
                c.append(name)
        else:
            pass


if len(c) != 0:
    #sys.stdout.write("the following species are found in the input file and on the cites list: \n")
    sys.stdout.writelines(c)
else:
    sys.stdout.write("n")
logging.info('finished cites_check')