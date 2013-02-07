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

name_file = []   #this list will be populated by the specie names from the blast script
for defenition in list_checked_blast_results:
    name_file.append(defenition.split(';;'))  

#split the hit_def(from my_blast.xml)

# blast hits are used as search query
search_name=[]
for line in name_file:
    for line in line:
        c = line.find('"')
        lineb = line[c:]
        a = line.find(' ') # find the first whitespace in the description and split there
        namelinea = line[:a]
        line = line[a+1:]
        b = line.find(' ')
        namelineb = line[:b]
        lineb =lineb.strip('"') #strip any "blank" entries from the specie name list
        line = namelinea + ',' + lineb # + ' ' + namelineb 
        search_name.append(line) #append the stripped specie name(now only a specie name instead of the whole description

search_name = search_name[:(len(search_name)-1)]

#download the CITES appendices from the website if no local file is present, will be downloaded as a HTML page named: appendices.php
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
closere = re.compile('</td>')       # end tag, the function will stop printing if it finds this tag in the HTML source code 

z = []
x = []
for name in search_name: 
    b = name.find(',')
    pattern = name[:b]              #search query( specie name)
    regex = re.compile(pattern)
    i = 0                           #set index to 0

    def remove_tags(text):          #this function removes all HTML tags
        return TAG_RE.sub('', text)
    
    def remove_nbsp(text):                      #this function removes all whitespaces(&nbsp)
        return TAG_REnbsp.sub('', text)
    
    while i < len (lines):                      #while the index is smaller the the number of lines in the HTML page(CITES appendix)
        if regex.search(lines[i]) != None:      #search the appendix for the specie name provided by blast(and stripped earlier in this script)
            notags  = remove_tags(lines[i])
            nosnbsp = remove_nbsp(notags)       #remove HTML tags
            sys.stdout.write(nosnbsp)
            z.append(nosnbsp)                      
            x.append(name[b+1:] + "\n")         #append the name and entire line to x
            j = i
            
            
            while closere.search(lines[j]) == None:   #after searching for the specie name now we search for the close tag(the script will print everything between the specie name and the close tag
                j = j + 1
                notags2 = remove_tags(lines[j])
                nonbsp  = remove_nbsp(notags2)
                sys.stdout.write(nonbsp)
                z.append(nonbsp)                      #append the lines 2 till the end tag
                
        i = i + 1
sys.stdout.write(";\n")
sys.stdout.writelines(x)                              #pass the results to the shell to be used in the results table
logging.info("finished CITES_checker")