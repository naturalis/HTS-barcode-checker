#!/usr/bin/env python

from hts_barcode_checker import Taxon, TaxonDB
import logging, datetime, argparse

parser = argparse.ArgumentParser(description = 'Create a table containing the CITES species')

parser.add_argument('-db', '--CITES_db', metavar='CITES database name', dest='db',type=str,
			help='Name and path to the location for the CITES database')
parser.add_argument('-dmp', '--CITES_dump', metavar='CITES CSV dump', dest='dmp', type=str,
			help='Location of the CSV dump downloaded from CITES')
parser.add_argument('-n', '--NCBI_names', metavar='NCBI taxid to names mapping', dest='n', type=str,
			help='Location of tab-separated NCBI taxid to names mapping')
parser.add_argument('-l', '--logging', metavar='log level', dest='l', type=str,
			help = 'Set log level to: debug, info, warning (default) or critical see readme for more details.', default='warning')
parser.add_argument('-lf', '--log_file', metavar='log file', dest='lf', type=str,
			help = 'Path to the log file')

args = parser.parse_args()


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

	# instantiate DB object, parse dump
	db = TaxonDB(date=str(datetime.datetime.now()))
	db.from_dump(args.dmp)
	
	# do TNRS, with cached ID<->name mapping
	mapping = db.read_taxids(args.n)
	reverse = dict((y,x) for x,y in mapping.iteritems())
	counter = 1	
	for taxon in db.taxa:
		try:
			taxon.tnrs(reverse=reverse)
		except:
			pass            
		logging.info('%d/%d' % ( counter, len(db.taxa) ))
		counter += 1
	
	# write output
	outfile = open(args.db, 'w')
	outfile.write(db.to_csv())
	outfile.close()

if __name__ == "__main__":
	main()	

