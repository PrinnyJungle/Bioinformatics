
import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import time
import bisect
from operator import itemgetter
import copy
try:
   import cPickle as pickle
except:
   import pickle
   
import Utility_extended


def main(argv):
	parser = OptionParser()
	(opt, args) = parser.parse_args(argv)
		
	A = [(1,2.5), (3.5, 15), (45, 71), (74, 93)]
	B = [(1.2,2.5), (2, 7), (2,2), (57, 84)]
	print A
	print B
	print Utility_extended.intersect(A, B, 0.0001)
	
	
		
if __name__ == "__main__":
	main(sys.argv)