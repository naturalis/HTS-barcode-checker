#!/usr/bin/python2.7

#@author: Thomas Bolderink

# blast script for blast -barcode pipeline
import Bio

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

fasta_string = open ("MID6.fa").read()
fasta_handle = NCBIWWW.qblast("blastn","nt", fasta_string)

save_file = open("my_blast.xml", "w")
save_file.write(fasta_handle.read())
save_file.close()
fasta_handle.close()

fasta_handle = open("my_blast.xml")
blast_record = NCBIXML.parse(fasta_handle)



























