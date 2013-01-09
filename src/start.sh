#!/bin/sh
#this file starts the blast -barcode pipeline (scripts: blast.py , trim.py , quality.py , output.py , cites_check).
#author: Alex Hoogkamer
#python ~/workspace/barcode-blast-pipeline/bin/Trim.py ~/workspace/barcode-blast-pipeline/data/test/s_2_1_sequence 46 0.05 | 
python ~/workspace/barcode-blast-pipeline/bin/blast.py ~/workspace/barcode-blast-pipeline/data/test/my_blast.xml blastn nt ~/workspace/barcode-blast-pipeline/src/IonXpress | python ~/workspace/barcode-blast-pipeline/bin/Quality-control.py 4 97 95 | python ~/workspace/barcode-blast-pipeline/bin/cites_check.py '-l ~/workspace/barcode-blast-pipeline/src/appendices.php' #| python ~/workspace/barcode-blast-pipeline/bin/Output.py ~/workspace/barcode-blast-pipeline/data/test/my_blast.xml 5
echo "done"
