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
# the biopython xml parser is import allong with sys and logging
from Bio.Blast import NCBIXML
import sys, logging

# from the CITES_check script the script rescieves the text and hit_id of blast hits that are matched to a spicies on the CITES appendices 
cites = sys.stdin.readlines()
# the path to the xml file and output file is given via commandline
xml = sys.argv[1]
path = sys.argv[2]
path = path[:-3]+"data"
result_handle = open(xml, "r")   

# the logging level is set to info 
logging.basicConfig(level = logging.INFO)

# two lists are created and used to store or the hit_id or text form cites appendices
asseccion = []
cites_names = []
# a is used to switch between text and hit_id
a = 0
for line in cites:
    line = line.strip("\n")
    # the ; symbol represents the end of the cites text and beginning of the hit_id's
    if line == ";":
       a = 1
    else:
        if a == 1:
            asseccion.append(line)
        elif a == 0:
            cites_names.append(line)

'''
this block takes an XML file filled with NCBI BLAST output and parses it 
into a human readable format. per query sequence it will show a given 
number or less results.
'''

# the output file is created or emptied and the collum headers are added
results_file = open("{path}/pipe_results.csv".format(path = path),"w")
results_file.write('"Query","Accession","Description","Bit score","Coverage","e-value","Identity","CITES"\n')
results_file.close()

logging.info('start output')

# the script iterates over the xml file
for blast_record in NCBIXML.parse(result_handle):
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            # this calculates the % identities and % coverage of the current alignment
            ident = float(hsp.identities/(len(hsp.match)*0.01))
            cover = float(len(hsp.match)/((blast_record.query_length)*0.01))
            # the numbers are rounded after 5 numbers
            ident = round(ident, 5)
            cover = round(cover, 5)
            
            # if the hit_def of the blast hit matches that of a matche on the CITES appendices than "yes" is added to the last collum of the output file 
            hit_def = alignment.hit_def
            if alignment.hit_id in asseccion:
                result_string = '"{a}","{g}","{b}","{c}","{d}","{e}","{f}","yes"\n'.format(a = blast_record.query, b = alignment.hit_def, c = hsp.bits, d = cover, e = hsp.expect, f = ident, g = alignment.hit_id)
            else:
                result_string = '"{a}","{g}","{b}","{c}","{d}","{e}","{f}"\n'.format(a = blast_record.query, b = alignment.hit_def, c = hsp.bits, d = cover, e = hsp.expect, f = ident, g = alignment.hit_id)
            results_file = open("{path}/pipe_results.csv".format(path = path),"a")
            results_file.write(result_string)
            results_file.close()
result_handle.close()

# the text of cites is printed to the command line
print(cites_names)

logging.info('finished output')