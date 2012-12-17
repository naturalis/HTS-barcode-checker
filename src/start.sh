#!/bin/sh
#this file starts the blast -barcode pipeline (scripts: blast.py , trim.py , quality.py , output.py).
#author: Alex Hoogkamer
python ~/workspace/barcode-blast-pipeline/bin/Trim/Trim.py ~/workspace/barcode-blast-pipeline/data/test/s_2_1_sequence 46 0.05 | python ~/workspace/barcode-blast-pipeline/bin/BLAST/script1.py
python ~/workspace/barcode-blast-pipeline/bin/Quality/Quality-control.py ~/workspace/barcode-blast-pipeline/src/my_blast.xml | python ~/workspace/barcode-blast-pipeline/bin/Output/Output.py ~/workspace/barcode-blast-pipeline/src/my_blast.xml 5
echo "done"
