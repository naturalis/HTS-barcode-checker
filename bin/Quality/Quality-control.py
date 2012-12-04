#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil filter the blast results on E-value and bit-score.

coverage 95%
identity 97%

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
pwd = pwd.strip("/bin/Quality")
pwd = pwd + "/data/test/"
os.chdir('/')
os.chdir(pwd)

result_handle = open("my_blast.xml".format(pwd = pwd), "r")

E_VALUE_THRESH = 0.04
MIN_IDENT = 97
MIN_COVER = 95
c1 = 1

for blast_record in NCBIXML.parse(result_handle):
    c2 = 0
    result_blast_record = open("out{number}.txt".format(number = c1), "a")
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01))
            cover = float(len(hsp.match)/(len(hsp.query)*0.01))
            if hsp.expect < E_VALUE_THRESH and ident > MIN_IDENT and cover > MIN_COVER:
                if c2 < 15:
                    if alignment.title == "":
                        pass
                    else:
                        result_blast_record.write(alignment.title)
                        #print(hsp.expect)
                        #print(cover, ident)
                        result_blast_record.write("\n")
                        c2 = c2 + 1
    result_blast_record.close()

    c1 = c1 + 1

result_handle.close()
print("done 75%")