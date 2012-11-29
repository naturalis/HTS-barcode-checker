#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil take the blast results and change them into a more human friendly format.

dependencies:
Bio python
'''
from Bio.Blast import NCBIXML
import os

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all nececary files
'''
pwd = os.getcwd()
pwd = pwd.strip("/bin/Output")
pwd = pwd + "/data/test/"
os.chdir('/')
os.chdir(pwd)
result_handle = open("my_blast.xml", "r")
blast_records = NCBIXML.parse(result_handle)
b1 = 0

for blast_record in blast_records:
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            a1 = (hsp.identities/(alignment.length*0.01))
            a2 = (len(hsp.match)/(len(hsp.query)*0.01))
            b1 = b1 + 1
            print('****Alignment****')
            print('sequence:'   , alignment.title)
            print('length:'     , alignment.length)
            print('% identity:' , a1)
            print('e value:'    , hsp.expect)
            print('% coverage'  , a2)
            print(hsp.query[0:75] + '...')
            print(hsp.match[0:75] + '...')
            print(hsp.sbjct[0:75] + '...')

if b1 == 0:
    print("none")