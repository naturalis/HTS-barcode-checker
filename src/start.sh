#!/bin/sh
#this file starts the blast -barcode pipeline (scripts: blast.py , trim.py , quality.py , output.py).
#author: Alex Hoogkamer
python ~/workspace/barcode-blast-pipeline/bin/Trim.py ~/workspace/barcode-blast-pipeline/data/test/s_2_1_sequence 46 0.05 | python ~/workspace/barcode-blast-pipeline/bin/blast.py ~/workspace/barcode-blast-pipeline/data/test/my_blast.xml blastn nt | python ~/workspace/barcode-blast-pipeline/bin/Quality-control.py 0.04 97 95 | python ~/workspace/barcode-blast-pipeline/bin/Output.py ~/workspace/barcode-blast-pipeline/data/test/my_blast.xml 5
echo "done"
