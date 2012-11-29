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
blast_records = NCBIXML.parse(result_handle)

E_VALUE_THRESH = 0.04
MIN_IDENT = 97
MIN_COVER = 95
b1 = 0
good_record_list = []

for blast_record in blast_records:
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < E_VALUE_THRESH:
                ident = (hsp.identities/(alignment.length*0.01))
                cover = (len(hsp.match)/(len(hsp.query)*0.01))
                if ident > MIN_IDENT and cover > MIN_COVER:
                    good_record_list.append(blast_record)

save_file = open("my_blast.xml", "w")
save_file.write(good_record_list)
save_file.close
print("75%")