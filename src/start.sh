#!/bin/sh
#this file starts the blast -barcode pipeline (scripts: blast.py , trim.py , quality.py , output.py , cites_check).
#author: Alex Hoogkamer
python start.py -i ~/workspace/barcode-blast-pipeline/data/gen -o ~/workspace/barcode-blast-pipeline/data/ -ps ~/workspace/barcode-blast-pipeline/bin
