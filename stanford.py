# Aug 6, 2017
# Step 0, move this file to stanford-corenlp folder 
# mode: 1: peer summries; 2: wise_crowd_summaries, 3:test_summaries 
# Usage: python stanford.py mode 

import os 
import sys
import glob 
#from lib_preprocessing import *

path_ = sys.argv[1]
mode = sys.argv[2]

for filename in glob.glob(os.path.join(path_,'*.txt')):
	print "current filename", filename
	print mode
	#mv = 'mv ' + getRoot(filename) + '.xml' + ' CoreNLP_XMLs/'
	#print "current filename", getRoot(filename)
	#os.system(mv)
	if int(mode) == 1:
		outpath = "../Preprocess/peer_summaries"
	elif int(mode) == 2:
		outpath = "../Preprocess/wise_crowd_summaries"
	elif int(mode) == 3:
		outpath = "../Preprocess/test_summaries"
	else:
		print "Option doesn't exist!!!"
	if outpath:
		print outpath
		command2 = "java -cp '*' edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse,depparse -file "+filename+" -outputDirectory "+outpath
		os.system(command2)




