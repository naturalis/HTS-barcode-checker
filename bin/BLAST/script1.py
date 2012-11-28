#!/usr/bin/python2.7

#@author: Thomas Bolderink
#@co-author: Alex Hoogkamer

# blast script for blast -barcode pipeline

from Bio.Blast import NCBIWWW
import os

pwd = os.getcwd()
pwd = pwd.strip("/bin/BLAST") 
file1 = "{pwd}/data/test/trimmed".format(pwd = pwd)

fasta_string = open(file1).read()
fasta_handle = NCBIWWW.qblast("blastn","nt", fasta_string)
save_file = open("{pwd}/data/test/my_blast.xml".format(pwd = pwd), "w")
save_file.write(fasta_handle.read())
save_file.close
fasta_handle.close

os.system("rm a1")
print("done 50%")