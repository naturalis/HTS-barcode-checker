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
# here argparse is imported for command line arguments, logging for displaying information for the user and os to start the other scripts
import logging, os, argparse

# the logging level is set to INFO so useful information can be presented to the user
logging.basicConfig(level = logging.INFO)

args = argparse.ArgumentParser(description = 'Pipeline to identify dna from samples and check if they are present on the cites list, the pipeline takes a file with fastq reads or a file with fasta reads')

# these are the command line arguments for the pipeline
args.add_argument('-i', '--input_file', type = str, help = 'Enter the path to the input file, the input file needs to be in fastq format for trimming or in fasta format without trimming', nargs='+') 
args.add_argument('-o','--output_file', type = str, help = 'Enter the path to the output file', nargs='+')
args.add_argument('-db','--blast_database', type = str, help = 'Enter which database to be used with BLAST', default = 'nt')
args.add_argument('-ba', '--blast_algorithm', type = str, help = 'Enter which database to be used with BLAST', default = 'blastn')
args.add_argument('-me', '--min_evalue', type = float, help = 'Enter the minimal E-value for BLAST results', default = 0.04)
args.add_argument('-mc', '--min_coverage', type = int, help = 'Enter the minimal coverage for BLAST results', default = 95 )
args.add_argument('-mi', '--min_identity', type = int, help = 'Enter the minimal identity for BLAST results', default = 97)
args.add_argument('-ps', '--path_scripts', type = str, help = 'Enter the path of the scripts', nargs='+')
args.add_argument('-t', '--fastq_trimming', action="store_true", help = 'Enter if the input file will be trimmed')
args.add_argument('-tp', '--phred_thresshold', type = int, help = 'Enter the the phred score cutoff for the trimming tool', default = 46)
args.add_argument('-bh', '--hitlist_size', type = int, help = 'enter the size of the BLAST hit list')
args.add_argument('-m', '--megablast', action='store_true', help = 'Switch to use megablast instead of blastn')
args.add_argument('-g', '--gapcost', type = str, help = 'Enter the gap cost for blast search, it is entered as "x y"')
args.add_argument('-nr', '--nucleotide_reward', type = int, help = 'Enter the match score for blast search')
args.add_argument('-np', '--nucleotide_penalty', type = str, help = 'Enter the mismatch score for blast search')
args.add_argument('-w', '--wordsize', type = int, help = 'Enter the wordsize for blast search', default = 11)
# here the arguments are added to the program
args = args.parse_args()

# the path is assigned from the first entry in the args.path_script
path = args.path_scripts[0]
path = path.strip('\r')

# if trimming is flagged the trimming script is run first, otherwise it is not run
if args.fastq_trimming:
    logging.info('running pipeline')
    # if megablast is flagged megablast is used in the blast script
    if args.megablast:
        os.system('python {path}/Trim.py {input_file} {path_output} {phred_score_thresshold} | python {path}/blast.py -m -o {path}/blast.xml -a {algorithm} -d {database} -i {path_output} -s {hitlist_size} -p -w "{word}" -np "{penalty}" -nr "{reward}" -g "{gap}" | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/CITES_check.py | python {path}/Output.py {path_output} {path}'.format(path = path, phred_score_thresshold = args.phred_thresshold, input_file = args.input_file, path_output = args.output_file, algorithm = args.blast_algorithm, database = args.blast_database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity, hitlist_size = args.hitlist_size, word = args.wordsize, penalty = args.nucleotide_penalty, reward = args.nucleotide_reward, gap = args.gapcost))
    else:
        os.system('python {path}/Trim.py {input_file} {path_output} {phred_score_thresshold} | python {path}/blast.py -o {path}/blast.xml -a {algorithm} -d {database} -i {path_output} -s {hitlist_size} -p -w "{word}" -np "{penalty}" -nr "{reward}" -g "{gap}" | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/CITES_check.py | python {path}/Output.py {path_output} {path}'.format(path = path, phred_score_thresshold = args.phred_thresshold, input_file = args.input_file, path_output = args.output_file, algorithm = args.blast_algorithm, database = args.blast_database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity, hitlist_size = args.hitlist_size, word = args.wordsize, penalty = args.nucleotide_penalty, reward = args.nucleotide_reward, gap = args.gapcost))
    logging.info('finished pipeline')
else:
    logging.info('starting pipeline')
    # if megablast is flagged megablast is used in the blast script
    if args.megablast:
        os.system('python {path}/blast.py -o {path_output} -a {algorithm} -d {database} -i {input_file} -w "{word}" -np "{penalty}" -nr "{reward}" -g "{gap}" -m | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/CITES_check.py | python {path}/Output.py {path_output} {path}'.format(path = path, input_file = args.input_file[0], path_output = args.output_file[0], algorithm = args.blast_algorithm, database = args.blast_database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity, hitlist_size = args.hitlist_size, word = args.wordsize, penalty = args.nucleotide_penalty, reward = args.nucleotide_reward, gap = args.gapcost))
    else:
        os.system('python {path}/blast.py -o {path_output} -a {algorithm} -d {database} -i {input_file} -w "{word}" -np "{penalty}" -nr "{reward}" -g "{gap}" | python {path}/Quality-control.py {evalue} {identity} {coverage} | python {path}/CITES_check.py | python {path}/Output.py {path_output} {path}'.format(path = path, input_file = args.input_file[0], path_output = args.output_file[0], algorithm = args.blast_algorithm, database = args.blast_database, evalue = args.min_evalue, coverage = args.min_coverage, identity = args.min_identity, hitlist_size = args.hitlist_size, word = args.wordsize, penalty = args.nucleotide_penalty, reward = args.nucleotide_reward, gap = args.gapcost))
    logging.info('finished pipeline')