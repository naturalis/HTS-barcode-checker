#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script will trim fastq files based on the phred quality scores.
'''
from Bio import SeqIO
import os
'''
this block counts the number of reads and filters reads that have more 
than 5% low quality bases.
'''
pwd = os.getcwd()
pwd = pwd.strip("/bin/Trim") 
file1 = "{pwd}/data/test/MID6".format(pwd = pwd)
count = 0
for rec in SeqIO.parse(file1, "fastq"):
    count += 1
    qual = rec.letter_annotations["phred_quality"]
    qualcount = 0
    for i in qual:
        if i < 46:
            qualcount = qualcount + 1
        else:
            pass
    if qualcount < (len(rec.seq)*0.05):
        out_handle = open("{filepath}/data/test/trimmed".format(filepath = pwd), "a")
        SeqIO.write(rec, out_handle, "fasta")
        out_handle.close
    else:
        pass
os.system("rm a1")
print("done 25%")