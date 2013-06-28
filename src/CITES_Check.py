#!/usr/bin/env python

# Indentify a set of FASTA sequences and check for each sequences
# if it a CITES protected species. The pipeline will use a
# blacklist containing genbank ids of incorrectly identified
# sequences on genbank, BLAST hits that will match with this list
# are avoided

# import the argparse module to handle the input commands
# and the logging module to track log messages
import argparse, logging, os

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
parser.add_argument('-l', '--logging', metavar='log level', dest='l', type=str,
			help = 'Set log level to: debug, info, warning (default) or critical see readme for more details.\nlog written to -output_file + \'.log\'', default='warning')

args = parser.parse_args()


def get_blacklist ():
	
	# return a list containing the blacklisted genbank id's
	# the blacklist follows the following format:
	# genbank_id, description
	logging.debug('Trying to obtain genbank IDs from blacklist file: %s.' % args.bl)
	try:
		return [line.split(',')[0] for line in open(args.bl,'r') if line[0] != '#']
	except:
		return []


def get_CITES ():
	
	# import the subporcess module to run the 
	# Retieve_CITES script from the shell
	from subprocess import call
	import sys, os

	logging.debug('Getting path to Retrieve_CITES.py script.')
	dir, file = os.path.split(sys.argv[0])
	CITES_path = dir+'/Retrieve_CITES.py'
	logging.debug('Retrieve_CITES.py path set to: %s.' % CITES_path)
	
	if args.fd == True:
		path = call([CITES_path, '-db'] + args.cd + ['-f', '-l', args.l, '-lf', args.o])
	else:
		path = call([CITES_path, '-db'] + args.cd + ['-l', args.l, '-lf', args.o])



def get_CITES_dic ():
	
	# open the local CITES database, return a dictionary
	# containing the CITES information with the taxids as keys
	
	logging.debug('Parsing through list of CITES dictionaries.')

	CITES_dic = {}
	for path in args.cd:
		logging.debug('Reading CITES information from file: %s.' % path)
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
	logging.debug('Creating temporary fasta file for blasting: %s.' % temp_file)

	# fill the temp file with sequences
	logging.debug('Writing fasta sequences to temporary file.')
	SeqIO.write(sequences, temp_file, 'fasta')
	temp_file.close()

	# read the temp fasta file
	logging.debug('Reading fasta sequences from temporary file.')
	temp_fasta_file = open(temp_file_path, 'r')
	fasta_handle = temp_fasta_file.read()

	# blast the temporary file, and save the blasthits in the blast_list
	logging.debug('Blasting fasta sequences.')
	try:	
		result_handle = NCBIWWW.qblast(args.ba, args.bd, fasta_handle, megablast=args.me, hitlist_size=args.hs)
		logging.debug('Parsing blast result XML file.')
		blast_list += [item for item in NCBIXML.parse(result_handle)]
	except:
		logging.warning('Failed to obtain blast results.')		
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
		blast_list = blast_bulk(sequences, thread)
		blast_count += 1
		logging.info('Blast thread: %i failed, retrying attempt %i.' % (thread, blast_count))

	if blast_list == 'failed':
		logging.debug('Could not obtain blast hits for set of sequences, written to output file as \"failed\".')
		for seq in sequences:
			write_results(seq.id + ',' + 'failed', 'a')
		return

	count = 1	

	# parse though the blast hits
	logging.debug('Parsing through blast XML results.')
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
				logging.debug('Appending CITES info to blast hit.')
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
		Entrez.email = "CITES_check@gmail.com"
		handle = Entrez.efetch(db="nucleotide", id= code, rettype="gb",retmode="text")
		record = SeqIO.read(handle, "gb")

		# parse through the features and grap the taxon_id
		sub = record.features
		taxon = sub[0].qualifiers['db_xref'][0].split(':')[1]
		species = sub[0].qualifiers['organism'][0]

	except:
		logging.warning('Could not obtain a taxon info for taxon ID: %s.' % code)
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
	logging.info('Reading user provided fasta file: %s.' % args.i)
	seq_list, sub_list = [seq for seq in SeqIO.parse(args.i, 'fasta')], []
	
	# blast each sequence in the seq_list list
	procs, count, threads = [], 1, 10
	logging.info('Blasting sequences, total: %i.' % len(seq_list))
	print('Blasting sequences, total sequences: %i.' % len(seq_list))
	logging.debug('Start multithreaded blast search.')
	while len(seq_list) > 0 or len(procs) > 0:
		# start the maximum number of threads
		while len(procs) < threads and len(seq_list) > 0:
			if len(seq_list) >= 50:
				sub_list = seq_list[:50]
				seq_list = seq_list[50:]
			else:
				sub_list = seq_list
				seq_list = []
			logging.debug('Try to open a blast thread.')
			try:
				logging.debug('Opening thread number: %i, total number %i.' % (len(procs), count))
				p = multiprocessing.Process(target=parse_blast_align, args=(sub_list, count, CITES_dic, blacklist,)) 
				procs.append([p, time.time()])
				p.start()
				count+=1
				sys.stdout.write('\r' + str(len(seq_list)))
				sys.stdout.flush()
			except:
				logging.warning('Failed to open thread number: %i, total number %i.' % (len(procs), count))
				break

		# check when a thread is done, remove from the thread list and start
		# a new thread
		while len(procs) > 0:
			for p in procs:
				if p[0].is_alive() == False:
					logging.debug('Process %s finished.' % str(p[0]))
					p[0].join()
					procs.remove(p)
				# time-out after 30 minutes
				elif time.time() - p[1] > 10800:
					try:
						logging.warning('Timeout for process %s.' % str(p[0]))
					except:
						pass
					logging.debug('Terminating and removing process %s.' % str(p[0]))
					p[0].terminate()
					procs.remove(p)
			break


def main ():

	# set log level
	log_level = getattr(logging, args.l.upper(), None)
	if not isinstance(log_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)
		return
	logging.basicConfig(filename=os.path.splitext(args.o)[0]+'.log', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)

	# Check if input fasta file and output file are provided
	if args.i == '' or args.o == '':
		logging.critical('No fasta file or output file provided, see -help for details.')
		print 'No fasta file or output file provided, see --help for details.'
		return

	# Check if there is a more recent CITES list online
	if args.ad != True:
		logging.info('Checking the status of the current CITES database.')
		get_CITES()

	# create a dictionary containing the local CITES set	
	logging.info('Reading the CITES database.')
	CITES_dic = get_CITES_dic()

	# create a list with the blacklisted genbank ids
	logging.info('Reading the user Taxon ID blacklist.')
	blacklist = get_blacklist()

	# create a blank result file and write the header
	header = 'query,hit,accession,identity,hit length,e-value,bit-score,taxon id,species,CITES info (numbers match the footnotes at the online CITES appendice),NCBI Taxonomy name,appendix'
	write_results(header, 'w')

	# parse through the sequence file, blast all sequences and write the blast hits + CITES info
	logging.info('Processing the sequence file.')
	parse_seq_file(CITES_dic, blacklist)

	print '\nDone\nResults are written to the: ' + args.o + ' output file'


if __name__ == "__main__":
    main()

