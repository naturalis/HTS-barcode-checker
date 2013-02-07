#!/usr/bin/python2.7
'''
@author: Thomas Bolderink

test script


this script searches the cites appendices(html file) (available at : http://www.cites.org/eng/app/appendices.php)
for hits on the cites list and extracts the hit and description 


'''
import re, sys, logging, os

logging.basicConfig(level = logging.INFO)

list_checked_blast_results = sys.stdin.readlines()

logging.info("starting CITES_checker")

name_file = []
for defenition in list_checked_blast_results:
    name_file.append(defenition.split(';;'))

# blast hits are used as search query
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
        line = namelinea + ',' + lineb # + ' ' + namelineb 
        search_name.append(line)

search_name = search_name[:(len(search_name)-1)]

try:
    php_doc = open ("appendices.php", "r")
except:
    logging.info('no local copy cites appendices, downloading from cites.org')
    os.system("wget http://www.cites.org/eng/app/appendices.php")
    php_doc = open ("appendices.php", "r")
lines = php_doc.readlines()
php_doc.close() 

TAG_REnbsp = re.compile('&nbsp;')   # to be removed piece of HTML(nbsp) code(for some reason it wont remove all hmtl content in one statement
TAG_RE = re.compile('<[^>]+>')      # remove all HTML tags
closere = re.compile('</td>')

z = []
x = []
for name in search_name:
    b = name.find(',')
    pattern = name[:b]
    regex = re.compile(pattern)
    i = 0    

    def remove_tags(text):
        return TAG_RE.sub('', text)
    
    def remove_nbsp(text):
        return TAG_REnbsp.sub('', text)
    
    while i < len (lines):
        if regex.search(lines[i]) != None:
            notags  = remove_tags(lines[i])
            nosnbsp = remove_nbsp(notags)
            sys.stdout.write(nosnbsp)
            z.append(nosnbsp)
            x.append(name[b+1:] + "\n")
            j = i
            
            
            while closere.search(lines[j]) == None:
                j = j + 1
                notags2 = remove_tags(lines[j])
                nonbsp  = remove_nbsp(notags2)
                sys.stdout.write(nonbsp)
                z.append(nonbsp)
                
        i = i + 1
sys.stdout.write(";\n")
sys.stdout.writelines(x)
logging.info("finished CITES_checker")