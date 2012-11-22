#!/usr/bin/python2.7

#@author: Thomas Bolderink
#@co-author: Alex Hoogkamer

# blast script for blast -barcode pipeline

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import os

os.system("pwd > a1")
file2 = open("a1","r")
a2 = file2.read()
file2.close
a2 = a2.strip("\n")
file1 = "{pwd}/data/test/s_2_1_sequence-trimmed".format(pwd = a2)

fasta_string = open(file1).read()
fasta_handle = NCBIWWW.qblast("blastn","nt", fasta_string)

blast_records = NCBIXML.parse(fasta_handle)

E_VALUE_THRESH = 0.04

for blast_record in blast_records:
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < E_VALUE_THRESH:
                print('****Alignment****')
                print('sequence:', alignment.title)
                print('length:'  , alignment.length)
                print('e value:' , hsp.expect)
                print(hsp.query[0:75] + '...')
                print(hsp.match[0:75] + '...')
                print(hsp.sbjct[0:75] + '...')

os.system("rm a1")

print("done 50%")