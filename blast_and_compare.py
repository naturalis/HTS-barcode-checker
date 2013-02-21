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
parser.add_argument('-s', '--hitlist_size', metavar='# hits', dest='s', type=str,
			help = 'Enter the size of the hitlist BLAST wil return (default=1)', default='1')
parser.add_argument('-m', '--megablast', dest='m', action='store_true', 
			help = 'Use megablast, can only be used in combination with blastn')

args = parser.parse_args()

def blast_bulk (fasta_file, settings):

	# The blast modules are imported from biopython
	from Bio.Blast import NCBIWWW, NCBIXML

	# open the fasta file
	fasta_open = open(fasta_file, 'r')
	fasta_handle = fasta_open.read()
	
	blast_list = []

	# Blast the sequences against the NCBI nucleotide database
	# return a list with the blast results
	result_handle = NCBIWWW.qblast(settings[0], settings[1], fasta_handle, megablast=settings[3], hitlist_size=settings[2])
	blast_list = [item for item in NCBIXML.parse(result_handle)]	

	return blast_list

def blacklist (blacklist_file):
	
	# return a list containing the blacklisted genbank id's
	# the blacklist follows the following format:
	# genbank_id, description
	
	return [line.split(',')[0] for line in open(blacklist_file,'r')]

def CITES_db (CITES_file):
	
	# open the local CITES database, return a dictionary
	# containing the CITES information with the taxid's as keys

	CITES_dic = {}
	
	for line in open(CITES_file, 'r'):
		line = line.split(',')
		CITES_dic[line[0]] = line[1:]

	return CITES_dic

def parse_blast (blast_list, filter_list, CITES_dic, outpath, mode):
	
	# parse_through the blast results and remove
	# results that do not meet the e-value, coverage,
	# identity and blacklist critera

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
				filter_hits([blast_result.query, ('\"' + alignment.title + '\"'), gb_num, str(identity),
						str(blast_result.query_length), str(hsp.expect), str(hsp.bits)],
						filter_list, CITES_dic, outpath, mode)


def obtain_tax (code):
	
	# a module from Biopython is imported to connect to the Entrez database
	from Bio import Entrez
	from Bio import SeqIO

	taxon = [[],[]]

	try:
		# based on the genbank id the taxon id is retrieved from genbank
		Entrez.email = "quick@test.com"
		handle = Entrez.efetch(db="nucleotide", id= code, rettype="gb",retmode="text")
		record = SeqIO.read(handle, "gb")

		# parse through the features and grap the taxon_id
		sub = record.features
		taxon[0] = sub[0].qualifiers['db_xref'][0].split(':')[1]
		taxon[1] = record.annotations['organism']

	except:
		pass

	return taxon

def filter_hits (blast, filter_list, CITES_dic, outpath, mode):
	
	# filter the blast hits, based on the minimum
	# identity, minimum coverage, e-value and the user blacklist
	if float(blast[3]) >= filter_list[0] and int(blast[4]) >= filter_list[1] and float(blast[5]) <= filter_list[2]:
		if blast[2] not in filter_list[3]:
			taxon = obtain_tax(blast[2])
			results = blast+taxon

			# check if the taxon id of the blast hit
			# is present in the CITES_dic
			if taxon[0] in CITES_dic:			
				results+CITES_dic[taxon[0]]
			
			# write the results
			write_results(','.join(results), outpath, mode)
			
			

def write_results (result, outpath, mode):
	
	# write the results to the output file
	out_file = open(outpath, mode)
	out_file.write(result + '\n')
	out_file.close()


def main ():
	blast_settings = [args.a, args.d, args.s, args.m]
	filter_list = [99, 100, 0.05,['300252683']]
	CITES_dic = {}
	header = 'query,hit,accession,identity,hit length,e-value,bit-score, taxon id, name, CITES species, CITES info, NCBI species, appendix'
	write_results(header, args.o, 'w')
	blast_list = blast_bulk(args.i, blast_settings)
	parse_blast(blast_list, filter_list, CITES_dic, args.o, 'a')
	

if __name__ == "__main__":
    main()

