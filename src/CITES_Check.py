#!/usr/bin/env python

# Indentify a set of FASTA sequences and check for each sequences
# if it a CITES protected species. The pipeline will use a
# blacklist containing genbank ids of incorrectly identified
# sequences on genbank, BLAST hits that will match with this list
# are avoided

# import the argparse module to handle the input commands
import argparse

# get the commandline arguments that specify the input fastafile and the output file
parser = argparse.ArgumentParser(description = ('Identify a set of sequences and check if there are CITES species present'))

parser.add_argument('-i', '--input_file', metavar='fasta file', dest='i', type=str, 
			help='enter the fasta file', default='')
parser.add_argument('-o', '--output_file', metavar='output file', dest='o', type=str, 
			help='enter the output file', default='')
parser.add_argument('-ba', '--BLAST_algorithm', metavar='algorithm', dest='ba', type=str, 
			help='Enter the algorithm BLAST wil use (default=blastn)', default='blastn')
parser.add_argument('-bd', '--BLAST_database', metavar='database', dest='bd', type=str,
			help = 'Enter the database BLAST wil use (default=nt)', default = 'nt')
parser.add_argument('-hs', '--hitlist_size', dest='hs', type=int,
			help = 'Enter the size of the hitlist BLAST wil return (default=10)', default = 10)
parser.add_argument('-mb', '--megablast', dest='mb', action='store_true', 
			help = 'Use megablast, can only be used in combination with blastn')
parser.add_argument('-mi', '--min_identity', dest='mi', type=int, 
			help = 'Enter the minimal percentage of identity for BLAST results (default=97)', default = 97)
parser.add_argument('-mc', '--min_coverage', dest='mc', type=int, 
			help = 'Enter the minimal coverage for BLAST results in number of bases (default=100)', default = 100)
parser.add_argument('-me', '--max_evalue', dest='me', type=float, 
			help = 'Enter the minimal E-value for BLAST results (default=0.05)', default = 0.05)
parser.add_argument('-bl', '--blacklist', metavar='blacklist file', dest='bl', type=str,
			help = 'File containing the blacklisted genbank id\'s', default='')
parser.add_argument('-cd', '--CITES_db', metavar='CITES database file', dest='cd', type=str,
			help = 'Path to the local copy of the CITES database', nargs='+')
parser.add_argument('-fd', '--force_download', dest='fd', action='store_true',
			help = 'Force the update of the local CITES database')
parser.add_argument('-ad', '--avoid_download', dest='ad', action='store_true',
			help = 'Avoid updating the local CITES database')
parser.add_argument('-v', '--verbose', dest='v', action='store_true',
			help = 'Verbose: The scripts prints detailed information on what it is doing for logging')

args = parser.parse_args()


def get_blacklist ():
	
	# return a list containing the blacklisted genbank id's
	# the blacklist follows the following format:
	# genbank_id, description
	try:
		return [line.split(',')[0] for line in open(args.bl,'r') if line[0] != '#']
	except:
		return []


def get_CITES ():
	
	# import the subporcess module to run the 
	# Retieve_CITES script from the shell
	from subprocess import call
	import sys, os

	dir, file = os.path.split(sys.argv[0])
	CITES_path = dir+'/Retrieve_CITES.py'
	
	if args.fd == True and args.v == True:
		path = call([CITES_path, '-db'] + args.cd + ['-f', '-v'])
	elif args.fd == True:
		path = call([CITES_path, '-db'] + args.cd + ['-f'])		
	elif args.v == True:
		path = call([CITES_path, '-db'] + args.cd + ['-v'])	
	else:
		path = call([CITES_path, '-db'] + args.cd)



def get_CITES_dic ():
	
	# open the local CITES database, return a dictionary
	# containing the CITES information with the taxids as keys

	CITES_dic = {}
	for path in args.cd:
		for line in open(path, 'r'):
			line = line.rstrip().split(',')
			if line[0] != 'Date' and line[0][0] != '#':
				CITES_dic[line[0]] = line[1:]

	return CITES_dic


def blast_bulk (sequences, thread_number):

	# The blast modules are imported from biopython
	from Bio.Blast import NCBIWWW, NCBIXML
	from Bio import SeqIO
	import os

	# grap the file path to the input file, here the temporary fasta files will be created
	dir, file = os.path.split(args.i)

	# create the list where all the blast results are stored in
	blast_list = []

	# create the temporary file
	temp_file_path = os.path.join(dir, (str(thread_number) + 'temp.fasta'))
	temp_file = open(temp_file_path, 'w')

	# fill the temp file with sequences
	SeqIO.write(sequences, temp_file, 'fasta')
	temp_file.close()

	# read the temp fasta file
	temp_fasta_file = open(temp_file_path, 'r')
	fasta_handle = temp_fasta_file.read()

	# blast the temporary file, and save the blasthits in the blast_list
	try:	
		result_handle = NCBIWWW.qblast(args.ba, args.bd, fasta_handle, megablast=args.me, hitlist_size=args.hs)

		blast_list += [item for item in NCBIXML.parse(result_handle)]
	except:
		return 'failed'

	# remove the temporary file		
	os.remove(temp_file_path)

	# return the filled blast hit
	return blast_list


def parse_blast_align (sequences, thread, CITES_dic, blacklist):
	# import the biopython module to deal with fasta parsing
	from Bio import SeqIO
	
	blast_count, blast_list = 0, 'failed'
	while blast_list == 'failed' and blast_count < 3:
		if blast_count > 0: print '\nblast thread: ' + str(thread) + ' failed, retrying attempt: '+ str(blast_count)
		blast_list = blast_bulk(sequences, thread)
		blast_count += 1

	if blast_list == 'failed':
		for seq in sequences:
			write_results(seq.id + ',' + 'failed', 'a')
		return

	count = 1	

	# parse though the blast hits
	for blast_result in blast_list:
		for alignment in blast_result.alignments:
			for hsp in alignment.hsps:
	            		
				# calculate the %identity
		            	identity = float(hsp.identities/(len(hsp.match)*0.01))

				# grab the genbank number
				gb_num = alignment.title.split('|')[1]

				# an alignment needs to meet 3 criteria before 
				# it is an acceptable result: above the minimum 
				# identity, minimum coverage and E-value
			
				# create containing the relevant blast results
				# pass this list to the filter_hits function to
				# filter and write the blast results
				filter_hits([('\"' + blast_result.query + '\"'), ('\"' + alignment.title + '\"'), gb_num, str(identity),
						str(blast_result.query_length), str(hsp.expect), str(hsp.bits)], CITES_dic, blacklist)
				count += 1


def filter_hits (blast, CITES_dic, blacklist):
	
	# filter the blast hits, based on the minimum
	# identity, minimum coverage, e-value and the user blacklist
	if float(blast[3]) >= args.mi and int(blast[4]) >= args.mc and float(blast[5]) <= args.me:
		if blast[2] not in blacklist:
			taxon = obtain_tax(blast[2])
			results = blast+taxon

			# check if the taxon id of the blast hit
			# is present in the CITES_dic
			if taxon[0] in CITES_dic:
				results += CITES_dic[taxon[0]][1:]
			
			# write the results
			write_results(','.join(results), 'a')

	
def obtain_tax (code):
	
	# a module from Biopython is imported to connect to the Entrez database
	from Bio import Entrez
	from Bio import SeqIO

	taxon = ''

	try:
		# based on the genbank id the taxon id is retrieved from genbank
		Entrez.email = "quick@test.com"
		handle = Entrez.efetch(db="nucleotide", id= code, rettype="gb",retmode="text")
		record = SeqIO.read(handle, "gb")

		# parse through the features and grap the taxon_id
		sub = record.features
		taxon = sub[0].qualifiers['db_xref'][0].split(':')[1]
		species = sub[0].qualifiers['organism'][0]

	except:
		pass

	return [taxon, species]


def write_results (result, mode):
	
	# write the results to the output file
	out_file = open(args.o, mode)
	out_file.write(result + '\n')
	out_file.close()


def parse_seq_file (CITES_dic, blacklist):
	# import the biopython module to deal with fasta parsing
	# and the multiprocessing module to run multiple blast threads
	from Bio import SeqIO
	import multiprocessing
	import time
	import sys
	
	# parse the fasta file
	seq_list, sub_list = [seq for seq in SeqIO.parse(args.i, 'fasta')], []
	
	# blast each sequence in the seq_list list
	procs, count, threads = [], 1, 10
	if args.v == True: print 'Blasting sequences\n' + str(len(seq_list))
	while len(seq_list) > 0 or len(procs) > 0:
		# start the maximum number of threads
		while len(procs) < threads and len(seq_list) > 0:
			if len(seq_list) >= 50:
				sub_list = seq_list[:50]
				seq_list = seq_list[50:]
			else:
				sub_list = seq_list
				seq_list = []
			try:
				p = multiprocessing.Process(target=parse_blast_align, args=(sub_list, count, CITES_dic, blacklist,)) 
				procs.append([p, time.time()])
				p.start()
				count+=1
				if args.v == True: sys.stdout.write('\r' + str(len(seq_list)))
				if args.v == True: sys.stdout.flush()
			except:
				break

		# check when a thread is done, remove from the thread list and start
		# a new thread
		while len(procs) > 0:
			for p in procs:
				if p[0].is_alive() == False: 
					p[0].join()
					procs.remove(p)
				# time-out after 30 minutes
				elif time.time() - p[1] > 10800:
					try:
						if args.v == True: print '\ntimeout proc: ' + str(p[0]) + '\n'
					except:
						pass
					p[0].terminate()
					procs.remove(p)
			break


def main ():

	# Check if input fasta file and output file are provided
	if args.i == '' or args.o == '':
		print 'No fasta file or output file provided, see -help for details'
		return

	# Check if there is a more recent CITES list online
	if args.ad != True:
		if args.v == True: print 'Checking the status of the current CITES database'
		get_CITES()

	# create a dictionary containing the local CITES set	
	if args.v == True: print 'Reading the CITES database'
	CITES_dic = get_CITES_dic()

	# create a list with the blacklisted genbank ids
	if args.v == True: print 'Reading the user Taxon ID blacklist'
	blacklist = get_blacklist()

	# create a blank result file and write the header
	header = 'query,hit,accession,identity,hit length,e-value,bit-score,taxon id,species,CITES info (numbers match the footnotes at the online CITES appendice),NCBI Taxonomy name,appendix'
	write_results(header, 'w')

	# parse through the sequence file, blast all sequences and write the blast hits + CITES info
	if args.v == True: print 'Processing the sequence file'
	parse_seq_file(CITES_dic, blacklist)

	if args.v == True: print 'Done\nResults are written to the: ' + args.o + ' output file'


if __name__ == "__main__":
    main()

