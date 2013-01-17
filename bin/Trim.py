#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script will trim fastq files based on the phred quality scores.

dependencies:
Bio python
Unix OS
'''
from Bio import SeqIO
import sys
import logging

logging.basicConfig(level = logging.INFO)

input_file = sys.argv[1]
output_path = sys.argv[2]
phred_score = sys.argv[3]
percentage_bad_base = 10
                            
'''
this block filters reads that have more 
than 10% low quality bases.
this for loop will extract the phred_quality 
for a fastQ file.
it will count the number of bad bases and 
delete the reads based on a percentage
both the percentage and quality threshold 
will be inputed form the terminal
'''

logging.info("start trimming")
for rec in SeqIO.parse('{input_file}'.format(input_file = input_file), "fastq"):
    quality_seq = rec.letter_annotations["phred_quality"]   # extract the quality sequence for the fastQ record
    qualitycount = 0
    '''
    this for loop will count the number of bases which have a quality score lower than the 
    given value
    '''
    for phred_score in quality_seq:
        if int(phred_score) < int(bad_qual_score):                    # if quality score is below a given score quality count increases by 1
            qualitycount = qualitycount + 1
        else:
            pass
    if qualitycount < ((len(rec.seq))*percentage_bad_base): # the quality count needs to be below the given percentage before it is written to file
        '''
        the output is given to the terminal in the fasta format.
        '''
        out_handle = open("{path}/trimmed".format(path = output_path), "a")
        out_handle.write(rec.format("fasta"))          #this writes the fastQ record in fasta format to the terminal
        out_handle.close # the file is closed each time to prevent the RAM to fill needlessly is the file is big.
    else:
        pass
logging.info("finished trimming")