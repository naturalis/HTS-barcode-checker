#!/usr/bin/python2.7
'''

@author: Thomas Bolderink
@co-author: Alex Hoogkamer

blast script for blast -barcode pipeline
dependencies:
Bio python
Unix OS

A script for blasting fasta reads.

input: fastqfile
output: XML file with blastN search results
'''

from Bio.Blast import NCBIWWW    #import biopython BLAST module
import sys, logging, argparse

logging.basicConfig(level = logging.INFO)
args = argparse.ArgumentParser(description = '2nd part of pipeline, BLAST the input file and writes the results to xml file')
# possible user  input parameters 
args.add_argument('-i', '--input_file', type = str, help = 'Enter the path to the input file, the input file needs to be in fastq format for trimming or in fasta format without trimming', nargs='+') 
args.add_argument('-o','--output_file', type = str, help = 'Enter the path to the output file', nargs='+')
args.add_argument('-a', '--BLAST_algorithm', type = str, help = 'Enter the algorithm BLAST wil use', default = 'nt')
args.add_argument('-d', '--BLAST_database', type = str, help = 'Enter the database BLAST wil use', default = 'blastn')
args.add_argument('-s', '--hitlist_size', type = int, help = 'Enter the size of the hitlist BLAST wil return', default =1)
args.add_argument('-p', '--pipe', action='store_true', help = 'switch to enable piping')
args.add_argument('-m', '--megablast', action='store_true', help = 'Switch to use megablast instead of blastn')
args.add_argument('-g', '--gapcost', help = 'Enter the gap cost, it is entered as "x y"' , default = "5 5")
args.add_argument('-nr', '--nucleotide_reward', help = 'Enter the match', default = "5")
args.add_argument('-np', '--nucleotide_penalty', help = 'Enter the mismatch', default = "-4")
args.add_argument('-w', '--wordsize', help = 'Enter the wordsize for blast', default = 11)

#output/parse the parameters to the other scripts
args         = args.parse_args()
out_file     = args.output_file[0]
algorit      = args.BLAST_algorithm
database     = args.BLAST_database
filename     = args.input_file[0]
size_hitlist = args.hitlist_size

'''
the input from the Trim script needs to be converted into 
a format which is usable by NCBIWWW
'''
if args.pipe:
    fasta = sys.stdin.readlines()
    print(fasta)
else:
    file = open(filename,'r')
    fasta_handle = file.read()
    file.close

#start the blast
logging.info('starting BLAST')
fasta_handle = NCBIWWW.qblast("{algorit}".format(algorit = algorit), "{database}".format(database = database), fasta_handle, megablast = args.megablast, hitlist_size = size_hitlist, word_size = args.wordsize, gapcosts = "5 5", nucl_penalty = "-5" , nucl_reward = "4")  # define(default) blast parameters for blast search
logging.info('finished BLAST')

save_file = open(out_file, "w")
save_file.write(fasta_handle.read()) # results of the blast search are stored in xml file(named: my_blast.xml)and stored on the users's computer
sys.stdout.write(out_file)
save_file.close
fasta_handle.close