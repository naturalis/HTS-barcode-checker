#!/usr/bin/env python

from hts_barcode_checker import Taxon, TaxonDB
import logging, datetime, argparse, sqlite3

# NCBI taxonomy tree database 10.6084/m9.figshare.4620733

parser = argparse.ArgumentParser(description = 'Create a table containing the CITES species')

parser.add_argument('-db', '--CITES_db', metavar='CITES database name', dest='db',type=str,
			help='Name and path to the output location for the CITES database')
parser.add_argument('-csv', '--CITES_dump', metavar='CITES CSV dump', dest='dmp', type=str,
			help='Location of the CSV dump downloaded from CITES')
parser.add_argument('-ncbi', '--NCBI_taxonomy', metavar='NCBI taxonomy tree database', dest='n', type=str,
			help='Location of sqlite database with NCBI taxonomy tree')
parser.add_argument('-l', '--logging', metavar='log level', dest='l', type=str,
			help = 'Set log level to: debug, info, warning (default) or critical see readme for more details.', default='warning')
parser.add_argument('-lf', '--log_file', metavar='log file', dest='lf', type=str,
			help = 'Path to the log file')

args = parser.parse_args()


def main ():
	
	# configure logger
	log_level = getattr(logging, args.l.upper(), None)
	log_format = '%(funcName)s [%(lineno)d]: %(levelname)s: %(message)s'
	if not isinstance(log_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)
		return
	if args.lf == '':
		logging.basicConfig(format=log_format, level=log_level)
	else:
		logging.basicConfig(filename=args.lf, filemode='a', format=log_format, level=log_level)	

	# instantiate DB object, parse CITES dump
	db = TaxonDB(date=str(datetime.datetime.now()))
	db.from_dump(args.dmp)
	
	# configure local sqlite database
	conn = sqlite3.connect(args.n)
	curr = conn.cursor()

	# iterate over parsed taxa, resolve NCBI taxid and expand higher taxa
	counter  = 1
	expanded = []
	for taxon in db.taxa:
		taxon.tnrs(cursor=curr)
		result = taxon.expand(cursor=curr)
		for taxid in result.keys():
			expanded.append(Taxon(
				appendix=taxon.appendix,
				name=taxon.name,
				description=taxon.description,
				footnotes=taxon.footnotes,
				ncbi={taxid:result[taxid]}
			))
		logging.info('%d/%d' % ( counter, len(db.taxa) ))
		counter += 1
	
	# write output
	for taxon in expanded:
		db.taxa.append(taxon)
	handle = open(args.db, 'w')
	db.to_csv(handle)
	handle.close()

if __name__ == "__main__":
	main()	

