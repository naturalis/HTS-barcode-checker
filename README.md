barcode-blast-pipeline
======================

Pipeline for BLAST analysis of IonTorrent DNA barcoding data.

requirements:
Linux

dependecies:
python-biopython (RPM)


this pipeline takes fasQ input files and converts them to fasta format to be used in our blast section of the script.
the fasta file will then be blasted (blastn) and results are passed back as a XMl file.
the XML file is then used to perform a quality control(parameters will be entered by the user) and displayed back to the user's terminal
