#!/usr/bin/env python
# Author :  Weiqun Peng

"""
Takes a raw repetive element data file and 
1) splits it by the repetitive element name : repClass_repFamily_repName.txt
2) generate the RE tree and output it in pickle and txt
3) generate and output repClass_repFamily_repName.pkl, which has the repClass_repFamily_repName as a RepElements class instance

re_tree: {repClass:{repFamily:[repName]}}

"""

import re, os, shutil, time, sys, operator
from math import *
from string import *
from optparse import OptionParser
import copy
from operator import itemgetter
try:
   import cPickle as pickle
except:
   import pickle

sys.path.append('/home/wpeng/data/SICER1.1/SICER/lib')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra/tools/RepElements')
sys.path.append('/home/data/SICER1.1/SICER/lib')
sys.path.append('/home/data/SICER1.1/SICER/extra')
sys.path.append('/home/data/SICER1.1/SICER/extra/tools/RepElements')

import GenomeData 
import RepElements


plus = re.compile('\+');
minus = re.compile('\-');

RepElementsError = "Error in RepElement class";

def main(argv):

	"""Lines to parse command line arguments from the file repUCSC.sh"""
	parser = OptionParser()
	parser.add_option("-i", "--file", action="store", type="string", dest="datafile", metavar="<file>",
					help="text file in raw format")    
	parser.add_option("-s", "--species", action="store", type="string", dest="species",help="species, mm8, hg18, etc", metavar="<str>")
	
	(opt, args) = parser.parse_args(argv)
	
	if len(argv) < 4:
		parser.print_help()
		sys.exit(1)
	
	if opt.species in GenomeData.species_chroms.keys():
		chroms = GenomeData.species_chroms[opt.species];
	else:
		print "This species is not recognized, exiting";
		sys.exit(1);

	mytree = {}
	infile = open(opt.datafile);
	for line in infile:
		if not re.match("#", line):
			myline = line.strip();   #"""Strip white space off line""" 
			sline = myline.split();  #"""Split line into individual strings (fields)"""
			""" Check to make sure this chromosome is declared in the dictionary."""
			repName = sline[10]
			repClass = sline[11]
			repFamily = sline[12]
			name = "_".join([repClass, repFamily, repName]) + ".txt"
			outf = open(name, 'a')
			outf.write(line)
			outf.close()
			
			if repClass not in mytree.keys():
				mytree[repClass] = {}
				mytree[repClass][repFamily] = []
				mytree[repClass][repFamily].append(repName)
			else:
				if repFamily not in mytree[repClass]:
					mytree[repClass][repFamily] = []
					mytree[repClass][repFamily].append(repName)
				else:
					if repName not in mytree[repClass][repFamily]:
						mytree[repClass][repFamily].append(repName)
	infile.close()
	
	output = open("mm9_re_tree.pkl", 'wb')
	pickle.dump(mytree, output)
	output.close()	
	
	# output the pkl file store the rep elements organized in a dictionary: {id: rep_element class instance}
	for reClass in mytree.keys():
		for reFamily in mytree[reClass].keys():
			for reName in mytree[reClass][reFamily]:
				re_file_name = "_".join([reClass, reFamily, reName]) + ".txt"
				known_repelements = RepElements.KnownRepElements.initiate_from_file(chroms, re_file_name)
				re_file_name = "_".join([reClass, reFamily, reName]) + ".pkl"
				known_repelements.output_pickle(re_file_name)
	

if __name__ == "__main__":
	main(sys.argv)
