#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil filter the blast results on E-value and bit-score.

default minimum coverage: 95%
default minimum identity : 97%

dependencies:
Bio python
Unix OS
'''
from Bio.Blast import NCBIXML
import os, sys, logging, subprocess

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all necessary files are placed

a = ["python test.py", "Agave"]

p = subprocess.Popen(a)
    
logging.info(p)
'''

logging.basicConfig(level = logging.INFO)
filename       = sys.stdin.readline()
filename       = filename.strip('\n')
result_handle  = open(filename, "r")                       # this gets input in an xml format from blast
E_VALUE_THRESH = float(sys.argv[1])
MIN_IDENT      = int(sys.argv[2])
MIN_COVER      = int(sys.argv[3])
result_list    = []


logging.info('start quality control')
for blast_record in NCBIXML.parse(result_handle):
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01))# this calculates the % identities and % coverage of the current alignment
            cover = float(len(hsp.match)/((blast_record.query_length)*0.01))
                                                               # an alignment needs to meet 3 criteria before we consider it an acceptable result: above the minimum identity, minimum coverage and E-value
            if int(hsp.expect) < E_VALUE_THRESH and int(ident) > MIN_IDENT and int(cover) > MIN_COVER:
                line = alignment.hit_def + '"' + alignment.hit_id + '"' + ';;'
                #result_list.append(alignment.hit_def)
                #result_list.append(alignment.hit_id)
                #result_list.append(';;')                        #the ; marks the end of a title and is used to split the list into seperate titles in the output script
                result_list.append(line)

sys.stdout.writelines(result_list)
logging.info("finished quality control")