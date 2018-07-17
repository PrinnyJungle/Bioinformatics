#!/usr/bin/env python
import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import csv

"""
This module is used to make a UCSC format gene file that can be read by UCSC.py and used for drawing profiles etc
The input file can be any format gene file given gene name, chromosome, strand, start position and end position in differnt columns.
The input parameters are the 5 colum number for name, chromosome, strand, txStart, txEnd.
The output is the UCSC readable gene file, where other five colums not used are all set zero.

The annotation file should have the following format:
id	0
chromosome	1
strand	2
txStart	3
txEnd	4

"""

def get_formated_genes(input_file_name, annotation_dic, output_file):
	"""
	"""
	infile = open(input_file_name,'r')
	outfile = open(output_file, 'w')
	for line in infile:
		if not re.match("#", line):
			line = line.strip()
			sline = line.split()
			if len(sline) >= max(annotation_dic.values()):
				outlist = [sline[annotation_dic["id"]], sline[annotation_dic["chrom"]], sline[annotation_dic["strand"]], sline[annotation_dic["txStart"]], sline[annotation_dic["txEnd"]], 0, 0, 0, 0, 0]
				outline = "\t".join([str(i) for i in outlist]) + "\n"
				outfile.write(outline)
	infile.close()
	outfile.close()

def get_annotation_table(annotation_file_name):
	"""
	annotation_dic {column_name: column_index(o based)}
	"""
	annotation_dic = {}
	with open(annotation_file_name, 'rb') as f:
		reader = csv.reader(f, delimiter='\t')
		for row in reader:
			annotation_dic[row[0]] = int(row[1])
	return annotation_dic
		
	
def main(argv):
	parser = OptionParser()
	parser.add_option("-i", "--inputfile", action="store", type="string", dest="input_file_name", metavar="<file>", help="original gene file to be formatted")
	parser.add_option("-a", "--ColumnCorrespondencefile", action="store", type="string", dest="annotation_file_name", metavar="<file>", help="file that contains annotation info for columns")
	parser.add_option("-o", "--outputfile", action="store", type="string", dest="output_file", metavar="<file>", help="output UCSC format file")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 6:
        	parser.print_help()
        	sys.exit(1)
	
	annotation_dic = get_annotation_table(opt.annotation_file_name)
	get_formated_genes(opt.input_file_name, annotation_dic, opt.output_file)

if __name__ == "__main__":
	main(sys.argv)
