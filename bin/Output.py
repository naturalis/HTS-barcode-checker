#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script will take the blast results and change them into a more human friendly format.

dependencies:
Bio python
Unix OS
'''
from Bio.Blast import NCBIXML
import sys
import logging

cites = sys.stdin.readlines()
xml = sys.argv[1]
path = sys.argv[2]
path = path[:-3]+"data"
result_handle = open(xml, "r")   # this points to the my_blast.xml and comes from the terminal
logging.basicConfig(level = logging.INFO)

asseccion = []
cites_names = []
a = 0
for line in cites:
    line = line.strip("\n")
    #line = line.strip("\r")
    if line == ";":
       a = 1
    else:
        if a == 1:
            asseccion.append(line)
        elif a == 0:
            cites_names.append(line)
#logging.info(asseccion)
#logging.info(cites_names)
'''
this block takes an XML file filled with NCBI BLAST output and parses it 
into a human readable format. per query sequence it will show a given 
number or less results.
'''

results_file = open("{path}/pipe_results.csv".format(path = path),"w")
results_file.write('"Query","Accession","Description","Bit score","Coverage","e-value","Identity","CITES"\n')
results_file.close()

i = 1
logging.info('start output')
for blast_record in NCBIXML.parse(result_handle):
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01)) # this calculates the % identities and % coverage of the current alignment
            cover = float(len(hsp.match)/((blast_record.query_length)*0.01))
            ident = round(ident, 5)
            cover = round(cover, 5)
 
            hit_def = alignment.hit_def
            if alignment.hit_id in asseccion:
                result_string = '"{a}","{g}","{b}","{c}","{d}","{e}","{f}","yes"\n'.format(a = blast_record.query, b = alignment.hit_def, c = hsp.bits, d = cover, e = hsp.expect, f = ident, g = alignment.hit_id)
            else:
                result_string = '"{a}","{g}","{b}","{c}","{d}","{e}","{f}"\n'.format(a = blast_record.query, b = alignment.hit_def, c = hsp.bits, d = cover, e = hsp.expect, f = ident, g = alignment.hit_id)
            results_file = open("{path}/pipe_results.csv".format(path = path),"a")
            results_file.write(result_string)
            results_file.close()
result_handle.close()

print(cites_names)

logging.info('finished output')