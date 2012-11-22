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

blast_records = NCBIXML.parse(fasta_handle)
blast_record = list(blast_records)
print blast_record

#blast_record = blast_record.next()

#E_VALUE_THRESH = 0.04
#for alignment in blast_record.alignments:
#    for hsp in alignment.hsps:
#        if hsp.expect < E_VALUE_THRESH:
#            print '****Alignment****'
#            print 'sequence:', alignment.title
#            print 'length:'  , alignment.length
#            print 'e value:' , hsp.expect
#            print hsp.query[0:75] + '...'
#            print hsp.match[0:75] + '...'
#            print hsp.sbjct[0:75] + '...'
























