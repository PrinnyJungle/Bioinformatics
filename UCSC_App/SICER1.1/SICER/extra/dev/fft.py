import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import numpy as np

def main(argv):
	parser = OptionParser()
	parser.add_option("-i", "--infile", action="store", type="string", dest="inFile", metavar="<file>", help="correlation profile")
	parser.add_option("-o", "--outfile", action="store", type="string", dest="outFile", metavar="<file>", help="fft profile")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 4:
        	parser.print_help()
        	sys.exit(1)
	
	f = open(opt.inFile,'r')
	x = []
	y = []
	for line in f:
		if not re.match("#", line):
			line = line.strip()
			sline = line.split()
			x.append(atoi(sline[0]))
			y.append(atof(sline[1]))
	f.close()
	
	yarray = np.array(y)	
	yfourier = np.fft.rfft(yarray)
	yfourier_powerspectrum = np.abs(yfourier)**2
			
	f=open(opt.outFile, 'w')
	for i in xrange(len(yfourier)):
		outline =  str(yfourier_powerspectrum[i]) + '\t' + str(yfourier[i]) +  '\n'
		f.write(outline)
	f.close() 

if __name__ == "__main__":
	main(sys.argv)