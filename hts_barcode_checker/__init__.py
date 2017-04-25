import logging, urllib2, re, unicodedata, requests, time
import unicodecsv as csv
from io import BytesIO
from Bio import Entrez
try:
	from BeautifulSoup import BeautifulSoup
except:
	from bs4 import BeautifulSoup

class Taxon(object):    
	
	def __init__(self, **kwargs):
		
		"""Instantiates a HTSBarcodeChecker object, which encapsulates the data and \
		behaviors to reconcile the CITES appendices with the NCBI taxonomy, such that \
		BLAST results (which are annotated to NCBI species level) can be matched against \
		CITES (which uses higher taxa, possibly synonymous). Also configures the logger \
		for this class."""
		
		# process instance variable arguments
		self.appendix    = kwargs.get('appendix',None)
		self.name        = kwargs.get('name',None)
		self.description = kwargs.get('description',None)
		self.footnotes   = kwargs.get('footnotes',{})
		self.ncbi        = kwargs.get('ncbi',{})
		
		# process loglevel argument, warnings are default
		loglevel = kwargs.get('loglevel',logging.WARNING)
		if not isinstance(loglevel, int):
			raise ValueError('Invalid log level: %s' % loglevel)
			return
		
		# configure logger, optionally to file
		logfrmt = '%(funcName)s [%(lineno)d]: %(levelname)s: %(message)s'
		logfile = kwargs.get('logfile',None)
		if logfile == None:
			logging.basicConfig(format=logfrmt, level=loglevel)
		else:
			logging.basicConfig(filename=logfile, filemode='a', format=logfrmt, level=loglevel)
	
	def tnrs(self,cursor=None):
		
		"""Once the CITES name property is set, fetches the NCBI names and taxon ID."""
		
		logging.info('Resolving taxon "%s"' % self.name)

		# attempt to do an exact match against the local sqlite database via cursor
		if cursor != None:
			name = unicode(self.name)
			cursor.execute('select id from node where name=?', (name,))
			result = cursor.fetchone()
			if result != None:      
				self.ncbi[result[0]] = self.name
				logging.info('"%s" had exact local match: %d' % (self.name,result[0]))
				return
			else:
				logging.debug('No exact match local match for "%s"' % self.name ) 

		# no cursor or exact match, try TNRS
		try:
			url = 'http://resolver.globalnames.org/name_resolvers.json'
			response = requests.get(url, params={'names':self.name}, allow_redirects=True)
			json = response.json()
		except:
			logging.warn('TNRS globalnames connection error')
			json = []
			
		# if the JSON object has results, iterate over all matches
		if u'results' in json[u'data'][0].keys():
			if u'name_string' in json[u'data'][0][u'results'][0].keys():
				logging.debug('Received JSON object')
				for data_dict in json[u'data']:
					m = 0
					for results_dict in data_dict[u'results']:
							
						# the focal result is a match in the NCBI taxonomy
						if results_dict[u'data_source_title'] == 'NCBI':
								
							# store the NCBI taxon ID and name
							taxid = int(results_dict[u'taxon_id'])
							match = results_dict[u'name_string']
							self.ncbi[taxid] = match
							m += 1
							logging.debug('Added match {%d:"%s"}' % (taxid,match))
					
					# log number of checked data sources
					s = len(data_dict[u'results'])
					n = self.name
					logging.info('Found %d matches for %s in %d data sources' % (m,n,s))					

				# we processed a valid payload. done.
				return
	
	def expand(self,cursor=None):
		
		"""Expands the set of NCBI taxon IDs to the full subtree."""
		
		# attempt to do the expansion using the local sqlite database via cursor
		if cursor != None:
			logging.debug('Will expand %s using local database' % self.name)
			result = {}
			for taxid in self.ncbi.keys():
				logging.debug('Expanding id {0}'.format(taxid))
				cursor.execute('select left,right from node where id=?', (taxid,))
				lr = cursor.fetchone()
				if lr != None and lr[0] != lr[1]:
					l1 = lr[0] + 1
					l2 = lr[1] - 1
					logging.debug('left={0} right={1}'.format(l1,l2))
					for row in cursor.execute('select id,name from node where left between ? and ?', (l1,l2,)):
						logging.debug('descendant {0}={1}'.format(row[0],row[1]))
						result[row[0]] = row[1]
			logging.info('Expanded %s to %d descendants' % (self.name,len(result.keys())))
			return result

		# no cursor, use Entrez. Beware: this is slow
		Entrez.email = "HTS-barcode-checker@gmail.com"
		for species in self.ncbi.values():
			if species == None:
				logging.debug("species name is not defined")
				continue
			
			# do a taxonomy search to determine the number of subtaxa
			# if there are more subtaxa than NCBI returns by default (20)
			# do a second search with the retmax parameter set to the 
			# expected number of taxa.            
			logging.info('Expanding taxon "%s"' % species)
			query  = species + ' [subtree]'
			query  = query.replace(' ', '+').strip()
			search = Entrez.esearch(term=query, db="taxonomy", retmode="xml")
			record = Entrez.read(search, validate=False)        
			count  = int(record['Count'])
			logging.debug('JSON results count: %d' % count)
		
			# is subtree size exceeds 20 the entire tree needs to be redownloaded
			if count > 20:
				search = Entrez.esearch(term=query, db="taxonomy", retmode="xml", retmax=count)
				record = Entrez.read(search, validate=False)        

			# if the tree isnt empty, store the taxon ID list.
			result = {}
			for taxidstr in record['IdList']:
				taxid = int(taxidstr)
				if taxid in self.ncbi:
					logging.debug('Already seen %s for %s' % (taxid,self.ncbi[taxid]))
				else:
					if taxid in mapping:						
						result[taxid] = unicode(mapping[taxid])                        
					else:                            
						search = Entrez.efetch(db="taxonomy", id=str(taxid), retmode="xml")
						record = Entrez.read(search)
						result[taxid] = unicode(record[0]['ScientificName'])
					logging.debug('Stored NCBI taxon ID %s' % taxid)
			return result
	
	def to_csv(self,handle=BytesIO()):
		
		"""Stringifies the invocant in the format of records in CITES_db.csv."""
		
		writer = csv.writer(handle,encoding='utf-8')
		for taxid in self.ncbi.keys():
			
			# NCBI id, CITES species, CITES description, NCBI species, CITES appendix
			writer.writerow((
				unicode(taxid),
				unicode(self.name),
				unicode(self.description),
				unicode(self.ncbi[taxid]),
				unicode(self.appendix)
			))
		return handle
	
class TaxonDB(object):
	
	def __init__(self, **kwargs):        
		
		# file locations
		self.db        = kwargs.get('db',None)
		self.blacklist = kwargs.get('blacklist',None)
		self.additions = kwargs.get('additions',[])
		
		# latest CITES release
		self.date = kwargs.get('date',None)
		
		# in-memory db
		self.taxa = kwargs.get('taxa',[])
		
		# process loglevel argument, warnings are default
		loglevel = kwargs.get('loglevel',logging.WARNING)
		if not isinstance(loglevel, int):
			raise ValueError('Invalid log level: %s' % loglevel)
			return
		
		# configure logger, optionally to file
		logfrmt = '%(funcName)s [%(lineno)d]: %(levelname)s: %(message)s'
		logfile = kwargs.get('logfile',None)
		if logfile == None:
			logging.basicConfig(format=logfrmt, level=loglevel)
		else:
			logging.basicConfig(filename=logfile, filemode='a', format=logfrmt, level=loglevel)
		logging.debug("Instantiated database")
	
	def clean_cell (self,cell):
	
		"""Helper function to clean up html and formating of the CITES appendix."""
	
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
		
	def read_taxids(self,path=None):
		
		"""Reads the id-to-name mapping in taxonid_names.tsv."""
		
		# open the file and read the .tsv
		mapping = {}
		logging.debug('Going to read tsv file "%s"' % path)
		for line in open(path, 'r'):
			line = line.rstrip().split('\t')
			mapping[int(line[0])] = unicode(line[1])
		return mapping
	
	def from_csv(self,path=None,add=False):

		"""Reads a previously constructed CITES<->NCBI CSV mapping database."""
		
		# open the file and read the .csv
		logging.debug('Going to read csv file "%s"' % path)
		with open(path, 'rb') as csvfile:
			read = csv.reader(csvfile, encoding='utf-8', delimiter=',', quotechar='"')
			for line in read:
				
				# store the date
				if line[0] == u'Date':
					self.date = line[1]
					logging.debug('Stored date: "%s"' % self.date)
				
				# skip comment lines
				elif re.match('^#', line[0]):
					logging.debug('Skipping comment line: %s' % line)
					continue
				
				# ncbi taxid, name, description, ncbi name, CITES appendix
				else:                                
					taxid = line[0]
					name  = line[1]
					desc  = line[2]
					canon = line[3]
					app   = line[4]
					self.taxa.append( Taxon(
						name=name,
						description=desc,
						appendix=app,
						ncbi={taxid:canon}
					) )
					logging.debug('Instantiated "%s" with {%s:%s}' % (name,taxid,canon))
	
	def from_dump(self,path):

		"""Reads a downloaded CITES database dump."""
		
		# open the file and read the .csv
		logging.info('Reading the CITES data dump.')
		header = {}
		with open(path, 'rb') as csvfile:
			read = csv.reader(csvfile, delimiter=',', quotechar='"', encoding='utf-8')
			for line in read:
				if not header:
					header = line
					continue
				else:
					record = {}
					for idx, val in enumerate(header):
						record[header[idx]] = line[idx]
					if record[u'CitesAccepted'] == u'true':
						app   = { u'I':1, u'II':2, u'III':3 }
						for i in record[u'CurrentListing'].split(u'/'):
							if i in app:
								taxon = Taxon(
									name=record[u'FullName'],
									description=record[u'AnnotationEnglish'],
									appendix=unicode(app[i])
								)
								self.taxa.append(taxon)
	
	def from_html(self,url='http://www.cites.org/eng/app/appendices.php'):
	
		"""Reads CITES appendices directly from web pages."""

		# open the url and read the .php webpage
		logging.info('Downloading CITES appendix webpage.') 
		CITES_url = urllib2.urlopen(url)
		html = CITES_url.read()
		
		# read the CITES web page as BeautifulSoup object hierarchy
		logging.debug('Parsing the CITES html page.')
		CITES_page = BeautifulSoup(html)        
		
		# parse through the footnotes and create
		# a dictionary for each one of the notes
		logging.debug('Parsing the CITES appendix footnotes.')
		CITES_notes = {}
		fntable = CITES_page.findAll( 'table', { 'border' : 2 } )
		rows = fntable[0].findAll('tr')
		for tr in rows:
			notes = tr.findAll('td')
			CITES_notes[self.clean_cell(notes[0])] = self.clean_cell(notes[1])
	
		# the time stamp
		self.date = self.clean_cell(CITES_page.b.find('strong'))
		
		# table rows with the c10 class as well as having 4 cells in them are name records
		# in the CITES appendices. The cell/column number is the appendix number.
		trs = CITES_page.findAll('tr', { 'class' : 'c10' } )
		for tr in trs:
			tds = tr.findAll('td')
			
			# fewer columns would mean this is a header row
			if len(tds) == 4:
				for i in range(1,4):
					text = self.clean_cell(tds[i])
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
						taxon = re.sub(r'\s+$','',taxon)
						logging.debug('CITES appendix %d taxon %s' % ( i, taxon ) )
						
						# collect footnote ID references by their a tags                        
						notes = {}
						refs = [ self.clean_cell(note) for note in tds[i].findAll('a') ]
						for ref in refs:
							if ref == '':
								continue
							notes[ref] = CITES_notes[ref]
						self.taxa.append( Taxon(
							name=taxon,
							description=self.clean_cell(tds[i]),
							appendix=i,
							footnotes=notes
						) )
	
	def to_csv(self,handle=BytesIO()):
		
		"""Returns the database as CSV text."""
		
		writer = csv.writer( handle, encoding='utf-8' )
		writer.writerow(( u'#Date of last update:' ))
		writer.writerow(( u'Date', unicode(self.date) ))
		writer.writerow(( u'#taxon id', u'CITES species', u'CITES description', u'taxon species', u'CITES appendix' ))
		for taxon in self.taxa:
			taxon.to_csv(handle)
		return handle;
