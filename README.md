CITES-checker
=============

Pipeline for cross referencing DNA barcoding data with CITES appendices

Dependencies
------------
* python2.7 or 3
* bio-python
* beautiful-soup
* requests

License
-------
* BSD-3

General usage
-------------

The basic command for the CITES checker is:
    CITES_Check.py -i fasta_file(s) -o output_file -cd CITES_database_file
This command will check if the CITES database file (copy of the database is located in the data folder) is up-to-date,
it will download a new copy if it is outdated. It will continue by blasting the fasta sequences against the NCBI nucleotide
database (default) and check if the blast results contain CITES listed species. It will write the output to the
user specified output file in a comma separated format.

In order to avoid certain genbank accessions a user specified blacklist can be provided with:
    CITES_Check.py -i fasta_file(s) -o output_file -cd CITES_database_file -bl blacklist_file
An example blacklist file is present in the data folder

To account for synonyms a local database of reconciled CITES names can be provided with the -cd command:
    CITES_Check.py -i fasta_file(s) -o output_file -cd CITES_database_file reconciled_names_file
Any number of additional custom CITES files may be provided, though if the default CITES dataset is absent a new
copy will be downloaded.

To force or avoid updating the local database, add the --force_update or --avoid_update to the command

Full Command information
-----

Command line arguments:

    CITES_Check.py [-h] [-i fasta file] [-o output file] [-ba algorithm]
    [-bd database] [-hs HS] [-mb] [-mi MI] [-mc MC] [-me ME]
    [-bl blacklist file] [-cd CITES database file] [-fd] [-ad]

Help options:

    Identify a set of sequences and check if there are CITES species present
    
    optional arguments:
      -h, --help            show this help message and exit
      -i fasta file, --input_file fasta file
                            enter the fasta file
      -o output file, --output_file output file
                            enter the output file
      -ba algorithm, --BLAST_algorithm algorithm
                            Enter the algorithm BLAST wil use (default=blastn)
      -bd database, --BLAST_database database
                            Enter the database BLAST wil use (default=nt)
      -hs HS, --hitlist_size HS
                            Enter the size of the hitlist BLAST wil return
                            (default=1)
      -mb, --megablast      Use megablast, can only be used in combination with
                            blastn
      -mi MI, --min_identity MI
                            Enter the minimal identity for BLAST results
      -mc MC, --min_coverage MC
                            Enter the minimal coverage for BLAST results
      -me ME, --max_evalue ME
                            Enter the minimal E-value for BLAST results
      -bl blacklist file, --blacklist blacklist file
                            File containing the blacklisted genbank id's
      -cd CITES database file, --CITES_db CITES database file
                            Path to the local copy of the CITES database
      -fd, --force_download
                            Force the update of the local CITES database
      -ad, --avoid_download
                            Avoid updating the local CITES database
      -v, --verbose         Verbose: The scripts prints detailed information on
                            what it is doing for logging

