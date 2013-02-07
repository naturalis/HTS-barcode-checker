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
# biopython is used in the trimming process, sys is used for input/output and logging is used for user information
from Bio import SeqIO
import sys
import logging

# logging is set to the info level
logging.basicConfig(level = logging.INFO)

# the location of the input and output files and phred_score are given via command line arguments
input_file = sys.argv[1]
output_path = sys.argv[2]
phred_score_cut = int(sys.argv[3])

# if there already is a file with the same name than that file is first overwritten with a blank line
try:
    out_file = open('{path}'.format(path = output_path), 'w')
    out_file.write('')
    out_file.close
except(NameError):
    pass
                            
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

# the length of the bad sequence is set to 5
number_bad_base = 5

logging.info("start trimming")

# every fastq read is read from the file and assigned to rec
for rec in SeqIO.parse('{input_file}'.format(input_file = input_file), "fastq"):
    # the quality seq is retrieved from rec 
    quality_seq = rec.letter_annotations["phred_quality"]   # extract the quality sequence for the fastQ record
    # next the dna seq is retrieved from rec
    dna_seq = rec.seq
    # the length of the seq is calculated
    dna_length = len(dna_seq)
    # qualitycount is set to 0 because it is the beginning
    qualitycount = 0
    # subrec wil be the final seq and will be written to the output file
    subrec = rec.format('fasta')
    
    '''
    this for loop will count the number of bases which have a quality score lower than the 
    given value
    '''
    index = 0
    # p is used to check if the read has been trimmed
    p = 0
    # the quality score is read one by one form the quality seq
    for phred_score in quality_seq:
        # if quality score is below a given score quality count increases by 1 and the index is increased by one
        if int(phred_score) < int(phred_score_cut):
            qualitycount = qualitycount + 1
            index = index + 1
        # if the quality score is above a given score the qualitycount is checked to see if it is bigger than number_bad_base
        else:
            if qualitycount > number_bad_base:
                # if the bad seq is on the left side of the seq than the seq is trimmed from the left side else it is done from the right
                if (index-qualitycount) > (dna_length/2):
                    # subrec becomes a trimmed rec 
                    subrec = rec[:(index-qualitycount)].format('fasta')
                    # if the read is trimmed qualitycount is reset to 0
                    qualitycount = 0
                    p = 1
                else:
                    # subrec becomes a trimmed rec
                    subrec = rec[index:].format('fasta')
                    # if the read is trimmed qualitycount is reset to 0
                    qualitycount = 0
                    p = 1
            else:
                qualitycount = 0
            index = index + 1
    
    
    out_file = open('{path}'.format(path = output_path), 'a')
    # if the read has not been flagged as trimmed by p, the qualitycount is checked to see if it needs to be removed completely.
    if p == 0:
        if qualitycount > number_bad_base:
            # if qualitycount equals length of rec.seq than the entire read is of low quality and it is not written to the output file
            if qualitycount == len(rec.seq):
                pass
            else:
                subrec = rec[:-qualitycount].format('fasta')
                sys.stdout.write(subrec)
                out_file.write(subrec)
        else:
            sys.stdout.write(subrec)
            out_file.write(subrec)
    else:
        sys.stdout.write(subrec)
        out_file.write(subrec)
    out_file.close

logging.info("finished trimming")