#!/usr/bin/env python
# Build a data structure: gene_id: [list of PA peaks]
# Calculate the characteristics for each gene_id

import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import bisect
from operator import itemgetter
try:
   import cPickle as pickle
except:
   import pickle

import time


sys.path.append('/home/data/SICER1.1/SICER/lib')
sys.path.append('/home/data/SICER1.1/SICER/extra')
sys.path.append('/home/data/hg19/Annotation')
sys.path.append('/home/data/SICER1.1/SICER/extra/tools/RNASeq')

import Utility_extended
import GenomeData 
import SeparateByChrom
import UCSC_revised
import associate_tags_with_regions
import get_total_tag_counts

import Entrez
#import Calculate3UTRUsageIndexFromCuratedGenes
from Entrez import KnownEntrezGenes
from Entrez import EntrezGene

plus = re.compile("\+");
minus = re.compile("\-");
comment = re.compile("#|track")

def Calculate3UTRUsage(entrez_genes, bedfile, column_index, chroms, fragment_size, downstream_extension, outfile):
	"""
	entrez genes are made sure to be on one strand, 
	the bed file are reads for that strand
	
	entrez_genes is a KnownEntrezGenes class object
	The raw read file needs to conform to bed format
	
	column_index: column in bed file for sorting
	
	"""
	# Separate reads by chrom 
	rawreadslibName1 = (bedfile).split('/')[-1]
	rawreadssuffix1 = rawreadslibName1.split('.')[-1] 
	rawreadslibName1 = rawreadslibName1.split('.')[0]
	rawreadsextension1 = "-" + rawreadslibName1 +'.' + rawreadssuffix1 + "1"
	if Utility_extended.fileExists(bedfile):
		if Utility_extended.chrom_files_exist(chroms, rawreadsextension1) != 1:
			# Separate by chrom and sort by start
			print chroms, rawreadsextension1, " files do not exist, separate by chroms and sort each file according to the second column. "
			Utility_extended.separate_by_chrom_sort(chroms, bedfile, rawreadsextension1, [column_index])
	else:
		print bedfile, " is not found";
		sys.exit(1)
	
	# Here the output is 'a'
	outf = open(outfile, 'a')	
	for chrom in chroms: 
		if chrom in entrez_genes.chroms:
			# a KnownEntrezGenes object
			entrez_genes_by_chrom =  Entrez.KnownEntrezGenes([chrom], entrez_genes.subset_by_chrom(chrom))
			# this_chrom_length = chrom_lengths[chrom]
			# Get the read locations
			if Utility_extended.fileExists(chrom + rawreadsextension1):
				f = open(chrom + rawreadsextension1, 'r')
				tag_positions = []
				for line in f:
					line = line.strip();
					sline = line.split();
					tag_positions.append(associate_tags_with_regions.tag_position(sline, fragment_size))
				if not Utility_extended.is_list_sorted(tag_positions):
					tag_positions.sort()	
				f.close()
				
				for entrez_id in entrez_genes_by_chrom.entrez_ids:
					gene = entrez_genes_by_chrom.entrez_genes[entrez_id] # an EntrezGene class object
					three_UTRs = gene.get_3UTRs(downstream_extension)
					print three_UTRs
					union = Utility_extended.union(three_UTRs) # Find the union of 3UTRs [(start, end)], returns a [(start,end)]
					if len(union) > 1:
						print "There are disjoint 3UTRs in %s" %(str(entrez_id))
					else:
						# returns [((start, end), [tag_positions])], [tag_positions] = return[0][1]
						inside_reads = (Utility_extended.associate_simple_tags_with_regions(tag_positions, union))[0][1] 
						total_read_count = len(inside_reads)
						RUD = CUTR_vs_AUTR(three_UTRs, inside_reads, gene.strand)
					
						## For the set of genes, use the distal 3UTR at the designated representative 3UTR
						#myindex = Calculate3UTRUsageIndexFromCuratedGenes.find_distal_3UTR(genes)
						#gene = genes[myindex]
						#results = ThreeUTRCharacteristics(gene, inside_reads)
						
						gene_symbol = []
						for mytranscript in gene.transcripts:
							if mytranscript.additional_annotations[0] not in gene_symbol:
								gene_symbol.append(mytranscript.additional_annotations[0])
								
						union_length = union[0][1]-union[0][0]+1
						outline = str(entrez_id) + "\t" + str(union_length) + "\t" + str(RUD) + "\t" + str(total_read_count) + "\t" + ','.join([transcript.name for transcript in gene.transcripts]) + "\t" + ','.join(gene_symbol) + "\n"
					
					outf.write(outline)
	outf.close()		
	#SeparateByChrom.cleanup(chroms, rawreadsextension1)

def CUTR_vs_AUTR(three_UTRs, inside_reads, strand):
	"""
	three_UTRs: a list of tuples [(start, end)]
	insider_reads: [tag_positions]
	return a value
	"""
	return 1

def ThreeUTRCharacteristics(three_UTRs, tag_positions, strand):
	"""
	Calculate the mean and standard-deviation
	Use the farthest transcription end site as the reference 
	"""
	# tag_positions: [position]
	# output: total read count, mean distance away from annotated PA, SD 
	total_read_count = float(len(tag_positions))
	
	if plus.match(strand):
		annotated_PAS = max([item[1] for item in three_UTRs])
		mean = sum ([(annotated_PAS - item )/total_read_count for item in tag_positions])
		pmi = sum([(item - (annotated_PAS - mean))*(item - (annotated_PAS - mean))/total_read_count for item in tag_positions])
	elif minus.match(strand):
		annotated_PAS = min ([item[0] for item in three_UTRs])
		mean = sum([(item - annotated_PAS)/total_read_count for item in tag_positions])
		pmi = sum([(item - (annotated_PAS + mean))*(item - (annotated_PAS + mean))/total_read_count for item in tag_positions])
	pmi = sqrt(pmi)
	return (total_read_count, mean, pmi)


def main(argv):
	parser = OptionParser()
	parser.add_option("-f", "--forwardreadfile", action="store", type="string", dest="ReadsOnForwardStrand", help="input bed file for RNASeq raw reads on forward strand", metavar="<file>")
	parser.add_option("-r", "--reversereadfile", action="store", type="string", dest="ReadsOnReverseStrand", help="input bed file for RNASeq raw reads on reverse strand", metavar="<file>")
	parser.add_option("-u", "--entrez_genes_file", action="store", type="string", dest="entrez_genes", metavar="<file>", help="file with curated known genes clustered by entrez ID in pickle format")
	parser.add_option("-g", "--fragment_size", action="store", type="int", dest="fragment_size", help="fragment_size determines the shift (half of fragment_size of ChIP-seq read position, in bps", metavar="<int>")
	parser.add_option("-o", "--outfile", action="store", type="string", dest="outfile", help="outfile name", metavar="<file>")
	parser.add_option("-s", "--species", action="store", type="string", dest="species",help="species, mm8, hg18, etc", metavar="<str>")
	parser.add_option("-d", "--3UTRdownstreamextension", action="store", type="int", dest="downstream_extension",help="3UTR down stream extension", metavar="<int>")
	
	(opt, args) = parser.parse_args(argv)
	
	if len(argv) < 14:
		parser.print_help()
		sys.exit(1)
	
	startTime = time.time()
	
	allowance = 10
	
	if opt.species in GenomeData.species_chroms.keys():
		chroms = GenomeData.species_chroms[opt.species];
		chrom_lengths = GenomeData.species_chrom_lengths[opt.species]
	else:
		print "This species is not recognized, exiting";
		sys.exit(1);
	
	# entrez_gene_collection is a KnownEntrezGenes class object. The core is a entrez_genes.entrez_genes is a dic (keyed by entrez_id) of lists of EntrezGene object
	annotation = open(opt.entrez_genes, 'rb')
	entrez_gene_collection = Entrez.KnownEntrezGenes(chroms, pickle.load(annotation)) 
	annotation.close()
	
	# test module
	test = 0
	if test == 1:
		print "Testing gene structure"
		test_id = 54
		Entrez.test_gene_structure(entrez_gene_collection, test_id)
	

	# Filter cluster of refseq_ids (keyed by entrez_id) according to the criterion of identical cdsEnd
	entrez_ids_with_unique_cdsEnd = entrez_gene_collection.get_ids_with_unique_cdsEnd()
	print "There are ", len(entrez_ids_with_unique_cdsEnd), " Entrez IDs each of which has a unique cdsEnd."
	
	
	#get total read count
	totalcount_F = get_total_tag_counts.get_total_tag_counts(opt.ReadsOnForwardStrand);
	totalcount_R = get_total_tag_counts.get_total_tag_counts(opt.ReadsOnReverseStrand);
	totalcount = totalcount_F + totalcount_R
	print totalcount_F, totalcount_R
	
	#Clear the file and write the first line, needs to be modified
	outf = open(opt.outfile, 'w')
	#outline = "# Entrez ID \t Main Refseq ID \t 3UTR union length \t Length Index \t PA Multiplicity Index \t 3UTR Read Count \t RefSeq IDs \t Gene symbols \n"
	outline = "# Entrez ID \t 3UTR Union length \t RUD \t 3UTR Read Count \t RefSeq IDs \t Gene symbols \n"
	outf.write(outline)
	outf.close()
	
	#index: column in bed file for sorting
	index = 2
	
	print "Process genes on forward strand"
	entrez_ids_on_forward_strand = entrez_gene_collection.get_strand_specific_ids("+", entrez_ids_with_unique_cdsEnd)
	print "There are ", len(entrez_ids_on_forward_strand), " Entrez IDs on forward strand."
	entrez_gene_subset = Entrez.KnownEntrezGenes(chroms, entrez_gene_collection.subset(entrez_ids_on_forward_strand))
	
	Calculate3UTRUsage(entrez_gene_subset, opt.ReadsOnForwardStrand, index, chroms, opt.fragment_size, opt.downstream_extension, opt.outfile)
	
	
	print "Process genes on reverse strand"
	entrez_ids_on_reverse_strand = entrez_gene_collection.get_strand_specific_ids("-", entrez_ids_with_unique_cdsEnd)
	print "There are ", len(entrez_ids_on_reverse_strand), " Entrez IDs on reverse strand."
	entrez_gene_subset = Entrez.KnownEntrezGenes(chroms, entrez_gene_collection.subset(entrez_ids_on_reverse_strand))
	
	Calculate3UTRUsage(entrez_gene_subset, opt.ReadsOnReverseStrand, index, chroms, opt.fragment_size, opt.downstream_extension, opt.outfile)
	
	print "it took", time.time() - startTime, "seconds."
	
if __name__ == "__main__":
	main(sys.argv)