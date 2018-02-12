""" PyrEval Pipeline """
import os
import sys
import glob
import re
import pandas as pd 

#this_dir = os.getcwd()

#DUC_patt = re.compile(r'D[\d]+')
#summary_dirs = this_dir + '/Summaries/*'
#summary_dirs = this_dir + '/D10-Summaries/*'
this_dir = "../D311/"

summary_dirs = list(glob.iglob(this_dir + '*'))

for summ_dir in summary_dirs:
	#dataset_ind = summ_dir[-5:]
	print "currently preprocessing", summ_dir 
	#preprocess1 = "python test_scoring.py %s %s " % (str(dataset_ind), str(summ_dir)) 
	
	#preprocess1 = "python pyramid.py "+str(summ_dir)
	preprocess1 = "python eduac.py "+str(summ_dir)
	os.system(preprocess1)
	#os.system(preprocess2)