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
import sys
import logging

logging.basicConfig(level = logging.INFO)
out_file = sys.argv[1]
algorit = sys.argv[2]
database = sys.argv[3]
filename = sys.argv[4]
'''
the input from the Trim script needs to be converted into 
a format which is usable by NCBIWWW
'''
file = open(filename,'r')
fasta_handle = file.read()
file.close

logging.info('starting BLAST')
fasta_handle = NCBIWWW.qblast("{algorit}".format(algorit = algorit), "{database}".format(database = database), fasta_handle, megablast = False)  # define blast parameters for blast search
logging.info('finished BLAST')
save_file = open(out_file, "w")
save_file.write(fasta_handle.read()) # results of the blast search are stored in xml file
sys.stdout.write(out_file)
save_file.close
fasta_handle.close