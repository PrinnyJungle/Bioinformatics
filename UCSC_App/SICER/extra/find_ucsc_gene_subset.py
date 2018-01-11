#!/usr/bin/env python
import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator

import gene_set_manipulation

plus = re.compile("\+");
minus = re.compile("\-");


def main(argv):
	parser = OptionParser()
	
	parser.add_option("-i", "--genelistfile", action="store", type="string", dest="gene_list", metavar="<file>", help="file for list of genes")
	parser.add_option("-r", "--UCSCfile", action="store", type="string", dest="ucsc", metavar="<file>", help="UCSC file for all genes")
	parser.add_option("-o", "--outfile", action="store", type="string", dest="out_file", metavar="<file>", help="output file name for ucsc file of selected genes")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 6:
        	parser.print_help()
        	sys.exit(1)
	genelist = gene_set_manipulation.get_gene_list(opt.gene_list, 0);
	gene_set_manipulation.output_UCSCsubset_in_file (opt.ucsc, genelist, opt.out_file)
	
	
if __name__ == "__main__":
	main(sys.argv)