#!/usr/bin/python2.7
'''
@author: Thomas Bolderink

this script searches the cites appendices (available at : http://www.cites.org/eng/app/appendices.php)
for hits on illegal species(?)


'''
import re

xml = open ("cites.php", "r")
lines = xml.readlines()
pattern = ("Moschus")
regex = re.compile(pattern)
closere = re.compile("</td>")
i = 0


TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

while i < len (lines):
    if regex.search(lines[i]) != None:
        #lines[i]= re.sub("</?[^\W].{0,10}?>", "", lines[i])
        #print lines[i]
        test = remove_tags(lines[i])
        print test
        j = i
        while closere.search(lines[j]) == None:
            #lines[j]= re.sub("</?[^\W].{0,10}?>", "", lines[j])
            j = j + 1
            test2 = remove_tags(lines[j])
            print test2
            
            #lines[j]= re.sub("</td>","",lines[j])
            #print lines[j]
    i = i + 1
        
        


       

