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
# from biopython we import the xml parser to parse a .xml file that is obtained with blast.py
from Bio.Blast import NCBIXML
# further we import sys for input/output logging for user information 
import sys, logging

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all necessary files are placed
'''


logging.basicConfig(level = logging.INFO)       # the logging level is set to info
filename       = sys.stdin.readline()           # the filename is the path to an xml file from the ncbi webserver
filename       = filename.strip('\n')           # a \n is removed from the path
result_handle  = open(filename, "r")            # this gets input in an xml format from blast
E_VALUE_THRESH = float(sys.argv[1])             # an e-value treshold is given from the commandline
MIN_IDENT      = int(sys.argv[2])               # the minimum identity criteria
MIN_COVER      = int(sys.argv[3])               # the minimum coverage criteria
result_list    = []                             # a list to store the hits that meed certain criteria


logging.info('start quality control')
# the program iterates over the xml file
for blast_record in NCBIXML.parse(result_handle):
    # each alignment is extracted from the blast_record
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            # this calculates the % identities and % coverage of the current alignment
            ident = float(hsp.identities/(len(hsp.match)*0.01))
            cover = float(len(hsp.match)/((blast_record.query_length)*0.01))
            # an alignment needs to meet 3 criteria before we consider it an acceptable result: above the minimum identity, minimum coverage and E-value
            if int(hsp.expect) < E_VALUE_THRESH and int(ident) > MIN_IDENT and int(cover) > MIN_COVER:
                # the hit_def and hit_id are stored in a list for use later in the script, an ; marks the end of a hit
                line = alignment.hit_def + '"' + alignment.hit_id + '"' + ';;'
                result_list.append(line)

# the list with the hit_def and hit_id of blast hits is given to the next stage
sys.stdout.writelines(result_list)
logging.info("finished quality control")