#!/usr/bin/python2.7
'''
@author: Thomas Bolderink

this script searches the cites appendices(html file) (available at : http://www.cites.org/eng/app/appendices.php)
for hits on the cites list and extracts the hit and description 


'''
import re

xml = open ("cites.php", "r")
lines = xml.readlines()
pattern = ("Moschus")
regex = re.compile(pattern)
closere = re.compile("</td>")
i = 0


TAG_REnbsp = re.compile(r'&nbsp;')
TAG_RE = re.compile(r'<[^>]+>')
#'<[^>]+>'
def remove_tags(text):
    return TAG_RE.sub('', text)


def remove_nbsp(text):
    return TAG_REnbsp.sub('', text)

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
        
        


       

