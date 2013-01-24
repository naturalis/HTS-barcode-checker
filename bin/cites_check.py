#!/usr/bin/python2.7
'''
this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)

Created on 7 Jan. 2013
Author: Thomas Bolderink
E-mail: thomas_bolderink@hotmail.com / s1047798@student.hsleiden.nl
Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl
'''

#import the modules os to handle downloading, sys for input and output, logging for
#user information and BeautifulSoup for html parsing 
import sys
import os
import logging
import re
#from bs4 import BeautifulSoup

logging.basicConfig(level = logging.INFO)
list_checked_blast_results = sys.stdin.readlines()
name_file = []

try:
    php_doc = open ("cites.php", "r")
except:
    logging.info('no local copy cites list, downloading from cites.org')
    os.system("wget http://www.cites.org/eng/app/appendices.php")
    php_doc = open ("appendices.php", "r")

logging.info('starting cites_check')

'''
soup = BeautifulSoup(php_doc)

logging.info('soup')
list_cites = soup.find_all(['i','b','em'])
logging.info('/soup') 

for defenition in list_checked_blast_results:
    name_file.append(defenition.split(';;'))
'''
search_name=[]
for line in name_file:
    for line in line:
        a = line.find(' ')
        namelinea = line[:a]
        line = line[a+1:]
        b = line.find(' ')
        namelineb = line[:b]
        line = namelinea + ' ' + namelineb
        search_name.append(line)
'''
c = []
for name in search_name:
    for entry in list_cites:
        a = entry.find(name)
        if a != -1:
            if name not in c:
                c.append(name)

if len(c) != 0:
    print("the following species are found in the input file and on the cites list:")
    for line in c:
        print(line)
else:
    print("no hits were found on the cites list")
logging.info('finished cites_check')'''


#xml = open ("cites.php", "r")  # retrieve the cites HTML file
lines = php_doc.readlines()
pattern = search_name          #blast hits are used as search query 
regex = re.compile(pattern)
closere = re.compile("</td>")
i = 0


TAG_REnbsp = re.compile(r'&nbsp;')   # to be removed piece of HTML(nbsp) code(for some reason it wont remove all hmtl content in one statement
TAG_RE = re.compile(r'<[^>]+>')      # remove all HTML tags
#'<[^>]+>'
def remove_tags(text):
    return TAG_RE.sub('', text)


def remove_nbsp(text):
    return TAG_REnbsp.sub('', text)


for name in search_name:
    
    while i < len (lines):
        if regex.search(lines[i]) != None:
            notags  = remove_tags(lines[i])
            nosnbsp = remove_nbsp(notags)
            print nosnbsp
            j = i
        
        
        while closere.search(lines[j]) == None:
            j = j + 1
            notags2 = remove_tags(lines[j])
            nonbsp  = remove_nbsp(notags2)
            print nonbsp
            
    i = i + 1