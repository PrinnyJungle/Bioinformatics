#!/usr/bin/env python
# 
# Authors: Chongzhi Zang, Weiqun Peng
#
# 
# Disclaimer
# 
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# Comments and/or additions are welcome (send e-mail to:
# wpeng@gwu.edu).
#
# Version 1.1  6/9/2010


import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import bisect
import numpy
import pylab

import BED_revised
import GenomeData
import SeparateByChrom
import filter_raw_tags_by_islands_dev
import Utility


Dir = os.getcwd();
grep = "/bin/grep";
cat = "/bin/cat";

plus = re.compile("\+");
minus = re.compile("\-");


def generateReadCountDic(chrom, start, end, binSize, strand, shift,rawReadFile, outfile):
	# This is good for very large islands with low read count density, so that a lot of bins have no reads
	# the code calling this should check that the start and end are not out of bounds
	# strand can be '+', '-', '+-'
	# return a sorted dictionary of [binStart: readCountInBin]
	# Also write the results in outfile if outfile name is not "".
	
	assert (end>=start)
	
	# Generate read list in (start, end) and sort it.
	readList=[]
	f = open(rawReadFile,'r')
	for line in f:
		if not re.match("#", line):
			line = line.strip()
			sline = line.split()
			if sline[0] == chrom:
				if plus.match(strand):
					if plus.match(sline[5]):
						position = atoi(sline[1]) + shift;
				elif minus.match(strand):
					if minus.match(sline[5]):
						position = atoi(sline[2]) - 1 - shift;
				elif strand == "+-":
					position = filter_raw_tags_by_islands_dev.tag_position(sline, shift)
				else:
					print "strand info is wrong: ", strand
					exit(1)
				if position>=start and  position<=end:
					readList.append(position)
	f.close()
	if not Utility.is_list_sorted(readList):
		readList.sort()
	
	# generate bins and read counts, only bins with reads are registered. 
	
	if(len(readList)>0):
		binStart=[]
		readCountInBin=[]
		currentBinStart = ((readList[0]-start)/binSize)*binSize
		currentReadCountInBin = 1;
		if (len(readList)>1):
			for i in range(1, len(readList)):
				newstart = ((readList[i]-start)/binSize)*binSize;		
				if newstart == currentBinStart: 
					currentReadCountInBin += 1;
				elif newstart > currentBinStart:
					# All the reads in the previous window have been counted 
					currentBinEnd = currentBinStart + binSize -1;
					# if the bin goes beyond the island end, it is discarded. 
					if currentBinEnd <= end:
						binStart.append(currentBinStart)
						readCountInBin.append(currentReadCountInBin)
					currentBinStart = newstart;
					currentReadCountInBin = 1;
				else:
					print 'Something is wrong!!!!!!!';
					
		currentBinEnd = currentBinStart + binSize -1;
		# if the window goes beyond the chromsome limit, it is discarded. 
		if currentBinEnd <= end:
			binStart.append(currentBinStart)
			readCountInBin.append(currentReadCountInBin)
	
	if outfile != "": 
		out = open(outfile, 'w');
		for i in xrange(len(binStart)):	
			outline = chrom + "\t" + str(binStart[i]) + "\t" + str(binStart[i] + binSize -1) + "\t" +  str(readCountInBin[i]) + "\n";
		out.write(outline);
		out.close();
		
	return (binStart, readCountInBin)

def average(numberOfBins, readCountInBin):
	avg = 0.0
	for item in readCountInBin:
		avg += item*1.0/numberOfBins # not divided by the length of the bin yet.
	return avg

def autoCorrelationDic(start, end, binStart, readCountInBin, distance, binSize):
	#distance has to be in terms of the number of bins
	assert (len(binStart) == len(readCountInBin))
	
	numberOfBins = (int)((end-start)/binSize); #incomplete bins are ignored
	numberOfPoints = numberOfBins - distance
	avg = average(numberOfBins, readCountInBin)
	
	correlation = 0
	
	for i in xrange(len(binStart)):
		currentBinStart = binStart[i];
		partnerCoordinate = binStart[i] + distance * binSize;
		if partnerCoordinate < end:
			partnerPosition = bisect.bisect_left(binStart, partnerCoordinate)
			if  partnerPosition < bisect.bisect_right(binStart, partner): #partnerCoordinate is in binStart
				correlation += (readCountInBin[i] - avg) * (readCountInBin[partnerPosition] - avg)
		
	return (numberOfPoints, correlation)	


def crossCorrelationDic(start, end, binStart1, readCountInBin1,  binStart2, readCountInBin2, distance, binSize):
	#distance has to be in terms of the number of bins
	assert (len(binStart1) == len(readCountInBin1))
	assert (len(binStart2) == len(readCountInBin2))
	
	numberOfBins = (int)((end-start)/binSize); #incomplete bins are ignored
	numberOfPoints = numberOfBins - distance
	avg1 = average(numberOfBins, readCountInBin1)
	avg2 = average(numberOfBins, readCountInBin2)
	
	correlation = 0
	for i in xrange(len(binStart1)):
		currentBinStart = binStart1[i];
		partnerCoordinate = binStart1[i] + distance * binSize;
		if partnerCoordinate < end:
			partnerPosition = bisect.bisect_left(binStart2, partnerCoordinate)
			if  partnerPosition < bisect.bisect_right(binStart2, partner): #partnerCoordinate is in binStart
				correlation += (readCountInBin1[i] - avg1) * (readCountInBin2[partnerPosition] - avg2)
	return (numberOfPoints, correlation)	



def generateReadCountVector(chrom, start, end, binSize, strand, shift, rawReadFile):
	# This is good for  1) relative high read count density, so that most of the bins have reads  or 2) non-superscale islands
	# 
	# Could be memory intensive if the region is very large
	# the code calling this should check that the start and end are not out of bounds
	# strand can be '+', '-', '+-'
	assert (end>=start)
	numberOfBins = (int)((end-start)/binSize); #incomplete bins are ignored
	readCounts = [0]*numberOfBins
	
	f = open(rawReadFile,'r')
	for line in f:
		if not re.match("#", line):
			line = line.strip()
			sline = line.split()
			if sline[0] == chrom:
				if plus.match(strand):
					if plus.match(sline[5]):
						position = atoi(sline[1]) + shift;
						if position >= start and  position <= end:
							binIndex = (int)((position-start)/binSize)
							readCounts[binIndex] += 1
				elif minus.match(strand):
					if minus.match(sline[5]):
						position = atoi(sline[2]) - 1 - shift;
						if position >= start and  position <= end:
							binIndex = (int)((position-start)/binSize)
							readCounts[binIndex] += 1
				elif strand == "+-":
					position = filter_raw_tags_by_islands_dev.tag_position(sline, shift)
					if position >= start and  position <= end:
						binIndex = (int)((position-start)/binSize)
						readCounts[binIndex] += 1
				else:
					print "strand info is wrong: ", strand
					exit(1)
				
	f.close()
	return readCounts

def autoCorrelation(readCounts, distance):
	#distance has to be in terms of the number of bins
	numberOfBins = len(readCounts)
	numberOfPoints = numberOfBins - distance
	if numberOfPoints > 0:
		readCountsArray = numpy.array(readCounts)
		average = numpy.average(readCountsArray) # not divided by the length of the bin yet.
		correlation = numpy.dot(readCountsArray[0 : numberOfBins-distance] - average, readCountsArray[0 + distance : numberOfBins] - average)
	else:
		numberOfPoints = 0, 
		correlation = 0
	return (numberOfPoints, correlation)
	
def autoCorrelations(readCounts, resolution, maxDistance, minPoints):
	# resolution and maxdistance are in terms of number of bins
	numberOfPoints = []
	correlations = []
	total = (int) (maxDistance/resolution) + 1
	for i in xrange(total):
		distance = i*resolution
		currentNumberOfPoints = len(readCounts) - distance
		if currentNumberOfPoints >= minPoints:
			(a,b) = autoCorrelation(readCounts, distance)
		else:
			a = 0
			b = 0
		numberOfPoints.append(a)
		correlations.append(b)
	return (numberOfPoints, correlations)
	
def crossCorrelation(readCounts1, readCounts2, distance):
	#distance has to be in terms of number of bins
	assert (len(readCounts1) == len(readCounts2))
	numberOfBins = len(readCounts1)
	numberOfPoints = numberOfBins - distance
	if numberOfPoints > 0:
		readCountsArray1 = numpy.array(readCounts1)[0 : numberOfBins-distance]
		average1 = numpy.average(readCountsArray1)
		readCountsArray2 = numpy.array(readCounts2)[0 + distance : numberOfBins]
		average2 = numpy.average(readCountsArray2)
		correlation = numpy.dot(readCountsArray1-average1, readCountsArray2-average2)
	else:
		numberOfPoints = 0, 
		correlation = 0
	return (numberOfPoints, correlation)

def crossCorrelations(readCounts1, readCounts2, resolution, maxdistance, minPoints):
	# minPoints
	# resolution, maxdistance have to be in terms of number of bins
	assert (len(readCounts1) == len(readCounts2))
	numberOfPoints = []
	correlations = []
	total = (int) (maxdistance/resolution) + 1
	for i in xrange(total):
		distance = i*resolution
		currentNumberOfPoints = len(readCounts1) - distance
		if currentNumberOfPoints >= minPoints:
			(a,b) = crossCorrelation(readCounts1, readCounts2, i*resolution)
		else:
			a = 0
			b = 0	
		numberOfPoints.append(a)
		correlations.append(b)
	return (numberOfPoints, correlations)

def plot_profile(x, y, fignum, title, legend, outgraphname):
	pylab.figure(fignum)
	if (legend != ""):
		pylab.plot(x, y, "b",label=legend[0])
	else:
		pylab.plot(x, y, "b")
	pylab.xlabel('Distance',fontsize=12)
	ax=pylab.axes()
	#ax.set_xticks(xticks)
	#ax.set_xticklabels(xticklabels)
	pylab.ylabel('Correlation' , fontsize=12)
	pylab.title(title)
	if (legend != ""):
		pylab.legend()
	pylab.show()
	pylab.savefig(outgraphname, format='eps')




def main(argv):
	parser = OptionParser()
	parser.add_option("-b", "--readfile", action="store", type="string", dest="readFile", metavar="<file>", help="raw read file in bed format")
	parser.add_option("-s", "--species", action="store", type="string", dest="species", help="species, mm8, hg18", metavar="<str>")
	parser.add_option("-i", "--islands", action="store", type="string", dest="islandFile", metavar="<file>", help="island File in chrom start end ... format")
	parser.add_option("-w", "--binSize", action="store", type="int", dest="binSize", metavar="<int>", help="bin size for resolution")
	parser.add_option("-m", "--minimum-number-of-points-per-island", action="store", type="int", dest="minimumRequiredPoints", metavar="<int>", help="minimum-number-of-data-points-needed-per-island")
	parser.add_option("-n", "--maxdistance", action="store", type="int", dest="maxDistance", metavar="<int>", help=" max distance for correlation, in terms of bin size")
	parser.add_option("-r", "--resolution", action="store", type="int", dest="resolution", metavar="<int>", help=" resolution in distance in terms of bin size")
	parser.add_option("-t", "--type", action="store", type="string", dest="type", metavar="<str>", help=" type of correlation, +auto, -auto, cross")
	parser.add_option("-f", "--shift", action="store", type="int", dest="shift", metavar="<int>", help=" shift of reads, only useful when calculate cross-correlation or combining the plus and minus reads")
	parser.add_option("-o", "--outfile", action="store", type="string", dest="out_file", metavar="<file>", help="output file")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 20:
        	parser.print_help()
        	sys.exit(1)
	
	if opt.species in GenomeData.species_chroms.keys():
		chroms = GenomeData.species_chroms[opt.species];
		chrom_lengths = GenomeData.species_chrom_lengths[opt.species];
	else:
		print "This species is not recognized, exiting";
		sys.exit(1);
	
	
	#t0 = time.time()
	if Utility.fileExists(opt.readFile) == 0:
		print opt.readFile, " does not exist"
		exit(1)
	
	libName = (opt.readFile).split('/')[-1]
	libName = libName.split('.')[0]
	extension = "-" + libName +'.bed1'
	SeparateByChrom.separateByChrom(chroms, opt.readFile,  extension)
	
	print "Species: ", opt.species
	print "Read File: ", opt.readFile
	print "Island File: ", opt.islandFile
	print "Bin Size: ", opt.binSize, "bp"
	print "Resolution: ", opt.resolution, " bins"
	print "Max distance: ", opt.maxDistance, " bins"
	assert (opt.type == "+auto" or opt.type == "-auto" or opt.type == "cross")
	print "Type of correlation: ", opt.type
	print "Reads shift: ", opt.shift

	# Here we are assuming that the file has the format chrom start end + .....for each line
	# chrom is sline[0], start is sline[1], end is sline[2]	
	if Utility.fileExists(opt.islandFile):	
		islandDic = BED_revised.BED(opt.species, opt.islandFile, "BED3")
	
	num_islands = 0
	for chrom in islandDic.keys():
		num_islands += len(islandDic[chrom]);
		# Clean up potential island-specific read files
		filter_raw_tags_by_islands_dev.cleanup_files(islandDic[chrom], extension)
	
	total = (int) (opt.maxDistance/opt.resolution) + 1
	distances = [0] * total
	numberOfPointsCollector = [0] * total
	correlationCollector = [0] * total
	
	totalReadCount = 0
	
	for chrom in chroms:
		chrombed = chrom + extension;
		if Utility.fileExists(chrombed):
			if (chrom in islandDic.keys()):
				if (len(islandDic[chrom]) > 0):
					# First find out all the reads that lands on islands and save them on island-specific temporary files.Then use only the read file specific to that island to do binning.  
					currentReadCount = filter_raw_tags_by_islands_dev.find_reads_on_each_island(chrombed, islandDic[chrom], opt.shift, extension)
					totalReadCount += currentReadCount
					for island in islandDic[chrom]:
						assert (island.start >= 0)
						assert (island.end <= chrom_lengths[chrom])
						islandReadFile = island.chrom + "-" + str(island.start) + "-" + str(island.end) + extension
						numberOfPoints = [0] * total
						correlations = [0] * total
						if opt.type == "+auto":
							readCountVector = generateReadCountVector(island.chrom, island.start, island.end, opt.binSize, "+", opt.shift, islandReadFile)
							(numberOfPoints, correlations) = autoCorrelations(readCountVector, opt.resolution, opt.maxDistance, opt.minimumRequiredPoints)
						elif opt.type == "-auto":
							readCountVector = generateReadCountVector(island.chrom, island.start, island.end, opt.binSize, "-", opt.shift, islandReadFile)
							(numberOfPoints, correlations) = autoCorrelations(readCountVector,opt.resolution, opt.maxDistance, opt.minimumRequiredPoints)
						elif opt.type == "cross":
							plusReadCountVector = generateReadCountVector(island.chrom, island.start, island.end, opt.binSize, "+", opt.shift, islandReadFile)
							minusReadCountVector = generateReadCountVector(island.chrom, island.start, island.end, opt.binSize, "-", opt.shift, islandReadFile)
							(numberOfPoints, correlations) = crossCorrelations(plusReadCountVector, minusReadCountVector, opt.resolution, opt.maxDistance, opt.minimumRequiredPoints)
						assert (len(numberOfPoints) == total)
						assert (len(correlations) == total)
						print chrom, island.start, island.end
						for i in xrange(total):
							if numberOfPoints[i] == 0:
								distances[i] = i * opt.resolution * opt.binSize
								print distances[i], "\t", numberOfPointsCollector[i], "\t", correlationCollector[i]
							numberOfPointsCollector[i] += numberOfPoints[i]
							correlationCollector[i] += correlations[i]
	
	# Normalization and output
	f = open(opt.out_file, 'w')
	for i in xrange(total):
		distances[i] = i * opt.resolution * opt.binSize
		correlationCollector[i] /= numberOfPointsCollector[i] #normalize by the number of points 
		correlationCollector[i] /= (totalReadCount/1000000.0)*(totalReadCount/1000000.0)
		print distances[i], "\t", numberOfPointsCollector[i], "\t", correlationCollector[i]
		outline = str(distances[i]) + "\t" + str(correlationCollector[i]) + "\n"
		f.write(outline)
	f.close()

	SeparateByChrom.cleanup(chroms, extension)
		
	#Plot it out
	title = libName + " " +  opt.type + "  correlation"
	legend = "B" + str(opt.binSize) + " S" + str(opt.shift)
	plot_profile(distances[1:], correlationCollector[1:], 0,  title, legend, opt.out_file + '.eps')

if __name__ == "__main__":
	main(sys.argv)
