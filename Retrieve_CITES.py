#!/usr/bin/env python

# Create a local database containing the CITES appendices
# Database contains the CITES species names and synonymes based on:
# and the species ncbi species taxon identifier


# import the argparse module to handle the input commands
#import argparse, sys

#parser = argparse.ArgumentParser(description = 'Create a table containing the CITES species')

#parser.add_argument('--download', metavar='', type=str, 
#			help='Enter the 454 sequence fasta file(s)', nargs='+')
#parser.add_argument('--output_dir', metavar='output directory', type=str, 

def download_raw_CITES ():
	
	# import the urllib2 module used to download the Cites appendices
	import urllib2

	# open the url and read the .php webpage
	CITES_url = urllib2.urlopen('http://www.cites.org/eng/app/appendices.php')
	CITES_php = CITES_url.read()

	#print(CITES_php)

	# return the raw .php file
	return CITES_php


def clean_cell (cell):
	
	import re

	regex = re.compile(r'[\n\r\t]')
	cell = regex.sub('', cell)
	
	while '  ' in cell:
		cell = cell.replace('  ', ' ')

	return cell	


def parse_php (php_file):

	# import BeautifulSoup to parse the webpage
	from BeautifulSoup import BeautifulSoup
	
	# fill this dictionary with all species for the 3
	# CITES categories
	CITES_dict = {1:[],2:[],3:[]}
	
	# read the CITES web page	
	CITES_page = BeautifulSoup(php_file)
	
	# extract the tables
	tables = CITES_page.findAll('table')
	
	# parse through the table and find all cites species
	# (in bold / italic) and under which category they fit
	rows = tables[1].findAll('tr')
	for tr in rows[2:]:
		cols = tr.findAll('td')
		count = 1
		for td in cols:
			cell = td.find('b')
			# if the cell is filled, retrieve the
			# species name and add it to the dictionary
			if cell != None:
				cell = str(''.join(cell.findAll(text=True)))
				if ';' in cell:	cell = cell.split(';')[1]
				CITES_dict[count].append(clean_cell(cell))
			count += 1
	
	# return the dictionary containing the species
	return CITES_dict			


def TNRS (name):
	
	# import the request module to connect to the TNRS api
	# and deal with the JSON resuls and the time module
	# to prevent floading of the api
	import requests, time

	# Send the TNRS request
	TNRS_req = requests.get('http://api.phylotastic.org/tnrs/submit',
		params={'query':name},
		allow_redirects=True)

	redirect_url = TNRS_req.url

	# send retrieve requests at 5 second intervals till
	# the api returns the JSON object with the results
	while redirect_url:
		retrieve_response = requests.get(redirect_url)
		retrieve_results = retrieve_response.json()
		
		# if the results contains the JSON object
		# retrieve all accepted names for the species
		# and return these
		if u'names' in retrieve_results:
			name_list = []
			names = retrieve_results.get(u'names')
			for item in names[0]['matches']:
				name_list.append(str(item['acceptedName']))

			# return the list with species names
			return name_list
		time.sleep(5)


def main ():
	
	#CITES_php = download_raw_CITES()
	#CITES_dic = parse_php(CITES_php)
	names = TNRS('Aloe pillansii')
	print names

if __name__ == "__main__":
    main()
