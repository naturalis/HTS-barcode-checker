#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script will take the blast results and change them into a more human friendly format.

dependencies:
Bio python
Unix OS
'''
from Bio.Blast import NCBIXML
import sys
import logging

good_blast    = sys.stdin.readlines()    # this receives the titles of the alignments that passed the quality control
result_handle = open(sys.argv[1], "r")   # this points to the my_blast.xml and comes from the terminal
max_results   = int(sys.argv[2])         # the max number of results per query is given from the terminal
good_blast    = good_blast[0].split(";") # the input comes as one entry in a list, this converts it into a list of titles

'''
this block takes an XML file filled with NCBI BLAST output and parses it 
into a human readable format. per query sequence it will show a given 
number or less results.
'''
logging.info('start output')
for blast_record in NCBIXML.parse(result_handle):
    current_results = 0
    for alignment in blast_record.alignments:
        if current_results < max_results:                           #if the max number of results is reached it will continue on the the next query
            for hsp in alignment.hsps:
                ident = float(hsp.identities/(len(hsp.match)*0.01)) # this calculates the % identities and % coverage of the current alignment
                cover = float(len(hsp.match)/(len(hsp.query)*0.01))
                if alignment.hit_def in good_blast:
                    print('****Alignment****')                      # print formatting for user
                    print('sequence:'   , alignment.title)
                    print('length:'     , alignment.length)
                    print('% identity:' , ident)
                    print('e value:'    , hsp.expect)
                    print('% coverage'  , cover)
                    print(hsp.query[0:75] + '...')
                    print(hsp.match[0:75] + '...')
                    print(hsp.sbjct[0:75] + '...')
                    print('\n')
        current_results = current_results + 1
result_handle.close()
logging.info('finished output')