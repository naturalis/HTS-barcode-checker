#!/usr/bin/env python

# descrip


# import the argparse module to handle the input commands
import argparse

# get the commandline arguments that specify the input fastafile and the output file
parser = argparse.ArgumentParser(description = ('retrieve blast and taxonomic information for a fasta file'))

parser.add_argument('-i', '--input_file', metavar='fasta file', dest='f', type=str, 
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
parser.add_argument('-mi', '--min_identity', dest='mi', type=int, 
			help = 'Enter the minimal identity for BLAST results', default = 97)
parser.add_argument('-mc', '--min_coverage', dest='mc', type=int, 
			help = 'Enter the minimal coverage for BLAST results', default = 100)
parser.add_argument('-me', '--max_evalue', dest='me', type=float, 
			help = 'Enter the minimal E-value for BLAST results', default = 0.05)
parser.add_argument('-b', '--blacklist', metavar='blacklist file', dest='b', type=str,
			help = 'File containing the blacklisted genbank id\'s', default='')
parser.add_argument('-c', '--CITES_db', metavar='CITES database file', dest='c', type=str,
			help = 'Path to the local copy of the CITES database')

args = parser.parse_args()

def get_CITES (CITES_path):
	
	# import the subporcess module to run the 
	# Retieve_CITES script from the shell
	from subprocess import call
	
	path = call(['Retrieve_CITES.py', '-db', CITES_path])


def run_Blast (fasta_file, output_file, CITES_path, arguments):

	# import the subporcess module to run the 
	# Blast_and_Compare.py script from the shell
	from subprocess import call

	path = call(['Blast_and_Compare.py', '-i', fasta_file, '-o', output_file, '-c', CITES_path,
			'-a', arguments[0], '-d', arguments[1], '-s', arguments[2], '-m', arguments[3],
			'-mi', arguments[4], '-mc', arguments[5], '-me', arguments[6], '-b', arguments[7]])


def main ():	
	
	Blast_args = [args.a, args.d, args.s, args.m, args.mi, args.mc, args.me, args.b]
	# retrieve the raw CITES appendix page
	CITES_php = download_raw_CITES()

	# parse through the CITES page and retrieve the
	# species names
	CITES_info = parse_php(CITES_php)
	
	# try to open the CITES database and check if the current version
	# (if there is one) is up to date
	try:
		if CITES_info[0] == CITES_date(args.db):
			print 'Local CITES database is up to date'
			return
	except:
		pass

	# use TNRS to grab the species synonyms and
	# taxid if available. Expand the taxids with 
	# taxids from lower ranked records
	taxon_id_dic = combine_sets(CITES_info[1])

	# write the results to the output location
	write_csv(CITES_info[0], taxon_id_dic, args.db)
	

if __name__ == "__main__":
    main()
