#!/usr/bin/python2.7
'''

@author: Thomas Bolderink
@co-author: Alex Hoogkamer

 blast script for blast -barcode pipeline
dependencies:
Bio python
Unix OS


input: fastqfile
output: XML file with blastN search results
'''

from Bio.Blast import NCBIWWW
#import os
import sys
import logging

logging.basicConfig(level = logging.INFO)
input_handle = sys.stdin.readlines()
out_file = sys.argv[1]
algorit = sys.argv[2]
database = sys.argv[3]
'''
the input from the Trim script needs to be converted into 
a format which is usable by NCBIWWW
'''
data_handle = []
fasta       = ''
a           = 0

for line in input_handle:
    if a == 0:
        if line[0] == '>':
            fasta = line + '\n'
            a = a + 1
        else:
            pass
    else:
        if line[0] == '>':
            fasta = fasta + "\n"
            data_handle.append(fasta)
            fasta = line
        else:
            fasta = fasta + line.strip("\r\n")
'''
if len(data_handle) == 0:
    data_handle.append(fasta)
'''
blast_handle = ''
for line in data_handle:
    blast_handle = blast_handle + line
logging.info('starting BLAST')
fasta_handle = NCBIWWW.qblast("{algorit}".format(algorit = algorit), "{database}".format(database = database), blast_handle)  # define blast parameters for blast search
logging.info('finished BLAST')
save_file = open(out_file, "w")                                          # results of the blast search are stored in xml file
save_file.write(fasta_handle.read())
sys.stdout.write(out_file)
save_file.close
fasta_handle.close