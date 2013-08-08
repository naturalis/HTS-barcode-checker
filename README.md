HTS-barcode-checker
===================

The correct taxonomic identification of internationally traded biological materials is 
crucial for the effective enforcement of the Convention on International Trade in 
Endangered Species of Wild Fauna and Flora (CITES). This project provides a pipeline that
automates the putative taxonomic identification of DNA barcodes (e.g. as generated from
confiscated materials) by chaining together the steps of DNA sequence similarity searching 
in public databases and taxonomic name reconciliation of the names associated with 
returned, similar sequences and the names listed in the CITES "appendices" (which itemize 
species and higher taxa in which international trade is restricted).

Disclaimer
----------

Although the authors of this pipeline have taken care to consider exceptions such as 
incorrectly annotated sequence records in public databases, taxonomic synonyms and 
ambiguities in the CITES appendices themselves, the user is advised that the results of 
this pipeline can in no way be construed as conclusive evidence for either positive or
negative taxonomic identification of the contents of biological materials. To emphasize
this point, we reproduce the disclaimer of the license under which this pipeline is 
released verbatim, below:

**THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR 
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.**

General usage
-------------

The basic command to run the pipeline is:

`CITES_Check.py --input_file <in.fa> --output_file <out.csv> --CITES_db <db.csv>`

This command will run BLAST searches of the provided input FASTA file(s) against the NCBI
nucleotide database (by default), then cross-reference the returned taxon IDs with local
databases of taxon IDs that were obtained by taxonomic name reconciliation of the names 
listed in CITES appendices with the NCBI taxonomy. Any putative matches are recorded in 
the output file, a CSV spreadsheet, which needs to be evaluated further by the user.

Important options
-----------------

* **Blacklisted GenBank accessions** Some GenBank accessions are known to have incorrect 
taxon IDs, which can cause both Type I and Type II errors in this pipeline. To avoid such 
known, problematic, GenBank accessions, the command line argument `--blacklist <list.csv>` 
can be provided. An example of what such a file should look like is provided in the data 
folder as _Blacklist.csv_.

* **Synonyms** Some nodes in the NCBI taxonomy are considered to be synonyms of other such 
nodes. This, too, has the potential to cause Type I and Type II errors. For known nodes 
where this is the case, (an) additional CSV spreadsheet(s) can be provided that identifies 
NCBI synonyms that are also CITES-listed. An example of such an additional file is 
provided in the data folder as _Reconciled\_names\_db.csv_.

* **Local database updates** Periodically, CITES releases new appendices with new lists of 
names. In order to stay up to date, this pipeline checks whether such new update are 
available and downloads and processes the new data if this is the case. This behavior can 
be influenced by either forcing the download (with `--force_update`) or omitting it (with 
`--avoid_update`) regardless.

* **Verbosity** The script keeps a log of the different processes in the script. The log 
file is named similar to the file specified with the `--output_file` parameter, but with 
the .log extension. With the `--logging parameter` the amount of information written to 
the log file can be altered. The parameter can be set to: WARNING (default), INFO or DEBUG. 
WARNING logs only the  messages generated when something is amiss with either blasting 
sequences or updating the CITES database. This verbosity level is the default. INFO logs 
the basic steps of the pipeline and any recoverable issues that might occur (similar to 
WARNING). DEBUG logs everything the pipeline does and is of limited use to the end-user.


Full command information
------------------------

Command line arguments:

	CITES_Check.py [-h] [-i fasta file] [-o output file] [-ba algorithm]
	[-bd database] [-hs HS] [-mb] [-mi MI] [-mc MC] [-me ME]
	[-bl blacklist file] [-cd CITES database file [CITES database file ...]]
	[-fd] [-ad] [-l log level]

All command line arguments and options can be provided in short of long form, as listed
below:

	-h, --help            
		show help message and exit
  
	-i <fasta file>, --input_file <fasta file>
		input data in FASTA format
		
	-o <output file>, --output_file <output file>
		results file in CSV format

	-ba <algorithm>, --BLAST_algorithm <algorithm>
		BLAST algorithm to use (default=blastn)
		
	-bd <database>, --BLAST_database <database>
		BLAST database to use (default=nt)

	-mb, --megablast      
		use megablast, can only be used in combination with blastn
		
	-hs <size>, --hitlist_size <size>
		number of results BLAST wil return (default=10)
		
	-mi <identity>, --min_identity <identity>
		lowest percentage identity for BLAST results to consider (default=97)
		
	-mc <coverage>, --min_coverage <coverage>
		minimal coverage for BLAST results in number of bases (default=100)
		
	-me <e-value>, --max_evalue  <e-value>
		threshold E-value for BLAST results (default=0.05)
		
	-bl <blacklist file>, --blacklist <blacklist file>
		CSV file containing blacklisted genbank accession numbers
						
	-cd <db file> [<db file> ...], --CITES_db <db file> [<db file> ...]
		one or more database (CSV) files with CITES-listed taxon identifiers
						
	-fd, --force_download
		force update of the local CITES database

	-ad, --avoid_download
		avoid updating the local CITES database

	-l <verbosity>, --logging <verbosity>
		set log level to: debug, info, warning (default) or critical. log written to
		-output_file + '.log'

Dependencies
------------
* python2.7 or 3
* bio-python
* beautiful-soup
* requests

License
-------
* BSD-3

