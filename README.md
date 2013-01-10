CITES-checker
======================

Pipeline for BLAST analysis of IonTorrent DNA barcoding data.

requirements:
Linux

dependencies:
python-biopython (RPM)


This pipeline takes FastQ input files and converts them to FASTA 
format to be used in our BLAST section of the script. The FASTA file 
will then be blasted (blastn) and results are passed back as an XML 
file. The XML file is then used to perform a quality control 
(parameters will be entered by the user) and displayed back to the 
user's terminal. The results will then be checked on the CITES list
(available at http://www.cites.org/eng/app/appendices.php) to see if 
there are any illegal "hits". The results are displayed to the user 
on the command line
