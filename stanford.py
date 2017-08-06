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
	else:
		outpath = "../Preprocess/test_summaries"
	print outpath
	command2 = "java -cp '*' edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse,depparse -file "+filename+" -outputDirectory "+outpath
	os.system(command2)




