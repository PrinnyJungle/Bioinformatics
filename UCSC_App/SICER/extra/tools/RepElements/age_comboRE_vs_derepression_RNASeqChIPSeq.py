#!/usr/bin/env python

"""
main data structure: pkl file from /home/data/mm9/Lin/processed/RepElements/brokendown/summary:

summary pickle data structure for RNASeq 
{id:
	{'annotation':RepElement class instance
	'index12_rc':
	'index12_rpkm':
	'index3_rc':
	'index3_rpkm':
	'index6_rc':
	'index6_rpkm':
	'index8_rc':
	'index8_rpkm':
	'index9_rc':
	'index9_rpkm':
	}
}

summary pickle data structure for ChIPSeq 
{id:
	{'annotation':RepElement class instance
	'H3K4me3_WT-W200-G200-E500-islandfiltered_rc':
	'H3K4me3_WT-W200-G200-E500-islandfiltered_rpkm':
	'H3K4me3_mir34bc_KO-W200-G200-E500-islandfiltered_rc':
	'H3K4me3_mir34bc_KO-W200-G200-E500-islandfiltered_rpkm':
	'H3K9me3_WT-W200-G400-E500-islandfiltered_rc':
	'H3K9me3_WT-W200-G400-E500-islandfiltered_rpkm':
	'H3K9me3_mir34bc_KO-W200-G400-E500-islandfiltered_rc':
	'H3K9me3_mir34bc_KO-W200-G400-E500-islandfiltered_rpkm':	
	}
}








assembled REs:
	{chrom: 
		{(region_start, region_end):
			{"elements":[ids]; 
			"age":  
			RNA_target_name + "_rc":
			RNA_control_name + "_rc":
			"strand": "+";
			"num_boundary_elements": value; 
			"5_boundary_elements":[id]; 
			"5_boundary_elements_age":
			"3_boundary_elements":[id];
			"3_boundary_elements_age":
			"I_boundary_elements":[id]; 
			"expression_fc_"+RNA_target_name+"_vs_" + RNA_control_name: max_value
			}
		}
	}
	
	
RE_info:
	{id:
		{
		RNA_target_name + "_rc":
		RNA_control_name + "_rc":
		RNA_target_name + "_cluster_rc":
		RNA_control_name + "_cluster_rc":
		"cluster_elements":[ids]; 
		"cluster_region":(start, end); 
		"num_boundary_elements": value;
		"expression_fc": value
		"cluster_expression_fc":max_fc
		}
	}

"""

import re, os, sys, shutil
from math import *   
from string import *
from optparse import OptionParser
import operator
import time
from operator import itemgetter
import scipy.stats
import matplotlib.pyplot as plt
import matplotlib
try:
   import cPickle as pickle
except:
   import pickle

sys.path.append('/home/wpeng/data/SICER1.1/SICER/lib')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra')
sys.path.append('/home/wpeng/data/SICER1.1/SICER/extra/tools/RepElements')

import Utility_extended
import RepElements
import AssembleFeatures
import get_read_count_on_REs
import AnalyzeRNASeq

def scatterplot(a, b, title, xscale='log', yscale='log'):
	"""
	a, b are lists or arrays
	"""
	assert len(a)==len(b)
	plt.plot(a, b, "ro", markersize = 3.5, alpha = 1);
	ax = plt.gca();
	ax.set_xscale(xscale)
	ax.set_yscale(yscale)
	#ax.set_aspect(1.) 
	ax.grid (color='gray', linestyle='dashed')
	plt.savefig(title + ".png", format="png")
	plt.close()
	
def main(argv):
	parser = OptionParser()
	parser.add_option("-r", "--name_for_RNASeq_pickle_file", action="store", type="string", dest="RNASeq_summary_name", help="the name of the RNASeq_pickle file", metavar="<str>")
	parser.add_option("-c", "--name_for_ChIPSeq_pickle_file", action="store", type="string", dest="ChIPSeq_summary_name", help="the name of the ChIPSeq_pickle file", metavar="<str>")
	parser.add_option("-o", "--name_for_the_output_summary_file", action="store", type="string", dest="output_name", help="the name of the output file", metavar="<str>")
	
	(opt, args) = parser.parse_args(argv)
	if len(argv) < 4:
		parser.print_help()
		sys.exit(1)
	
	RNA_target_name = "index8"
	RNA_control_name = "index6"
	RNASeq_summary_name = (opt.RNASeq_summary_name).split('/')[-1]
	RNASeq_summary_name = (RNASeq_summary_name).split('.')[0]
	
	# decode the RNASeq pkl structure
	inf = open(opt.RNASeq_summary_name, 'rb')
	this_RNASeq_summary = pickle.load(inf)
	inf.close()
	print AnalyzeRNASeq.get_feature_names(this_RNASeq_summary)
	
	
	
	
	
	
	#myresult_age: {myid:(age, quality, myfc)}
	
	# Age vs derepression for individual REs
	rc_threshold = 3
	(myresult_age, myresult_age_on_mappable_REs) = AnalyzeRNASeq.age_vs_derepression_for_RE_family(this_RNASeq_summary, RNA_RNA_target_name, RNA_control_name, rc_threshold, pc = 5)
	print "There are %d elements in %s " %(len(myresult_age.keys()), RNASeq_summary_name)
	mykeys = sorted(myresult_age.keys())
	age = [myresult_age[myid][0] for myid in mykeys]
	quality = [myresult_age[myid][1] for myid in mykeys] 
	expression_fc = [myresult_age[myid][2] for myid in mykeys] 
	scatterplot(age, expression_fc, "age_vs_derepression_for_" + RNASeq_summary_name, xscale='linear', yscale='log')
	scatterplot(quality, expression_fc, "quality_vs_derepression_for_" + RNASeq_summary_name, xscale='linear', yscale='log')

	#myresult_age_on_mappable_REs: {myid:(age, quality, myfc)}
	print "There are %d %s elements that have reads above %d" %(len(myresult_age_on_mappable_REs.keys()), RNASeq_summary_name, rc_threshold)
	mykeys = sorted(myresult_age_on_mappable_REs.keys())
	age = [myresult_age_on_mappable_REs[myid][0] for myid in mykeys]
	quality = [myresult_age_on_mappable_REs[myid][1] for myid in mykeys] 
	expression_fc = [myresult_age_on_mappable_REs[myid][2] for myid in mykeys] 
	scatterplot(age, expression_fc, "age_vs_derepression_for_mappable_" + RNASeq_summary_name, xscale='linear', yscale='log')
	#scatterplot(quality, expression_fc, "quality_vs_derepression_for_mappable_" + RNASeq_summary_name, xscale='linear', yscale='log')
	
	"""
	examine the sandwich structure
	
	extension: the max distance for between the boundary element and the edge of the element in consideration. There is the issue that the element in consideration can be really short, in which case the extension must be shorter, otherwise a boundary element will be counted as neighbouring both sides of the RE.As a result: extension = min ( extension, length_of_RE -10)
	
	"""
	extension = 100
	print "Setting the bounary allowance to be %d" %extension
	current_dir = os.getcwd()
	path = "/home/data/mm9/Lin/processed/RepElements/brokendown/summary"
	os.chdir(path)
	boundary_elements_file_name = "summary_on_LTR_ERV1_RLTR4_Mm.pkl"
	assert( Utility_extended.fileExists(boundary_elements_file_name) == 1)
	inf = open(boundary_elements_file_name, 'rb')
	boundary_elements = pickle.load(inf)
	inf.close()
	print "There are %d %s as boundary elements" %(len(boundary_elements.keys()), boundary_elements_file_name)
	os.chdir(current_dir)
	
	#The age cutoff on the boundary elements does not seem very useful
	age_cutoff = 100000 # no age cutoff
	filtered_boundary_elements = AnalyzeRNASeq.select_by_age(boundary_elements, age_cutoff)
	print "There are %d %s as boundary elements after age filtering" %(len(filtered_boundary_elements.keys()), boundary_elements_file_name)


	"""
	examine the sandwich structure after RE clustering
	RE_info:
	{id:{"cluster_region":(start, end); "num_boundary_elements": value; "cluster_expression_fc":{id:fc}}}}
	"""
	
	# extension with a value less than 150 is not as good as 150.
	family_names = AnalyzeRNASeq.find_family_name([this_RNASeq_summary])
	print "\n\nExamine the sandwich structure after RE clustering, ", family_names
	print "There are %d elements in %s" %(len(this_RNASeq_summary.keys()), family_names[0])
	cluster_extension = 150 
	print "Setting the cluster extension to be %d" %cluster_extension
	extension = 100
	print "Setting the boundary allowance to be %d" %extension
	pc= 5
	print "Pseudo count for calculating expression fold change is %d" %pc
	
	assembled_REs = AnalyzeRNASeq.explore_sandwich_structure_for_clusteredRE_family(this_RNASeq_summary, RNA_target_name, RNA_control_name, cluster_extension, extension, filtered_boundary_elements, pc)
	
	RE_info = AnalyzeRNASeq.convert_assembled_RE_to_single_RE_annotation(assembled_REs, [this_RNASeq_summary], RNA_target_name, RNA_control_name, pc)
	num_of_boundary_elements = []
	expression_fc_max = [] # use the max of expression fc to represent the whole cluster. 
	for myid in RE_info.keys():
		num_of_boundary_elements.append(RE_info[myid]["num_boundary_elements"]) 
		expression_fc_max.append(RE_info[myid]["cluster_expression_fc"]) # use the max of expression fc to represent the whole cluster. 
	scatterplot(num_of_boundary_elements, expression_fc_max, "comboRE_vs_derepression_for_clustered" + RNASeq_summary_name, xscale='linear', yscale='log')
	
	all_5_boundary_elements, all_3_boundary_elements, all_I_boundary_elements = AnalyzeRNASeq.get_boundary_elements_from_assembled_REs(assembled_REs)
	
	# Output in an ordered manner
	RE_summary = []
	for myid in RE_info.keys():
		my_num_of_boundary_elements = RE_info[myid]["num_boundary_elements"]
		cluster_ids = RE_info[myid]["cluster_elements"]
		num_REs_in_cluster = len(cluster_ids)
		my_expression_fc = RE_info[myid]["expression_fc"]
		cluster_expression_fc = RE_info[myid]["cluster_expression_fc"]
		RE_summary.append( (myid, my_num_of_boundary_elements, num_REs_in_cluster, my_expression_fc, cluster_expression_fc, ",".join(cluster_ids))) 
	sorted_RE_summary = sorted(RE_summary, key=itemgetter(1, 4))
	outf = open(opt.output_name + "_cluster_REs", "w")
	for item in sorted_RE_summary:
		outf.write("\t".join([str(i) for i in item]) + "\n")
	outf.close()
	
	"""
	examine the sandwich structure after RE clustering in both RLTR4-MM-int and MULV-int
	RE_info:
	{id:{"cluster_region":(start, end); "num_boundary_elements": value; "cluster_expression_fc":{id:fc}}}}
	"""
	
	
	current_dir = os.getcwd()
	path = "/home/data/mm9/Lin/processed/RepElements/brokendown/summary"
	os.chdir(path)
	RNASeq_summary_name_list = ["summary_on_LTR_ERV1_RLTR4_MM-int.pkl", "summary_on_LTR_ERV1_MuLV-int.pkl"]
	summaries = []
	for summary_file_name in RNASeq_summary_name_list:
		inf = open(summary_file_name, 'rb')
		summaries.append (pickle.load(inf))
		inf.close()
	
	family_names = AnalyzeRNASeq.find_family_name(summaries)
	print "\n\nExamine the sandwich structure after RE clustering ", family_names
	for i in xrange(len(summaries)):
		print "There are %d elements in %s" %(len(summaries[i].keys()), family_names[i])
	cluster_extension = 150 
	print "Setting the cluster extension to be %d" %cluster_extension
	extension = 100
	print "Setting the boundary allowance to be %d" %extension
	pc= 5
	print "Pseudo count for calculating expression fold change is %d" %pc
	
	
	assembled_REs = AnalyzeRNASeq.explore_sandwich_structure_for_clusteredRE_families(summaries, RNA_target_name, RNA_control_name, cluster_extension, extension, filtered_boundary_elements, pc)
	os.chdir(current_dir)
	
	test_id = 'RLTR4_MM-intchr2-87360672'
	#print test_id
	#print summaries[0][test_id][RNA_target_name + "_rc"]
	#print summaries[0][test_id][RNA_control_name + "_rc"]
	print AnalyzeRNASeq.get_rc_for_RE_cluster(summaries, RNA_target_name, RNA_control_name,[test_id])
	
	AnalyzeRNASeq.output_assembled_REs(assembled_REs, RNA_target_name, RNA_control_name, "assembled_REs_summary.dat")
	
	RE_info = AnalyzeRNASeq.convert_assembled_RE_to_single_RE_annotation(assembled_REs, summaries, RNA_target_name, RNA_control_name, pc)
	
	num_of_boundary_elements = []
	expression_fc_max = [] # use the max of expression fc to represent the whole cluster. 
	for myid in RE_info.keys():
		num_of_boundary_elements.append(RE_info[myid]["num_boundary_elements"]) 
		expression_fc_max.append(RE_info[myid]["cluster_expression_fc"]) # use the max of expression fc to represent the whole cluster. 
	scatterplot(num_of_boundary_elements, expression_fc_max, "comboRE_vs_derepression_for_clustered" + "+".join(family_names), xscale='linear', yscale='log')
	
	all_5_boundary_elements, all_3_boundary_elements, all_I_boundary_elements = AnalyzeRNASeq.get_boundary_elements_from_assembled_REs(assembled_REs)
	
	# Output in an ordered manner
	RE_summary = []
	for myid in RE_info.keys():
		my_num_of_boundary_elements = RE_info[myid]["num_boundary_elements"]
		cluster_ids = RE_info[myid]["cluster_elements"]
		num_REs_in_cluster = len(cluster_ids)
		my_expression_fc = RE_info[myid]["expression_fc"]
		cluster_expression_fc = RE_info[myid]["cluster_expression_fc"]
		RE_summary.append( (myid, my_num_of_boundary_elements, num_REs_in_cluster, my_expression_fc, cluster_expression_fc, ",".join(cluster_ids))) 
	sorted_RE_summary = sorted(RE_summary, key=itemgetter(1, 4))
	outf = open(opt.output_name + "_cluster_REs", "w")
	for item in sorted_RE_summary:
		outf.write("\t".join([str(i) for i in item]) + "\n")
	outf.close()
	
	
	print "\n\nFC histogram 0 LTR vs 2 LTR"
	zero_LTR_assembled_REs = AnalyzeRNASeq.get_assembled_REs_subset_by_num_LTR(assembled_REs, num_LTR=0)
	num_zero_LTR_assembled_REs = AnalyzeRNASeq.get_number_of_assembled_REs(zero_LTR_assembled_REs)
	print "There are %d 0_LTR assembled REs" % (num_zero_LTR_assembled_REs)
	fc_zero_LTR_assembled_REs =  AnalyzeRNASeq.get_fc_from_assembled_REs(zero_LTR_assembled_REs, RNA_target_name, RNA_control_name)
	log_fc_zero_LTR_assembled_REs = [log(value, 2) for value in fc_zero_LTR_assembled_REs]
	Utility_extended.output_list(log_fc_zero_LTR_assembled_REs, "log_fc_zero_LTR_assembled_REs.txt")
	Two_LTR_assembled_REs = AnalyzeRNASeq.get_assembled_REs_subset_by_num_LTR(assembled_REs, num_LTR=2)
	num_two_LTR_assembled_REs = AnalyzeRNASeq.get_number_of_assembled_REs(Two_LTR_assembled_REs)
	print "There are %d 2_LTR assembled REs" % num_two_LTR_assembled_REs
	fc_Two_LTR_assembled_REs =  AnalyzeRNASeq.get_fc_from_assembled_REs(Two_LTR_assembled_REs, RNA_target_name, RNA_control_name)
	log_fc_Two_LTR_assembled_REs = [log(value, 2) for value in fc_Two_LTR_assembled_REs]
	Utility_extended.output_list(log_fc_Two_LTR_assembled_REs, "log_fc_Two_LTR_assembled_REs.txt")
	print "log fc comparison:	p-value associated with ranking of the two sets of observations using MWU test: ", scipy.stats.mannwhitneyu(log_fc_Two_LTR_assembled_REs,log_fc_zero_LTR_assembled_REs)[1]
	
	
	
	plt.clf()
	plt.hist(log_fc_zero_LTR_assembled_REs, bins=15, color='r', normed=True, alpha=0.75, label= "0 LTR" )	
	plt.hist(log_fc_Two_LTR_assembled_REs, bins=50, color='b', normed=True, alpha=0.75, label= "2 LTR" )	
	plt.title(RNA_target_name + "_vs_" + RNA_control_name + "_on_assembled_REs, p-value = 2.7 E-77")
	plt.xlabel("log(Fold Change)")
	plt.ylabel("Frequency")
	plt.legend()
	#plt.legend(loc = 'upper left')
	plt.savefig(RNA_target_name + "_vs_" + RNA_control_name + "_on_assembled_REs" + "_logfc_hist" + ".eps", format="eps")
	plt.close()
	
	# age distribution between 0- and 2-LTR REs:
	ages_zero_LTR_assembled_REs = AnalyzeRNASeq.get_age_from_assembled_REs(zero_LTR_assembled_REs)
	log_ages_zero_LTR_assembled_REs = [log(value,2) for value in ages_zero_LTR_assembled_REs]
	Utility_extended.output_list(log_ages_zero_LTR_assembled_REs, "log_ages_zero_LTR_assembled_REs.txt")
	ages_two_LTR_assembled_REs = AnalyzeRNASeq.get_age_from_assembled_REs(Two_LTR_assembled_REs)
	log_ages_two_LTR_assembled_REs = [log(value,2) for value in ages_two_LTR_assembled_REs]
	Utility_extended.output_list(log_ages_two_LTR_assembled_REs, "log_ages_two_LTR_assembled_REs.txt")
	
	pvalue = scipy.stats.mannwhitneyu(log_ages_zero_LTR_assembled_REs,log_ages_two_LTR_assembled_REs)[1]
	print "log divergence comparison:	p-value associated with ranking of the two sets of observations using MWU test: ", pvalue
	plt.clf()
	plt.boxplot([log_ages_zero_LTR_assembled_REs, log_ages_two_LTR_assembled_REs])
	labels = ("0 LTR", "2 LTR")
	plt.xticks(range(1,3),labels, rotation=0)
	plt.title(RNA_target_name + "_vs_" + RNA_control_name + "_on_assembled_REs, p-value = 5.4 E-44")
	#plt.xlabel('Month')
	#plt.ylabel('$log_{2} Age$')
	plt.ylabel('log(Divergence)')
	plt.ylim([0,10])
	plt.savefig(RNA_target_name + "_vs_" + RNA_control_name + "_on_assembled_REs" + "_logdivergence_boxplot" + ".eps", format="eps")
	plt.close()
	
	
	#assembled REs classified according to # of LTR
	one_LTR_assembled_REs = AnalyzeRNASeq.get_assembled_REs_subset_by_num_LTR(assembled_REs, num_LTR=1)
	num_one_LTR_assembled_REs = AnalyzeRNASeq.get_number_of_assembled_REs(one_LTR_assembled_REs)
	print "There are %d 1_LTR assembled REs" % num_one_LTR_assembled_REs
	y = [num_two_LTR_assembled_REs, num_one_LTR_assembled_REs, num_zero_LTR_assembled_REs]
	labels = ["2 LTR", "1 LTR", "0 LTR"]
	plt.clf()
	wedges, labels = plt.pie(y, labels=labels, explode=None, shadow=False)
	plt.axis('equal')
	plt.savefig("assembled_REs_classified_according_to_#_of_LTR_pie_chart.eps", format="eps")
	plt.close()
	
	
	
	
	print "\n\nFocus on 2_LTR REs"
	print "\n\nAll 2_LTR assembled_REs have read count above 20 in either %s or %s!" %(RNA_target_name, RNA_control_name)
	rc_threshold =10
	
	fc_threshold = 4
	Two_LTR_assembled_REs_derepressed, Two_LTR_assembled_REs_nonderepressed = AnalyzeRNASeq.classify_assembled_REs_by_fc(Two_LTR_assembled_REs, RNA_target_name, RNA_control_name, fc_threshold)
	print "There are %d 2_LTR assembled REs with fc > %d" % (AnalyzeRNASeq.get_number_of_assembled_REs(Two_LTR_assembled_REs_derepressed), fc_threshold)
	
	#derepressed
	all_5_boundary_elements, all_3_boundary_elements, all_I_boundary_elements = AnalyzeRNASeq.get_boundary_elements_from_assembled_REs(Two_LTR_assembled_REs_derepressed)
	
	outfile = "5_boundary_elements_on_2_LTR_derepressed_assembled_REs"
	outf = open(outfile, "w")
	for item in all_5_boundary_elements:
		outf.write(item + "\n")
	outf.close()
	
	outfile = "3_boundary_elements_on_2_LTR_derepressed_assembled_REs"
	outf = open(outfile, "w")
	for item in all_3_boundary_elements:
		outf.write(item + "\n")
	outf.close()
	
	all_5_boundary_elements, all_3_boundary_elements, all_I_boundary_elements = AnalyzeRNASeq.get_boundary_elements_from_assembled_REs(Two_LTR_assembled_REs_nonderepressed)
	
	outfile = "5_boundary_elements_on_2_LTR_nonderepressed_assembled_REs"
	outf = open(outfile, "w")
	for item in all_5_boundary_elements:
		outf.write(item + "\n")
	outf.close()
	
	outfile = "3_boundary_elements_on_2_LTR_nonderepressed_assembled_REs"
	outf = open(outfile, "w")
	for item in all_3_boundary_elements:
		outf.write(item + "\n")
	outf.close()
	
	
	print "Correlate 5' LTR age with derepression"
	LTR_ages, myfc = AnalyzeRNASeq.correlate_two_features(Two_LTR_assembled_REs, "5_boundary_elements_age", "expression_fc_"+RNA_target_name+"_vs_" + RNA_control_name)
	scatterplot(LTR_ages, myfc, "5prime_LTR_age_vs_derepression")
	print "Correlate 5' LTR age with int age"
	LTR_ages, ages = AnalyzeRNASeq.correlate_two_features(Two_LTR_assembled_REs, "5_boundary_elements_age", "age")
	scatterplot(LTR_ages, ages, "5prime_LTR_age_vs_INT_age")
	
	ages, myfc = AnalyzeRNASeq.correlate_two_features(Two_LTR_assembled_REs, "age", "expression_fc_"+RNA_target_name+"_vs_" + RNA_control_name)
	scatterplot(ages, myfc, "INT_age_vs_derepression")
	
	
	
	
	
		
if __name__ == "__main__":
	main(sys.argv)
