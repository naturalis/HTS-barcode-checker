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
import sys

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all nececary files
'''

result_handle = open(sys.argv[1], "r")

E_VALUE_THRESH = 0.04
MIN_IDENT = 97
MIN_COVER = 95
c1 = 1

new_blast_record = []
new_blast_records = []
for blast_record in NCBIXML.parse(result_handle):
    print(blast_record)
    '''
    c2 = 0
    result_blast_record = open("out{number}.txt".format(number = c1), "a")
    '''
    for alignment in blast_record.alignments:
        '''
        print(alignment)
        '''
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01))
            cover = float(len(hsp.match)/(len(hsp.query)*0.01))
            if hsp.expect < E_VALUE_THRESH and ident > MIN_IDENT and cover > MIN_COVER:
                new_blast_record.append(blast_record)
                '''
                if c2 < 15:
                    c2 = c2 + 1
                    #sys.stdout.write(str(hsp))
                    result_blast_record.write(str(alignment))
                    result_blast_record.write(str(hsp))
                    result_blast_record.write(str("\n"))
    result_blast_record.close
    c1 = c1 + 1
    '''
print(new_blast_record)
'''
save_file = open("my_blast_filterd.xml", "w")
save_file.write(blast_records.read())
save_file.close
result_handle.close()
'''