#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script will trim fastq files based on the phred quality scores.

dependencies:
Bio python
'''
from Bio import SeqIO
import os
import sys

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all nececary files
'''
pwd = os.getcwd()
pwd = pwd.strip("/bin/Trim")
pwd = pwd + "/data/test/"
os.chdir('/')
os.chdir(pwd)
print("====== Welcome ======")
print("\nvoer alstublieft de naam van uw file in:")
filename = sys.stdin.readline()
filename = filename.strip("\n")
try:
    with open("trimmmed", "r") as file_clear:
        file_clear.write("")
        file_clear.close
except(IOError):
    pass

try:
    with open(filename,"r") as file_check:
        a = True
        file_check.close
except(IOError):
    filename = filename + '.txt'

            
'''
this block filters reads that have more 
than 5% low quality bases.
this for loop will extract the phred_quality 
for a fastq file.
it will count the number of bad bases and 
delete the reads based on a percentage
both the precentage and quality thresshold 
will be inputed form the terminal
'''
print("voer de phred score thresshold in:")
bad_qual_score = sys.stdin.readline()
print("als laaste willen wij nog het maximum percentage slechte reads:")
percentage_bad_base = sys.stdin.readline()

for rec in SeqIO.parse(filename, "fastq"):
    quality_seq = rec.letter_annotations["phred_quality"] # extract the quality sequence for the fastq record
    qualitycount = 0
    '''
    this for loop will count the number of bases which have a quality score lower than the 
    given value
    '''
    for phred_score in quality_seq:
        if phred_score < bad_qual_score:
            qualitycount = qualitycount + 1
        else:
            pass
    if qualitycount < (len(rec.seq)*percentage_bad_base): # the quality count needs to be below the given percentage before it is written to file
        '''
        the output is writen to a file called {trimmed} in the fasta format.
        '''
        out_handle = open("trimmed", "a")
        SeqIO.write(rec, out_handle, "fasta")#this writes the fastq record in fasta format to the file
        out_handle.close # the file is closed each time to prevent the RAM to fill needlessly is the file is big.
    else:
        pass

print("done 25%")