#!/usr/bin/env python
"""
This is a driver module to find the subset whose ids are given in a separate file. Weiqun Peng
"""

import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
from operator import itemgetter

sys.path.append('/home/data/SICER1.1/SICER/lib')
sys.path.append('/home/data/SICER1.1/SICER/extra')
import gene_set_manipulation

def main(argv):
	parser = OptionParser()
	parser.add_option("-a", "--genefile1", action="store", type="string", dest="genefile1", metavar="<file>", help="gene file 1, to be subtracted from")
	parser.add_option("-b", "--genefile2", action="store", type="string", dest="genefile2", metavar="<file>", help="gene file 2, to be subtracted")
	parser.add_option("-c", "--column1", action="store", type="int", dest="c1", metavar="<int>", help="the cloumn index of the gene id for gene file 1, 0 based")
	parser.add_option("-d", "--column2", action="store", type="int", dest="c2", metavar="<int>", help="the cloumn index of the gene id for gene file 2, 0 based")
	parser.add_option("-o", "--outputfile", action="store", type="string", dest="outfile", metavar="<file>", help="outputfile")
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 10:
		parser.print_help()
		sys.exit(1)
	
	list1 = gene_set_manipulation.get_gene_list(opt.genefile1, opt.c1)
	list2 = gene_set_manipulation.get_gene_list(opt.genefile2, opt.c2)
	
	IDs_to_be_retained = list( set(list1) & set(list2) )
	
	print opt.genefile1,": ", len(list1)
	print opt.genefile2,": ", len(list2)
	print "Retained: ", len(IDs_to_be_retained)
	gene_set_manipulation.output_subset_in_file (opt.genefile1, opt.c1, IDs_to_be_retained, opt.outfile)
	
if __name__ == "__main__":
	main(sys.argv)