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

MIN_IDENT = 97
MIN_COVER = 95
E_VALUE_THRESH = 0.04

for blast_record in NCBIXML.parse(result_handle):
    c1 = 0
    for alignment in blast_record.alignments:
        if c1 < 1:
            for hsp in alignment.hsps:
                ident = float(hsp.identities/(len(hsp.match)*0.01))
                cover = float(len(hsp.match)/(len(hsp.query)*0.01))
                if hsp.expect < E_VALUE_THRESH and ident > MIN_IDENT and cover > MIN_COVER:
                    print('****Alignment****')
                    print('sequence:'   , alignment.title)
                    print('length:'     , alignment.length)
                    print('% identity:' , ident)
                    print('e value:'    , hsp.expect)
                    print('% coverage'  , cover)
                    print(hsp.query[0:75] + '...')
                    print(hsp.match[0:75] + '...')
                    print(hsp.sbjct[0:75] + '...')
        c1 = c1 + 1
result_handle.close()

print("done 100%")