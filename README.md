CITES-checker
=============

Pipeline for crossreferencing DNA barcoding data with CITES appendices

Dependencies
------------
* python2.7 or 3
* bio-python
* beautiful-soup
* requests

License
-------
* BSD-3

Usage
-----
$ python CITES_Check.py [-h] [-i fasta file] [-o output file] [-a algorithm]
                      [-d database] [-s S] [-m] [-mi MI] [-mc MC] [-me ME]
                      [-b blacklist file] [-c CITES database file] [-fu] [-au]

optional arguments:
  -h, --help            show this help message and exit
  -i fasta file, --input_file fasta file
                        enter the fasta file
  -o output file, --output_file output file
                        enter the output file
  -a algorithm, --BLAST_algorithm algorithm
                        Enter the algorithm BLAST wil use (default=blastn)
  -d database, --BLAST_database database
                        Enter the database BLAST wil use (default=nt)
  -s S, --hitlist_size S
                        Enter the size of the hitlist BLAST wil return
                        (default=1)
  -m, --megablast       Use megablast, can only be used in combination with
                        blastn
  -mi MI, --min_identity MI
                        Enter the minimal identity for BLAST results
  -mc MC, --min_coverage MC
                        Enter the minimal coverage for BLAST results
  -me ME, --max_evalue ME
                        Enter the minimal E-value for BLAST results
  -b blacklist file, --blacklist blacklist file
                        File containing the blacklisted genbank id's
  -c CITES database file, --CITES_db CITES database file
                        Path to the local copy of the CITES database
  -fu, --force_update   Force the update of the local CITES database
  -au, --avoid_update   Avoid updating the local CITES database    