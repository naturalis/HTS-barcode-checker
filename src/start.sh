#!/bin/sh
#deze file start de pipelijn.
#author: Alex Hoogkamer
cd ..
python bin/Trim/Trim.py
python bin/BLAST/script1.py
python bin/Quality/Quality-control.py
python bin/Output/Output.py
echo "done"
