#!/usr/bin/python2.7

#@author: Thomas Bolderink
#@co-author: Alex Hoogkamer

# blast script for blast -barcode pipeline
#dependencies:
#Bio python

from Bio.Blast import NCBIWWW
import os

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all nececary files
'''
pwd = os.getcwd()
pwd = pwd.strip("/bin/BLAST") 
pwd = pwd + "/data/test/"
os.chdir('/')
os.chdir(pwd)
filename = "trimmed"

fasta_string = open(filename).read()
fasta_handle = NCBIWWW.qblast("blastn","nt", fasta_string)
save_file = open("my_blast.xml".format(pwd = pwd), "w")
save_file.write(fasta_handle.read())
save_file.close
fasta_handle.close

print("done 50%")