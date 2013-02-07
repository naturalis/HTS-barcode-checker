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
phred_score = int(sys.argv[3])
#percentage_bad_base = 10

phred_score_cut = phred_score

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
count1 = 0
count2 = 0
number_bad_base = 5
logging.info("start trimming")
for rec in SeqIO.parse('{input_file}'.format(input_file = input_file), "fastq"):
    count1 = count1 + 1
    quality_seq = rec.letter_annotations["phred_quality"]   # extract the quality sequence for the fastQ record
    dna_seq = rec.seq
    dna_length = len(dna_seq)
    qualitycount = 0
    subrec = rec.format('fasta')
    '''
    this for loop will count the number of bases which have a quality score lower than the 
    given value
    '''
    index = 0
    p = 0
    for phred_score in quality_seq:
        if int(phred_score) < int(phred_score_cut):                    # if quality score is below a given score quality count increases by 1
            qualitycount = qualitycount + 1
            index = index + 1
        else:
            if qualitycount > number_bad_base:
                if (index-qualitycount) > (dna_length/2):
                    subrec = rec[:(index-qualitycount)].format('fasta')
                    qualitycount = 0
                    p = 1
                else:
                    subrec = rec[index:].format('fasta')
                    qualitycount = 0
                    p = 1
            else:
                qualitycount = 0
            index = index + 1

    out_file = open('{path}'.format(path = output_path), 'a')
    if p == 0:
        if qualitycount > number_bad_base:
            if qualitycount == len(rec.seq):
                pass
            else:
                subrec = rec[:-qualitycount].format('fasta')
                sys.stdout.write(subrec)
                out_file.write(subrec)
        else:
            pass
    else:
        sys.stdout.write(subrec)
        out_file.write(subrec)
    out_file.close

logging.info("finished trimming")