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
pyrEval = sys.argv[3]


# Clean Summary before XML dump
for fname in glob.iglob(path_ + '/*'):
	f = open(fname, 'r')
	lines = f.readlines()
	f.close()
	clean = []
	for line in lines:
		line = line.replace("'", '').replace('`', '')
		# if '.' in line:
		# 	ind = line.index('.')
		# 	if len(line) == ind + 1:
		# 		pass
		# 	elif line[ind + 1] != ' ':
		# 		line[ind] = ' '
		clean.append(line)
	with open(fname, 'w') as f:
		for line in clean:
			f.write(line)
	f.close()



for filename in glob.glob(os.path.join(path_, '')):
	print "current filename", filename
	print mode
	if int(mode) == 1:
		outpath = pyrEval + "/Preprocess/peer_summaries"
	elif int(mode) == 2:
		outpath = pyrEval + "/Preprocess/wise_crowd_summaries"
	#elif int(mode) == 3:
		#outpath = pyrEval + "/Preprocess/test_summaries"
	else:
		print "Option doesn't exist!!!"
	if outpath:
		print outpath
		command2 = "java -cp '*' edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse,depparse -file "+filename+" -outputDirectory "+outpath
		os.system(command2)




