#!/usr/bin/env python

# descrip


# import the argparse module to handle the input commands
import argparse

# get the commandline arguments that specify the input fastafile and the output file
parser = argparse.ArgumentParser(description = ('retrieve blast and taxonomic information for a fasta file'))

parser.add_argument('-i', '--input_file', metavar='fasta file', dest='i', type=str, 
			help='enter the fasta file')
parser.add_argument('-o', '--output_file', metavar='output file', dest='o', type=str, 
			help='enter the output file')
parser.add_argument('-a', '--BLAST_algorithm', metavar='algorithm', dest='a', type=str, 
			help='Enter the algorithm BLAST wil use (default=blastn)', default='blastn')
parser.add_argument('-d', '--BLAST_database', metavar='database', dest='d', type=str,
			help = 'Enter the database BLAST wil use (default=nt)', default = 'nt')
parser.add_argument('-s', '--hitlist_size', dest='s', type=str,
			help = 'Enter the size of the hitlist BLAST wil return (default=1)', default='1')
parser.add_argument('-m', '--megablast', dest='m', action='store_true', 
			help = 'Use megablast, can only be used in combination with blastn')
parser.add_argument('-mi', '--min_identity', dest='mi', type=str, 
			help = 'Enter the minimal identity for BLAST results', default = '97')
parser.add_argument('-mc', '--min_coverage', dest='mc', type=str, 
			help = 'Enter the minimal coverage for BLAST results', default = '100')
parser.add_argument('-me', '--max_evalue', dest='me', type=str, 
			help = 'Enter the minimal E-value for BLAST results', default = '0.05')
parser.add_argument('-b', '--blacklist', metavar='blacklist file', dest='b', type=str,
			help = 'File containing the blacklisted genbank id\'s', default='')
parser.add_argument('-c', '--CITES_db', metavar='CITES database file', dest='c', type=str,
			help = 'Path to the local copy of the CITES database')
parser.add_argument('-fu', '--force_update', dest='fu', action='store_true',
			help = 'Force the update of the local CITES database')
parser.add_argument('-au', '--avoid_update', dest='au', action='store_true',
			help = 'Avoid updating the local CITES database')

args = parser.parse_args()

def get_CITES ():
	
	# import the subporcess module to run the 
	# Retieve_CITES script from the shell
	from subprocess import call
	
	if args.fu == True:
		path = call(['./Retrieve_CITES.py', '-db', args.c, '-f'])
	else:
		path = call(['./Retrieve_CITES.py', '-db', args.c])


def run_Blast ():

	# import the subporcess module to run the 
	# Blast_and_Compare.py script from the shell
	from subprocess import call

	if args.m == True:
		path = call(['./Blast_and_Compare.py', '-i', args.i, '-o', args.o, '-c', args.c,
			'-a', args.a, '-d', args.d, '-s', args.s, '-m', '-mi', args.mi, '-mc', 
			args.mc, '-me', args.me, '-b', args.b])

	else:
		path = call(['./Blast_and_Compare.py', '-i', args.i, '-o', args.o, '-c', args.c,
			'-a', args.a, '-d', args.d, '-s', args.s, '-mi', args.mi, '-mc', args.mc,
			'-me', args.me, '-b', args.b])


def main ():	
	
	# check if the CITES database needs to be updated
	if args.au != True:
		get_CITES()
	
	# run the Blast and compare script
	run_Blast()
	

if __name__ == "__main__":
    main()
