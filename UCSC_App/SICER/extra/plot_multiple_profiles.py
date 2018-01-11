#!/usr/bin/env/python
# Plot two curves from a single file: x from the first column, y1 from the second column, y2 the third column

import re, os, sys, pylab,shutil
from optparse import OptionParser

comment = re.compile("#|track")

def read_parameters(para_file, mytype, num_curves):
	"""
	mytype = "location" or "genebody"
	return a dictonary
	"""
	parameters = {}
	f = open(para_file, 'r')
	line_index = 0
	if mytype == "location":
		line = f.readline()
		while (comment.match(line) is True):
			line = f.readline()
		parameters["range"] = float(line.strip())
		line = f.readline()
		parameters["title"] = line.strip()
		line = f.readline()
		parameters["x_label"] = line.strip()
		parameters["legend"] = []
		for i in xrage(num_curves):
			line = f.readline()
			parameters["legend"].append(line.strip())
	elif mytype == "genebody":
		#upstream, downstream, resolution, genicPartition, title, legend
		line = f.readline()
		while (comment.match(line) is True):
			line = f.readline()
		parameters["upstream"] = int(line.strip())
		line = f.readline()
		parameters["downstream"] = int(line.strip())
		line = f.readline()
		parameters["resolution"] = int(line.strip())
		line = f.readline()
		parameters["genicPartition"] = int(line.strip())
		line = f.readline()
		parameters["title"] = line.strip()
		parameters["legend"] = []
		for i in xrange(num_curves):
			line = f.readline()
			parameters["legend"].append(line.strip())
	else:
		print "%s is not legitimate. It can only be location or genebody" %mytype
		exit(1)
	return parameters

def read_data(data_file):
	"""
	data file has multiple columns, 
	the first column denotes the x values
	the second, third .. columns denotes the y1, y2, .. values
	
	return a list of lists, each of which represents a data column
	"""
	data_row=[]
	data=[]
	f = open(data_file,'r')
	for line in f:
		if not comment.match(line):
			line = line.strip()
			data_row.append(map(float,line.split()))
	num_columns = len(data_row[0])
	for i in xrange(num_columns):
		data.append([])
	for item in data_row:
		assert len(item)==num_columns
		for j in xrange(num_columns):
			data[j].append(item[j])
	f.close()
	return data


def plot_gene_body_profile(upstream, downstream, resolution, genicPartition, title, legend, data, outgraphname):
	pylab.figure(0)
	upstreamNumPoints = int(float(upstream)/resolution);
	downstreamNumPoints = int(float(downstream)/resolution);
	numTicksInBody = 10
	stepSize = int(float(genicPartition)/numTicksInBody);
	xticks_subset =[ 0]*numTicksInBody
	xticklabels_subset = [0]*numTicksInBody
	for i in xrange(numTicksInBody):
		xticks_subset[i] = upstreamNumPoints + i*stepSize - 0.5
		if i == 0:
			xticklabels_subset[i] = 'TSS'
		else:
			xticklabels_subset[i] = str(i*1.0/numTicksInBody)
	xticks = [-0.5] + xticks_subset + [upstreamNumPoints + genicPartition -0.5, upstreamNumPoints + genicPartition + downstreamNumPoints -1 + 0.5]
	xticklabels = [str(float(upstream/1000.0))+'k up'] + xticklabels_subset + ['TES', str(float(downstream)/1000.0) +'k down']
	pylab.clf()
	#color = ['b', 'dark green', 'dark orange', 'c', 'm', 'k']
	#color = ['b', 'gold', 'cyan', 'c', 'm', 'k']
	color = ['b', 'brown', 'blue', 'c', 'm', 'k']
	my_linewidth = 5.0
	if (legend != ""):
		for i in range(1, len(data)):
			pylab.plot(data[i], color[i], linewidth = my_linewidth, label=legend[i-1])
	else:
		for i in range(1, len(data)):
			pylab.plot(data[i], color[i], linewidth = my_linewidth)
	pylab.xlabel('Gene Coordinate',fontsize=30)
	ax=pylab.axes()
	ax.set_xticks(xticks)
	ax.set_xticklabels(xticklabels)
	pylab.ylabel('Normalized Read Count' , fontsize=30)
	pylab.title(title)
	if (legend != ""):
		pylab.legend()
	pylab.savefig(outgraphname+ ".eps", format='eps')
	pylab.savefig(outgraphname+ ".png", format='png')

def plot_location_profiles(myrange, title, x_label, legend, data, outgraphname):
	"""
	data: a list of lists. data[0]: x; data[i>=1] y_i
	legend:[]
	myrange: half_range [-myrange:myrange]
	"""
	pylab.figure(0)
	x = data[0]
	color = ['b', 'g', 'r', 'c', 'm', 'k']
	if (legend != ""):
		for i in range(1, len(data)):
			pylab.plot(x, data[i], color[i], linewidth=3.0, label=legend[i-1])
	else:
		for i in range(1, len(data)):
			pylab.plot(x, data[i], color[i], linewidth=3.0)
	pylab.xlabel(x_label,fontsize=30)
	pylab.xlim((-1*myrange),myrange)
	pylab.ylabel('Normalized Read Counts' , fontsize=30)
	pylab.title(title, fontsize=14)
	if (legend != ""):
		pylab.legend()	
	#pylab.show()
	pylab.savefig(outgraphname, format='eps')
 
def main(argv):
	parser=OptionParser()
	parser.add_option("-d","--data_file",action="store",type="string",dest="data_file",help="data file of format x, y1, y2")
	parser.add_option("-p","--parameter_file", action="store",type="string",dest="parameter_file",help="parameter file")
	parser.add_option("-n","--number_of_curves", action="store",type="int",dest="num_curves",help="number of curves")
	parser.add_option("-t","--profile_type",action="store",type="string",dest="profile_type",help="location or genebody")
	parser.add_option("-o","--outfile",action="store",type="string",dest="outfile",help="output file name ")
	(opt,args)=parser.parse_args()
	if len(argv) < 10:
		parser.print_help()
		sys.exit(1)
	
	parameters = read_parameters(opt.parameter_file, opt.profile_type, opt.num_curves)
	data = read_data(opt.data_file)
	if (opt.profile_type) == "location":
		plot_location_profiles(parameters["range"], parameters["title"], parameters["x_label"],  parameters["legend"], data, opt.outfile)
	elif (opt.profile_type) == "genebody":
		plot_gene_body_profile(parameters["upstream"], parameters["downstream"], parameters["resolution"], parameters["genicPartition"], parameters["title"], parameters["legend"], data, opt.outfile)
	else:
		print "%d is not legitimate. It can only be location or genebody" %opt.profile_type
		exit(1)
		
if __name__ == "__main__":
	main(sys.argv)

