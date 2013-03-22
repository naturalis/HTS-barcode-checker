#!/usr/bin/env python

# Create a local database containing the CITES appendices
# Database contains the CITES species names and synonymes based on:
# and the species ncbi species taxon identifier


# import the argparse module to handle the input commands
import argparse

parser = argparse.ArgumentParser(description = 'Create a table containing the CITES species')

parser.add_argument('-db', '--CITES_db', metavar='CITES database name', dest='db',type=str,
			help='Name and path to the location for the CITES database', nargs='+')
parser.add_argument('-f', '--force', dest='f', action='store_true',
			help='Force updating the CITES database')
args = parser.parse_args()


def download_raw_CITES ():
	
	# import the urllib2 module used to download the Cites appendices
	import urllib2

	# open the url and read the .php webpage
	CITES_url = urllib2.urlopen('http://www.cites.org/eng/app/appendices.php')
	CITES_php = CITES_url.read()

	# return the raw .php file
	return CITES_php


def CITES_date ():
	
	# open the local CITES database(s) to retrieve the date of the last update
	for path in args.db:
		for line in open(path, 'r'):
			line = line.rstrip().split(',')
			if line[0] == 'Date':
				return line[1]

	
def clean_cell (cell):
	
	# minor function to clean up the html tags and 
	# formating of the CITES appendix
	import re, unicodedata

	# Try to remove tags, if not possible return a blank
	try:
		cell = str(''.join(cell.findAll(text=True)).encode('ascii','ignore'))
		regex = re.compile(r'[\n\r\t]')
		cell = regex.sub('', cell).strip().replace('&nbsp;',' ')
		cell = re.sub(r'&(#?)(.+?);','',cell)
	
		while '  ' in cell:
			cell = cell.replace('  ', ' ')

		return cell

	except:
		return ''


def parse_php (php_file):

	# import BeautifulSoup to parse the webpage
	from BeautifulSoup import BeautifulSoup
	import re
	
	# fill this dictionary with all species for the 3
	# CITES categories
	CITES_dict = {1:[],2:[],3:[]}
	
	# create a dictionary for the CITES footnotes
	CITES_notes = {}

	# read the CITES web page	
	CITES_page = BeautifulSoup(php_file)
	
	data = clean_cell(CITES_page.find('strong'))

	# extract the tables
	tables = CITES_page.findAll('table')

	# parse through the table and find all cites species
	# (in bold / italic) and under which category they fit
	rows = tables[1].findAll('tr')
	for tr in rows[2:]:
		cols = tr.findAll('td')
		count = 1
		for td in cols:
			cleaned = clean_cell(td.find('b'))
			# if the cell is filled, retrieve the
			# species name and add it to the dictionary
			#if cell != None and cell != ' ' and cell != '':
			if cleaned != '':			
				if ';' in cleaned: cleaned = cleaned.split(';')[1]
				CITES_dict[count].append([cleaned,clean_cell(td),[clean_cell(note) for note in td.findAll('a')]])

			count += 1

	# parse through the footnotes and create
	# a dictionary for each one of the notes
	rows = tables[2].findAll('tr')
	for tr in rows:
		notes = tr.findAll('td')
		CITES_notes[clean_cell(notes[0])] = clean_cell(notes[1])
		
	
	# return a list containing the data, species dictionary and CITES footnotes
	return [data, CITES_dict, CITES_notes]


def TNRS (name):
	
	# import the request module to connect to the TNRS api
	# and deal with the JSON resuls and the time module
	# to prevent floading of the api
	import requests, time

	# Send the TNRS request
	TNRS_req = requests.get('http://api.phylotastic.org/tnrs/submit',
		params={'query':name}, allow_redirects=True)

	redirect_url, time_count = TNRS_req.url, 0

	# send retrieve requests at 5 second intervals till
	# the api returns the JSON object with the results
	while redirect_url and time_count < 15:
		retrieve_response = requests.get(redirect_url)
		retrieve_results = retrieve_response.json()
		
		# if the results contains the JSON object
		# retrieve all accepted names for the species
		# and return these
		if u'names' in retrieve_results:
			name_list = [name,[]]
			names = retrieve_results.get(u'names')
			try:
				for item in names[0]['matches']:
					if item['sourceId'] == 'NCBI':
						name_list.append(str(item['uri']).split('/')[-1])
					synonym = item['acceptedName']
					
					if synonym not in name and synonym != '':
						if ' ' in name:
							if len(synonym.split(' ')) >= len(name.split(' ')):
								name_list[1].append(str(item['acceptedName']))
						else:
							if ' ' not in synonym:
								name_list[1].append(str(item['acceptedName']))						
			except:
				pass

			# return the list with species names
			return name_list
		
		# time out before sending the new request
		# use a counter to keep track of the time, if there is
		# still no server reply the function will return an empty list
		time.sleep(5)
		time_count += 5

	print('Timeout for species %s' % name)
	return [name,[]]


def get_taxid (species):
	
	# get taxon id based on species name (if not provided by TNRS search)

	# import Entrez module from biopython to connect to the genbank servers
	from Bio import Entrez
	#import time

	# correct species name for parsing and set temp email
	Entrez.email = "get_taxid@expand_CITES.com"
	species = species.replace(' ', '+').strip()
	
	# Do a taxonomy search to determine the number of subtaxa
	# If there are more subtaxa then NCBI returns by default (20)
	# do a second search with the retmax parameter set to the 
	# expected number of taxa.
	try:
		search = Entrez.esearch(term = (species + ' [subtree]'), db = "taxonomy", retmode = "xml")
		record = Entrez.read(search)
		count = record['Count']

		if count > 20:
	
			search = Entrez.esearch(term = (species + ' [subtree]'), db = "taxonomy", retmode = "xml", retmax = count)
			record = Entrez.read(search)

		if record['IdList'] != []:
	
			return record['IdList']
	except:
		print('failed to obtain hit for %s' % species)

	return []


def obtain_tax (taxid):
	# a module from Biopython is imported to connect to the Entrez database
	from Bio import Entrez
	#import time
		
	organism = ''

	# based on the taxid the species and taxonomy are retrieved from the Entrez database
	try:
		Entrez.email = "get_taxid@expand_CITES.com"
		search = Entrez.efetch(db="taxonomy", id= taxid, retmode="xml")
		record = Entrez.read(search)
		organism = '\"' + record[0]['ScientificName'] + '\"'
		handle.close()
	except:
		pass

	return organism


def combine_sets (CITES_dic, CITES_notes):
	
	# Expand the CITES information with TNRS synonyms and Taxonomic IDs

	# parse through the different CITES appendixes and
	# and try to retrieve the TNRS synonyms and NCBI Taxonomic IDs
	# for each species

	taxon_id_dic = {}

	for appendix in CITES_dic:
		for cell in CITES_dic[appendix]:
			# create a list of all lower taxon id's
			temp_name = cell[0].replace(' spp.','')
			
			# break when a cell turns out to be empty			
			if temp_name == '' or temp_name == ' ': continue			

			# grab the TAXON IDs for the species name
			temp_taxon_list = get_taxid(temp_name)

			# if no TAXON ID was found for the name
			# check if taxon IDs can be obtained for
			# the species synonyms
			if temp_taxon_list == []:
				TNRS_data = TNRS(temp_name)
				if len(TNRS_data) < 3 and len(TNRS_data[1]) > 0:
					for name in TNRS_data[1]:
						temp_taxon_list += get_taxid(name)
					# print the synomyms for who a taxon id could be found					
					if len(temp_taxon_list) > 0: 
						print temp_name
						print temp_taxon_list
						print '\n'
			
			# expand the taxon_id_dic with the taxid's as
			# keys and the CITES species / CITES cell and 
			# taxid linked species as values
			for taxid in temp_taxon_list:
				CITES_info = cell[1]			
				if taxid in taxon_id_dic:
					if appendix > int(taxon_id_dic[taxid][3]): continue
				
				# check if footnotes need to be attached:
				if len(cell[2]) != 0:
					for item in cell[2]:
						if item != ' ' and item != '':
							CITES_info += (' %s: %s' % (item, CITES_notes[item]))
	
				taxon_id_dic[taxid] = [cell[0],'\"' + CITES_info + '\"',obtain_tax(taxid),str(appendix)]
	
	return taxon_id_dic
			

def write_csv (date, taxon_id_dic):

	# write the CITES results to the database
	
	db = open(args.db, 'w')
	db.write('#Date of last update:\nDate,' + date + ',\n#taxon id,CITES species,CITES description,taxon species,CITES appendix\n')
	for taxid in taxon_id_dic:
		db.write(','.join([taxid] + taxon_id_dic[taxid]) + '\n')
	db.close()
			

def main ():	
	# retrieve the raw CITES appendix page
	CITES_php = download_raw_CITES()

	# parse through the CITES page and retrieve the
	# species names
	CITES_info = parse_php(CITES_php)
	
	# try to open the CITES database and check if the current version
	# (if there is one) is up to date
	try:
		if CITES_info[0] == CITES_date() and args.f != True:
			print 'Local CITES database is up to date'
			return
	except:
		pass

	print 'Downloading new local copy of the CITES database'

	# use TNRS to grab the species synonyms and
	# taxid if available. Expand the taxids with 
	# taxids from lower ranked records
	taxon_id_dic = combine_sets(CITES_info[1], CITES_info[2])

	# write the results to the output location
	write_csv(CITES_info[0], taxon_id_dic)
	

if __name__ == "__main__":
	main()	

