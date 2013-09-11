#!/usr/bin/env python

# Small python wrapper that passes the xml commands to the HTS-barcode-checker script
# This requires the HTS-barcode-checker script to be present in the $PATH variable

# import the used modules
import sys, os
from subprocess import call

# set the directory for a new CITES database file if the user selected the
# "no local copy" option
if '-new' in sys.argv:
	start = sys.argv.index('-new')
	sys.argv.append('--CITES_db')
	name = "%s_%s_%s_%s_%s" % ('primary', sys.argv[start+1], 'CITES-db.csv', 'visible', 'txt')#, sys.argv[start+3])
	name = os.path.join(sys.argv[start+2], name)
	sys.argv.append(name)
	del sys.argv[start:(start+3)]

# call the HTS-barcode-checker script with the parameters and commands from\
# the HTS-barcode-checker.xml galaxy file.
path = call(['HTS-barcode-checker'] + sys.argv[1:])
