#!/usr/bin/python2.7
'''
created on 10 jan. 2013
Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this file starts the barcode-blast-pipeline (scripts: blast.py , trim.py , Quality-control.py , output.py , cites_check).

dependencies:
Bio python
Unix OS
'''
#here argparse is imported for command line arguments, logging for displaying information for the user and os to start the other scripts
import logging, os, argparse

#the logging level is set to INFO so useful information can be presented to the user
logging.basicConfig(level = logging.INFO)

args = argparse.ArgumentParser(description = 'Pipeline to identify dna from samples and check if they are present on the cites list, the pipeline takes a file with fastq reads or a file with fasta reads')

#these are the command line arguments for the pipeline
args.add_argument('-i', '--input_file', type = str, help = 'Enter the path to the input file, the input file needs to be in fastq format for trimming or in fasta format without trimming', nargs='+') 
args.add_argument('-o','--output_file', type = str, help = 'Enter the path to the output file', nargs='+')
args.add_argument('-db','--database', type = str, help = 'Enter which database to be used with BLAST', default = 'nt')
args.add_argument('-ba', '--blast_algorithm', type = str, help = 'Enter which database to be used with BLAST', default = 'blastn')
args.add_argument('-me', '--min_evalue', type = float, help = 'Enter the minimal E-value for BLAST results', default = 0.04)
args.add_argument('-mc', '--min_coverage', type = int, help = 'Enter the minimal coverage for BLAST results', default = 95 )
args.add_argument('-mi', '--min_identity', type = int, help = 'Enter the minimal identity for BLAST results', default = 97)
args.add_argument('-ps', '--path_scripts', type = str, help = 'Enter the path of the scripts', nargs='+')
args.add_argument('-t', '--trimming', action="store_true", help = 'Enter if the input file will be trimmed')
args.add_argument('-tp', '--phred_thresshold', type = int, help = 'Enter the the phred score cutoff for the trimming tool', default = 46)

#here the arguments are added to the program
args = args.parse_args()

#print(args)
path = args.path_scripts[0]
path = path.strip('\r')
print(path)

#if trimming is triggerd the script trimming is run first, otherwise it is not run
if args.trimming:
    logging.info('running pipeline')
    os.system('python {path}/Trim.py {input_file} {path_output} {phred_score_thresshold} | python {path}/blast.py {path}/blast.xml {algorithm} {database} {path_output}/trimmed | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/cites_check.py'.format(path = path, phred_score_thresshold = args.phred_thresshold, input_file = args.input_file, path_output = args.output_file, algorithm = args.blast_algorithm, database = args.database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity))
    logging.info('finished pipeline')
else:
    logging.info('starting pipeline')
    os.system('python {path}/blast.py {path_output}/blast.xml {algorithm} {database} {input_file} | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/cites_check.py'.format(path = path, input_file = args.input_file[0], path_output = args.output_file[0], algorithm = args.blast_algorithm, database = args.database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity))
    logging.info('finished pipeline')