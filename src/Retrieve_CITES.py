#!/usr/bin/env python

# This script creates a local CSV database that maps between taxa (could be higher 
# taxonomic levels than species) in the CITES appendices and those that the NCBI taxonomy
# uses to annotate sequences. The CSV database has the following header; note the 
# timestamp that is used, potentially, to trigger an update of the database:

# #Date of last update:
# Date,24 June 2014
# #taxon id,CITES species,CITES description,taxon species,CITES appendix

# The columns are as follows:
# - 'taxon id': the NCBI taxon id, an integer
# - 'CITES species': the taxon name used in the CITES appendix
# - 'CITES description': the CITES taxon name, potentially with further clarification
# - 'taxon species': the NBCI taxon name
# - 'CITES appendix': an integer for the CITES appendix in which the taxon occurs

# This database is created by accessing the online (web page) version of the CITES 
# appendices, parsing the HTML, and checking the encountered names against a taxonomic
# name resolution service.

# import the modules used by this script
import argparse, logging, os, sys, urllib2, re, unicodedata, requests, time
try:
	from BeautifulSoup import BeautifulSoup
except:
	from bs4 import BeautifulSoup
from Bio import Entrez

parser = argparse.ArgumentParser(description = 'Create a table containing the CITES species')

parser.add_argument('-db', '--CITES_db', metavar='CITES database name', dest='db',type=str,
			help='Name and path to the location for the CITES database', nargs='+')
parser.add_argument('-f', '--force', dest='f', action='store_true',
			help='Force updating the CITES database')
parser.add_argument('-l', '--logging', metavar='log level', dest='l', type=str,
			help = 'Set log level to: debug, info, warning (default) or critical see readme for more details.', default='warning')
parser.add_argument('-lf', '--log_file', metavar='log file', dest='lf', type=str,
			help = 'Path to the log file')

args = parser.parse_args()


def download_raw_CITES ():
	
	# open the url and read the .php webpage
	logging.debug('Downloading CITES appendix webpage.')	
	CITES_url = urllib2.urlopen('http://www.cites.org/eng/app/appendices.php')
	CITES_php = CITES_url.read()

	# return the raw .php file
	return CITES_php


def local_CITES_data ():
	
	# open the local CITES database(s) to retrieve the date and path of output file
	results_dic = {}
	logging.debug('CITES files %s' % ' '.join(args.db))
	logging.debug('Trying to open the CITES databases provided by the user.')
	for path in args.db:
		logging.debug('Trying to open CITES database %s.' % path)
		try:
			for line in open(path, 'r'):
				line = line.rstrip().split(',')
				if line[0] == 'Date':
					results_dic['Date'] = line[1]
					results_dic['output'] = path
			if len(results_dic) == 0:
				logging.debug('No date found in CITES database %s, new CITES copy will be writen to this location.' % path)
				results_dic['output'] = path
		except:
			logging.debug('Could not open CITES database %s, new CITES copy will be writen to this location.' % path)
			results_dic['output'] = path
	return results_dic

	
def clean_cell (cell):
	
	# minor function to clean up the html tags and 
	# formating of the CITES appendix

	# Try to remove tags, if not possible return a blank
	try:
		cell = str(''.join(cell.findAll(text=True)).encode('ascii','ignore')).replace('\n', ' ')
		regex = re.compile(r'[\n\r\t]')
		cell = regex.sub('', cell).strip().replace('&nbsp;',' ')
		cell = re.sub(r'&(#?)(.+?);','',cell)
	
		while '  ' in cell:
			cell = cell.replace('  ', ' ')

		return cell

	except:
		return ''


def parse_php (php_file):

	# fill this dictionary with all species for the 3
	# CITES categories. Each value will consist of an array whose first element is the
	# taxon name, second element is name + description, third element is an array of
	# footnote ID references
	CITES_dict = {1:[],2:[],3:[]}
	
	# create a dictionary for the CITES footnotes
	CITES_notes = {}

	# read the CITES web page as BeautifulSoup object hierarchy
	logging.debug('Parsing the CITES html page.')
	CITES_page = BeautifulSoup(php_file)

	# TODO: is this the time stamp?
	data = clean_cell(CITES_page.b.find('strong'))
	
	# table rows with the c10 class as well as having 4 cells in them are name records
	# in the CITES appendices. The cell/column number is the appendix number.
	trs = CITES_page.findAll('tr', { 'class' : 'c10' } )
	for tr in trs:
		tds = tr.findAll('td')
		
		# fewer columns would mean this is a header row
		if len(tds) == 4:
			for i in range(1,4):
				text = clean_cell(tds[i])
				if re.match('\w', text):
					words = []
					
					# until a word starts with one of these special characters [({
					# the words are part of the taxon name
					for word in text:
						if re.match('[\(\{\[#]', word):
							break
						else:
							words.append(word)
					
					# concatenate words, strip out footnote ID references
					taxon = ''.join(words)
					taxon = re.sub(r'#*\d+','',taxon)
					logging.debug('CITES appendix %d taxon %s' % ( i, taxon ) )
					
					# collect the footnote ID references by their link tags
					footnotes = [ clean_cell(note) for note in tds[i].findAll('a') ]
					CITES_dict[i].append([ taxon, clean_cell(tds[i]), footnotes ])
	
	# parse through the footnotes and create
	# a dictionary for each one of the notes
	logging.debug('Parsing the CITES appendix footnotes.')
	fntable = CITES_page.findAll( 'table', { 'border' : 2 } )
	rows = fntable[0].findAll('tr')
	for tr in rows:
		notes = tr.findAll('td')
		CITES_notes[clean_cell(notes[0])] = clean_cell(notes[1])
		
	
	# return a list containing the data, species dictionary and CITES footnotes
	return [data, CITES_dict, CITES_notes]


def TNRS (name):
	
	# Send the TNRS request
	logging.debug('Send TNRS request to server. %s' % name)
	url = 'http://resolver.globalnames.org/name_resolvers.json'
	TNRS_req = requests.get( url, params = { 'names' : name }, allow_redirects = True )
	logging.debug('url: %s' % TNRS_req.url)		# Fout kan ook in de .url zitten
	redirect_url, time_count = TNRS_req.url, 0

	# send retrieve requests at 5 second intervals till
	# the api returns the JSON object with the results
	while redirect_url and time_count < 10:

		# Try to Download the JSON object with the TNRS results.
		try:
			retrieve_response = requests.get(redirect_url)
			retrieve_results = retrieve_response.json()
		except:
			retrieve_results = []
		
		# if the results contains the JSON object
		# retrieve all accepted names for the species
		# and return these
		if u'name_string' in retrieve_results[u'data'][0][u'results'][0].keys():
			logging.debug('Parsing TNRS results.')
			name_list = [name,[]]
			try:
				logging.debug(retrieve_results[u'data'])
				for lijst in retrieve_results[u'data']:
					for lijst_2 in lijst[u'results']:
						if lijst_2[u'data_source_title'] == 'NCBI':
							name_list.append(lijst_2[u'taxon_id'])
							synonym = lijst_2[u'name_string']
							logging.debug('Synoniem gevonden: %s' % synonym)
							if synonym not in name and synonym != '':
								if ' ' in name:
									if len(synonym.split(' ')) >= len(name.split(' ')):
										name_list[1].append(str(synonym))
								else:
									if ' ' not in synonym:
										name_list[1].append(str(synonym))					
			except:
				pass

			# return the list with species names
			return name_list
		
		# time out before sending the new request
		# use a counter to keep track of the time, if there is
		# still no server reply the function will return an empty list
		time.sleep(5)
		time_count += 5

	logging.warning('Timeout for species %s.' % name)
	return [name,[]]

def get_taxid (species):
	
	# get taxon id based on species name (if not provided by TNRS search)

	# correct species name for parsing and set temp email
	Entrez.email = "HTS-barcode-checker@gmail.com"
	species = species.replace(' ', '+').strip()
	
	# Do a taxonomy search to determine the number of subtaxa
	# If there are more subtaxa then NCBI returns by default (20)
	# do a second search with the retmax parameter set to the 
	# expected number of taxa.
	try:
		# Connect to Entrez to obtain subtree size
		search = Entrez.esearch(term = (species + ' [subtree]'), db = "taxonomy", retmode = "xml")
		record = Entrez.read(search)
		count = record['Count']
	
		# is subtree size exceeds 20 the entire tree needs to be redownloaded
		if count > 20:
			search = Entrez.esearch(term = (species + ' [subtree]'), db = "taxonomy", retmode = "xml", retmax = count)
			record = Entrez.read(search)

		# if the tree isnt empty, return the taxon ID list.
		if record['IdList'] != []:	
			return record['IdList']
	except:
		pass

	return ['empty']


def obtain_tax (taxid):

	organism = ''

	# based on the taxid the species and taxonomy are retrieved from the Entrez database
	try:
		Entrez.email = "CITES_check@gmail.com"
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

	taxon_id_dic, CITES_length, failed = {}, sum([len(CITES_dic[appendix]) for appendix in CITES_dic]), 0
	total = CITES_length

	logging.info('Total number of CITES entries: %i.' % CITES_length)

	logging.debug('Parse through the CITES species found per appendix.')
	for appendix in CITES_dic:
		logging.debug('Parsing through species found in appendix: %s.' % str(appendix))
		for cell in CITES_dic[appendix]:
			# create a list of all lower taxon id's
			temp_name, temp_taxon_list, count = cell[0].replace(' spp.',''), ['empty'], 0
			
			# break when a cell turns out to be empty			
			if temp_name == '' or temp_name == ' ': 
				failed += 1
				continue			

			# grab the TAXON IDs for the species name
			while temp_taxon_list[0] == 'empty' and count <= 20:
				temp_taxon_list = get_taxid(temp_name)
				count += 1

			if temp_taxon_list[0] == 'empty': 
				logging.warning('No taxon ID found for: %s.' % temp_name)
				failed += 1

			# if no TAXON ID was found for the name
			# check if taxon IDs can be obtained for
			# the species synonyms
			if temp_taxon_list[0] == 'empty':
				logging.debug('Looking for synonym species: %s.' % temp_name)
				temp_taxon_list = []
				TNRS_data = TNRS(temp_name)
				if len(TNRS_data) < 3 and len(TNRS_data[1]) > 0:
					for name in TNRS_data[1]:
						count, temp_tnrs = 0, ['empty']
						while temp_tnrs[0] == 'empty' and count <= 20:						
							temp_tnrs = get_taxid(name)
							count += 1
						if temp_tnrs[0] != 'empty': temp_taxon_list += temp_tnrs
					# print the synomyms for who a taxon id could be found					
					if len(temp_taxon_list) > 0: 
						logging.debug('Synonym found for %s, taxon ID(s) = %s.' % (temp_name, ' '.join(temp_taxon_list)))
			
			if temp_taxon_list == []: 
				logging.critical('No synonym found for: %s.' % temp_name)
				failed += 1

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

			# print the number of remaining CITES entries to process
			CITES_length -= 1
			logging.debug('%i CITES entries remaining' % CITES_length)			
	
	logging.info('No taxon ID found for %i out of the %i species' % (failed, total))	
	
	return taxon_id_dic
			

def write_csv (date, taxon_id_dic, file_path):

	# write the CITES results to the database
	logging.debug('Writing CITES results to %s.' % file_path)
	db = open(file_path, 'w')
	db.write('#Date of last update:\nDate,' + date + '\n#taxon id,CITES species,CITES description,taxon species,CITES appendix\n')
	for taxid in taxon_id_dic:
		db.write(','.join([taxid] + taxon_id_dic[taxid]) + '\n')
	db.close()
			

def main ():	

	# set log level
	log_level = getattr(logging, args.l.upper(), None)
	log_format = '%(funcName)s [%(lineno)d]: %(levelname)s: %(message)s'
	if not isinstance(log_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)
		return
	if args.lf == '':
		logging.basicConfig(format=log_format, level=log_level)
	else:
		logging.basicConfig(filename=args.lf, filemode='a', format=log_format, level=log_level)

	# retrieve the raw CITES appendix page
	logging.info('Downloading CITES appendix.')
	CITES_php = download_raw_CITES()

	# parse through the CITES page and retrieve the
	# species names
	logging.info('Parsing CITES entries.')
	CITES_info = parse_php(CITES_php)
	
	# try to open the CITES database and check if the current version
	# (if there is one) is up to date
	file_data = local_CITES_data()
	for i in file_data:
		logging.debug('CITES files %s - path %s' % (i, file_data[i]))
	output_path = file_data['output']
	logging.debug('Test if the current version of the CITES database is up to date.')
	try:
		if CITES_info[0] == file_data['Date'] and args.f != True:
			logging.info('Local CITES database is up to data.')
			return
	except:
		pass

	logging.info('Downloading new copy of CITES database.')

	# use TNRS to grab the species synonyms and
	# taxid if available. Expand the taxids with 
	# taxids from lower ranked records
	logging.debug('Get taxon IDs for CITES species.')
	taxon_id_dic = combine_sets(CITES_info[1], CITES_info[2])

	# write the results to the output location
	logging.debug('Write CITES info to output file %s.' % output_path)
	write_csv(CITES_info[0], taxon_id_dic, output_path)


if __name__ == "__main__":
	main()	

