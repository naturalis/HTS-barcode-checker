# descrip


# import the argparse module to handle the input commands
import argparse

# get the commandline arguments that specify the input fastafile and the output file
parser = argparse.ArgumentParser(description = ('retrieve blast and taxonomic information for a fasta file'))

parser.add_argument('-i', metavar='fasta file', type=str, 
			help='enter the fasta file')
parser.add_argument('-o', metavar='output file', type=str, 
			help='enter the output file')
args = parser.parse_args()

def blast_bulk (fasta_file):

	# The blast modules are imported from biopython
	from Bio.Blast import NCBIWWW, NCBIXML

	# open the fasta file
	fasta_open = open(fasta_file, 'r')
	fasta_handle = fasta_open.read()
	
	blast_list = []

	# Blast the sequences against the NCBI nucleotide database
	# return a list with the blast results
	result_handle = NCBIWWW.qblast('blastn', 'nt', fasta_handle)
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

def parse_blast (blast_list):#, e_value, min_coverage, min_identity):
	
	# parse_through the blast results and remove
	# results that do not meet the e-value, coverage,
	# identity and blacklist critera

	for blast_result in blast_list:
		for alignment in blast_result.alignments:
			for hsp in alignment.hsps:
	            		
				# calculate the %identity
		            	identity = float(hsp.identities/(len(hsp.match)*0.01))
				
				# an alignment needs to meet 3 criteria before 
				# it is an acceptable result: above the minimum 
				# identity, minimum coverage and E-value
			
				result_list = [blast_result.query, ('\"' + alignment.title + '\"'), identity,
						blast_result.query_length,hsp.expect, hsp.bits]

				print obtain_tax(alignment.title.split('|')[1])
				print alignment.title
				print hsp
				print hsp.expect

				return
	
				#blast_record.query, b = alignment.hit_def, c = hsp.bits, d = cover, e = hsp.expect, f = ident, g = alignment.hit_id)	

				#if int(hsp.expect) < e_value and identity > min_identity and blast_result.query_length > min_identity:
					
					# compare the 

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

def filter_hits (blast, filter_dic, blacklist, CITES_dic):
	
	# filter the blast hits, based on the e-value, minimum
	# identity, minimum coverage and the user blacklist
	if blast_data[0] <= blast_filter[0] and blast_data[1] >= blast_filter[1] and blast_data[2] >= blast_data[2]:
		if blast_data[3] not in blacklist:
			taxon_id = obtain_tax(blast_data[3])
			if taxon_id in CITES_dic:
				write_results()
			else:
				write_results()

def write_results (result):
	pass

def main ():
	filter_crit = [0.05, 97, 100]
	black_list = []
	CITES_dic = {}
	blast_list = blast_bulk(args.i)
	parse_blast(blast_list)
	

if __name__ == "__main__":
    main()

