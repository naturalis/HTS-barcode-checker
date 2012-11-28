#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil filter the blast results on E-value and bit-score.

coverage 95%
identity 97%
'''
from Bio.Blast import NCBIXML
import os

pwd = os.getcwd()
pwd = pwd.strip("/bin/Quality") 
file1 = "{pwd}/data/test/trimmed".format(pwd = pwd)

result_handle = open("{pwd}/data/test/my_blast.xml".format(pwd = pwd), "r")
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

save_file = open("{pwd}/data/test/my_blast.xml".format(pwd = a2), "w")
save_file.write(good_record_list.read())
save_file.close
print("75%")