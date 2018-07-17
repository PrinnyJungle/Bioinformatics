#!/usr/bin/env python

"""
Assign islands to gene annotations
Priority list:[promoter, 5'UTR, 3'UTR, exons, introns]

strategy: 
From gene annotation, grab the relevant regions of top priority
Assign islands to regions. 
	resolve island assignment if one island is assigned to multiple genes?
	Find islands not assigned
Assign remaining islands to those in second priority

return {island:{"id":[value]; {"annotation":"Promoter"/"5UTR/..."}

"""


import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import time
from operator import itemgetter

try:
   import cPickle as pickle
except:
   import pickle

sys.path.append('/home/data/SICER1.1/SICER/lib')
sys.path.append('/home/data/SICER1.1/SICER/extra')
sys.path.append('/home/data/SICER1.1/SICER/extra/tools/RepElements')


sys.path.append('/home/wpeng/data/SICER1.1/SICER/lib')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra/tools/RepElements')

import UCSC_revised
import GenomeData
import SeparateByChrom
import Utility_extended
import BED_annotated

plus = re.compile("\+");
minus = re.compile("\-");	

def multi_annotate_islands(known_genes, islands, annotation_type_list):
	"""
	known_genes: UCSC Known_genes class
	islands: BED_annotated class object
		islands.bed_vals: {chrom:[(chrom, start, end, annotation)]}
	annotation_list: []
	
	region_dic: {chrom:[UCSC_lite]}
	
	Return:
	{chrom:{(start, end, annotation):{annotation_type:[ids]}}}
	"""
	chroms = islands.bed_vals.keys()
	# Initialize the construct
	multi_annotated_islands = {}
	for chrom in chroms:
		multi_annotated_islands[chrom] = {}
		island_list = islands.bed_vals[chrom] #[(chrom, start, end, annotation)]
		formulated_island_list = [(island[1], island[2], island[3]) for island in island_list]
		for island in formulated_island_list:
			multi_annotated_islands[chrom][island]={}
	
	for annotation_type in annotation_type_list:
		# Determine the region type
		if annotation_type == "Promoter":
			upstream = 1000
			downstream = 500
			region_dic = known_genes.getPromoters(upstream, downstream)
		elif annotation_type == "PromoterGenebody":
			upstream = 1000
			region_dic = known_genes.getPromotergenebodys(upstream)
		elif annotation_type == "GeneBody":
			downstream = 0
			region_dic = known_genes.getGenebodys(downstream)
		elif annotation_type == 'ExonicRegion':
			region_dic = known_genes.getExons()
		elif annotation_type == "IntronicRegion":
			region_dic = known_genes.getIntrons()
		elif annotation_type == "5UTR":
			upstream = 0
			downstream = 0
			region_dic = known_genes.get5UTRs(upstream, downstream)
		elif annotation_type == "3UTR":
			upstream = 0
			downstream = 0
			region_dic = known_genes.get3UTRs(upstream, downstream)
		elif annotation_type == "GeneEnd":
			upstream = 500
			downstream = 1000
			region_dic = known_genes.getGeneEnds(upstream, downstream)
		else:
			print "Region type not recognized"
			exit(1)
	
		#cycle through chrom
		for chrom in chroms:
			#print chrom
			# Get the islands
			island_list = islands.bed_vals[chrom] #[(chrom, start, end, annotation)]
			if is_tuplelist_sorted(island_list, 1) == 0:
				island_list.sort(key=itemgetter(1)) #sort according to start
			#[(start, end, annotation)]
			formulated_island_list = [(island[1], island[2], island[3]) for island in island_list]
			
			region_list = region_dic[chrom] #[UCSC_lite]
			#[(start, end, name)]
			fomulated_region_list = [ (region.start,region.end, region.name ) for region in region_list]
			
			#[((start, end, annotation), [(start, end, name)])]
			my_islands_annotated = Utility_extended.find_islands_overlapping_with_regions(formulated_island_list,fomulated_region_list)
			for item in my_islands_annotated: #((start, end, annotation), [(start, end, name)])
				my_island = item[0] #(start, end, annotation)
				# item[1] is [(start, end, name)]
				ids = [myitem[2] for myitem in item[1]]
				multi_annotated_islands[chrom][my_island][annotation_type] = ids
	return multi_annotated_islands

def prioritize_island_annotations(multi_annotated_islands, priority_list):
	"""
	multi_annotated_islands:{chrom:{(start, end, annotation):{annotation_type:[ids]}}}
	
	return: {chrom:{(start, end, annotation):{annotation_type:[ids]}}}
	
	need to code this part
	
	"""
	
def main(argv):
	parser = OptionParser()
	
	parser.add_option("-b", "--bedfile", action="store", type="string", dest="bedfile", metavar="<file>", help="island bed file")
	parser.add_option("-a", "--AnnotationFile", action="store", type="string", dest="known_genes", metavar="<file>", help="file with ucsc annotation")
	parser.add_option("-s", "--species", action="store", type="string", dest="species",help="species, mm8, hg18, etc", metavar="<str>")
	parser.add_option("-p", "--priority_list", action="store", type="string", dest="priority_list_file",help="annotation feature priority file", metavar="<file>")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 8:
		parser.print_help()
		sys.exit(1)
	
	if opt.species in GenomeData.species_chroms.keys():
		chroms = GenomeData.species_chroms[opt.species]
		chrom_lengths = GenomeData.species_chrom_lengths[opt.species]
	else:
		print "This species is not recognized, exiting";
		sys.exit(1);
	
	lib_name = (opt.bedfile).split('/')[-1] # remove directory
	suffix = lib_name.split('.')[-1] # txt
	lib_name = lib_name.split('.')[0] 
	
	#load islands in bedfile
	#islands.bed_vals: {chrom:[(chrom, start, end, annotation)]}
	if Utility_extended.fileExists(opt.bedfile):
		islands = BED_revised.BED_annotated(opt.species, opt.bedfile, "BED3", -1)	
	
	#Read Priority list
	#should be a subset of ['Promoter', 'GeneBody', 'PromoterGenebody', 'ExonicRegion', "IntronicRegion", "5UTR", "3UTR", "GeneEnd"]
	priority_list = []
	inf = open(opt.priority_list_file, "r")
	for line in inf:
		line = line.strip()
		sline = line.split()
		priority_list.append(sline[0])
	inf.close()	
	
	#Load Annotation:
	known_genes = UCSC_revised.KnownGenes(opt.known_genes)
	
	

	
	prioritize_islands()
	
	
	
	
	
	
	
if __name__ == "__main__":
	main(sys.argv)