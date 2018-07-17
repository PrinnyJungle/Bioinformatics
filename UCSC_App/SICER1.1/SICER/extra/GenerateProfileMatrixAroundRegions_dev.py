#!/usr/bin/env python

"""
03/2011 Weiqun Peng, Sean Grullon

This is a template for the analysis of tag distribution with respect
to a set of regions, such as promoter+ gene body of known genes.

"""

import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import bisect
import pylab

import Utility
import BED_revised;
import UCSC;
import GenomeData
import SeparateByChrom
import GenerateProfileAroundLocations
import GenerateProfileMatrixAroundLocations
import GenerateAroundRegions

"""
The plan here is to get a profile for each modification across sets of
genes.

Break the 'gene region' up into:

-5kb ... -1 kb ...

...1st 5% of genes, 2nd 5% of gene,  .... last 5% of gene, ...

... +1 kb ... +5 kb

Get the tag densities in each region.
"""

plus = re.compile("\+");
minus = re.compile("\-");

Dir = os.getcwd();


def getGeneBodyProfileMatrix(coords, genicPartition, pshift, mshift, bed_vals, minimum_genic_resolution):
	"""
	Output a list of read counts normalized by length to per 1000 bps. The length of the list is genicPartition.
	
	THe normalization is done gene by gene. The alternative approach is the add up all reads in the first partition of all genes, and divide it by the total length of the first partition of all genes. This alternative approach is biased towards large genes. 
	
	score is absolute read count, only normalized by length, not by library size.
	
	returns a dictionary {g.name:[scores]}
	"""
	all_genes_scores = {}
	
	plus_scores = [0.0] * genicPartition; #Normalized by length already
	minus_scores = [0.0] * genicPartition;#Normalized by length already
	scores = [0.0] * genicPartition;#Normalized by length already
	
	for chrom in coords.keys():
		genes = coords[chrom];
		if chrom in bed_vals.keys():
			(plus_starts, minus_starts) = GenerateProfileAroundLocations.breakUpStrands(bed_vals[chrom]);
			if not Utility.is_list_sorted(plus_starts):
				plus_starts.sort();
			if not Utility.is_list_sorted(minus_starts):
				minus_starts.sort();
			plus_starts = [ item + pshift for item in plus_starts ]
			minus_starts = [ item - mshift for item in minus_starts ]	
			
			for g in genes:
				gene_length = abs(g.txStart - g.txEnd);
				partition_size = float(gene_length) / genicPartition;
				normalization = float(partition_size)/1000;
				resolution = int(partition_size);
				if resolution > minimum_genic_resolution:
					if plus.match(g.strand):
						for i in xrange(genicPartition):
							start = g.txStart + i * partition_size
							end = start + partition_size - 1
							plus_scores[i] = GenerateProfileAroundLocations.getProfileNearPosition(int(start), g.strand, 0, resolution, resolution, resolution, plus_starts)[0]/normalization
							minus_scores[i] = GenerateProfileAroundLocations.getProfileNearPosition(int(start), g.strand, 0, resolution, resolution, resolution, minus_starts)[0]/normalization
					elif minus.match(g.strand):
						## notice, swapped strands for tags because we're working on the crick strand now
						# ie, for genes on the minus strand, plus reads --> minus reads, minus-reads --> plus reads
						for i in xrange(genicPartition):
							end = g.txEnd - i * partition_size;
							start = end - partition_size + 1;
							plus_scores[i] = GenerateProfileAroundLocations.getProfileNearPosition(int(end), g.strand, 0, resolution, resolution, resolution, minus_starts)[0]/normalization
							minus_scores[i] = GenerateProfileAroundLocations.getProfileNearPosition(int(end), g.strand, 0, resolution, resolution, resolution, plus_starts)[0]/normalization	
					else:
						print "Wrong value for orientation, which can only be + or -";
						sys.exit (1);
					for i in xrange(genicPartition):
						scores[i] = plus_scores[i] +  minus_scores[i];
					all_genes_scores[g.name] = scores
	return all_genes_scores;
		
def main(argv):
	parser = OptionParser()
	parser.add_option("-k", "--known_gene_file", action="store", type="string",
			dest="genefile", help="file with known gene info", metavar="<file>")
	parser.add_option("-b", "--bedfile", action="store", type="string",
			dest="bedfile", help="file with tags in bed format", metavar="<file>")
	parser.add_option("-c", "--TypeOfSites", action="store", type="string",
			dest="type", help="GENE, ISLAND", metavar="<str>")
	parser.add_option("-o", "--outfile", action="store", type="string",
			dest="outfile", help="outfile name", metavar="<file>")
	parser.add_option("-s", "--species", action="store", type="string",
			dest="species", help="species", metavar="<str>")
	parser.add_option("-u", "--UpstreamExtension", action="store", type="int",
			dest="upstreamExtension", help="UpstreamExtension", metavar="<int>")
	parser.add_option("-d", "--DownstreamExtension", action="store", type="int",
			dest="downstreamExtension", help="DownstreamExtension", metavar="<int>")
	parser.add_option("-r", "--resolution", action="store", type="int",
			dest="resolution", help="resolution of the upstream and downstream profile, eg, 5", metavar="<int>")
	parser.add_option("-w", "--WindowSize", action="store", type="int",
			dest="window_size", help="window size for averaging for the upstream and downstream profile. When window size > resolution, there is smoothing", metavar="<int>")
	parser.add_option("-g", "--genicPartition", action="store", type="int", 
			dest="genicPartition", help="genicPartition, eg, 20", metavar="<int>")	
	parser.add_option("-p", "--plusReadShift", action="store", type="int",
			dest="pshift", help="plusReadShift", metavar="<int>")
	parser.add_option("-m", "--minusReadShift", action="store", type="int", 
			dest="mshift", help="minusReadShift", metavar="<int>")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 24:
		parser.print_help()
		sys.exit(1)
		
	if opt.species in GenomeData.species_chroms.keys():
		chroms = GenomeData.species_chroms[opt.species];
		chrom_lengths = GenomeData.species_chrom_lengths[opt.species];
	else:
		print "This species is not recognized, exiting";
		sys.exit(1);
	
	#t0 = time.time()
	libName = (opt.bedfile).split('/')[-1]
	libName = libName.split('.')[0]
	extension = "-" + libName +'.bed1'
	SeparateByChrom.separateByChrom(chroms, opt.bedfile,  extension)
	num_genes = 0
	num_tags = 0
	
	if (opt.upstreamExtension % opt.resolution != 0):
		print "Please choose the resolution commensurate with the length of the upstream region"
		sys.exit (1)
	if (opt.downstreamExtension % opt.resolution != 0):
		print "Please choose the resolution commensurate with the length of the downstream region"
		sys.exit (1)
	
	upstreamNumPoints = opt.upstreamExtension/opt.resolution
	all_gene_scores = {}
	
	
	
	print "Species: ", opt.species;
	print "Upstream extension: ", opt.upstreamExtension;
	print "Downstream extension: ", opt.downstreamExtension;
	print "Upstream and Downstream resolution:", opt.resolution;
	print "Upstream and Downstream Scanning window size: ", opt.window_size;
	print "Genic partition: ", opt.genicPartition;
	print "Plus reads shift: ", opt.pshift
	print "Minus reads shift: ", opt.mshift 

	if opt.type == "GENE":
		coords = UCSC.KnownGenes(opt.genefile);
	elif opt.type == "ISLAND":
		# Build coords in the mode of a pseudo ucsc file, all pseudo genes are in the positive direction
		# Here we are assuming that the file has the format chrom start end + .....for each line
		# chrom is sline[0], start is sline[1], end is sline[2]
		
		strand = '+'
		coords = {}
		index = 0
	
		infile = open(opt.genefile, 'r');
		for line in infile:
			""" check to make sure not a header line """
			if not re.match("track", line):
				index += 1;
				line = line.strip();
				sline = line.split();
				if sline[0] not in coords.keys():
					coords[sline[0]] = [];
				name = "Island" + str(index)
				chrom = sline[0]
				txStart = atoi(sline[1]);
				txEnd = atoi(sline[2]);
				# (name, chrom, strand, txStart, txEnd, cdsStart, cdsEnd, exonCount, exonStarts, exonEnds)
				mycoord = UCSC.UCSC(name, chrom, strand, txStart, txEnd, txStart, txEnd, 0, '0', '0');
				coords[chrom].append(mycoord)
		infile.close();
	else:
		print "Only two types of locations are allowed: GENE, ISLAND"
		sys.exit(1); 
	
	normalization = num_tags/1000000.0;
	
	minimum_genic_resolution = 10
	old_num_genes = getNumGenes(coords)
	coords = findEligibleGenes(coords, chroms, opt.genicPartition, minimum_genic_resolution) # no longer a knowngene object
	num_genes = getNumGenes(coords)
	print num_genes - new_num_genes, " genes whose length does not support minimal genic resolution of ", minimum_genic_resolution, " or are on exotic chroms, are discarded"
	print "Number of " + opt.type + ": ", num_genes;
	print "Number of reads: ", num_tags
	
	for chrom in chroms:
		chrombed = chrom + extension;
		if Utility.fileExists(chrombed):
			bed_vals = {};
			bed_vals = BED_revised.BED(opt.species, chrombed, "BED2");
			num_tags += bed_vals.getNumVals()
			if (chrom in coords.keys()):
				if (len(coords[chrom]) > 0):
					mycoords={}
					scoredic_upstream = {}
					scoredic_downstream = {}
					scoredic_genebody = {}
					
					mycoords[chrom] = coords[chrom];
					scoredic_upstream = GenerateProfileMatrixAroundLocations.getTSSPMProfileMatrix(mycoords, opt.upstreamExtension, 0, opt.resolution, opt.window_size, opt.pshift, opt.mshift, bed_vals)
					scoredic_downstream = GenerateProfileMatrixAroundLocations.getTESPMProfileMatrix(mycoords, 0, opt.downstreamExtension, opt.resolution, opt.window_size, opt.pshift, opt.mshift, bed_vals)
					scoredic_genebody = getGeneBodyProfileMatrix(mycoords, opt.genicPartition, opt.pshift, opt.mshift, bed_vals, minimum_genic_resolution)
					
					myid_set = list( set(scoredic_upstream.keys()) & set(scoredic_downstream.keys()) & set(scoredic_genebody.keys()))
					chrom_gene_scores = {}
					count_normalization = float(opt.window_size)/1000.0
					for myid in myid_set:
						chrom_gene_scores[myid] = [item/count_normalization for item in scoredic_upstream[myid]] + scoredic_genebody.keys[mykey] + [ item/count_normalization for item in scoredic_downstream[mykey]]
	all_genes_scores.update(chrom_gene_scores)	
	# Save in a file
	outFile = open(opt.outfile,'w')
	for mykey in xrange(len(all_genes_scores.keys())):
		outline = mykey + "\t" + "\t".join( [str(item/normalization) for item in all_genes_scores[mykey]] ) + '\n'
		outFile.write(outline)
	outFile.close()
	
	#test
	totalPoints = upstreamNumPoints + opt.genicPartition + downstreamNumPoints;
	half_partition = int(opt.resolution/2.0);
	
	upstreamXcoordinates = [0.0]*upstreamNumPoints;
	for i in xrange(upstreamNumPoints):
		upstreamXcoordinates[i] = -1.0 * opt.upstreamExtension + half_partition + i * opt.resolution
	downstreamXcoordinates=[0.0]*downstreamNumPoints;
	for i in xrange(downstreamNumPoints):
		downstreamXcoordinates[i] = half_partition + i * opt.resolution
	genebodyXcoordinates=[0.0]*opt.genicPartition
	for i in xrange(opt.genicPartition):
		genebodyXcoordinates[i]=float((i+1))/opt.genicPartition;
	
	overallXcoordinates = upstreamXcoordinates + genebodyXcoordinates + downstreamXcoordinates
	overall_score_profile = [0] * overallXcoordinates
	for mykey in xrange(len(all_genes_scores.keys())):
		assert( len(overallXcoordinates) == len(all_genes_scores[mykey]) )
		for i in xrange(overallXcoordinates):
			overall_score_profile[i] += (all_genes_scores[mykey])[i]

	#Plot it out
	xcords = [0]*len(overallXcoordinates)
	for i in xrange(len(xcords)): 
		xcords[i] = i
	
	libName = (opt.bedfile).split('/')[-1]
	libName = libName.split('.')[0]
	annotationName = (opt.genefile).split('/')[-1]
	annotationName = annotationName.split('.')[0]
	title = libName + " on " + annotationName
	legend = ""
	GenerateAroundRegions.plot_profile(opt.upstreamExtension, downstreamExtension, opt.resolution, opt.genicPartition, xcords, overall_score_profile, 0,  title, legend, opt.outfile+'_plot.eps')
	
	SeparateByChrom.cleanup(chroms, extension)
	
if __name__ == "__main__":
    main(sys.argv)


        
