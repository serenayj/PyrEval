""" Methods for Preprocessing Summaries """
import os
from weiwei import vectorize

"""
=============== Methods ===================
"""

def getRoot(fname):
	slash = fname.rfind('/')
	return fname[(slash + 1):]

def getRealName(fname):
	fname = getRoot(fname)
	dot = fname.rfind('.')
	if dot == -1:
		dot = None
	return fname[:dot]

def CoreNLPdecomposition(fname):
	print "RUNNING CoreNLP ON {}".format(fname)
	""" Takes input file file, creates xml parse using Stanford Core NLP
		Input -- File in Summaries Directory
		Output -- xml file to Preprocess Directory
		Actions -- move xml file to CoreNLP_XMLs """
	cmd = 'java -cp "CoreNLP/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file ' + fname
	os.system(cmd)
	mv = 'mv ' + getRoot(fname) + '.xml' + ' CoreNLP_XMLs/'
	os.system(mv)

def DecomposeSummary(fname, summ_ind):
	print "DECOMPOSING SENTENCES FROM SUMMARY {}".format(fname + '.xml')
	""" Reads in XML file from CoreNLP_XMLs, facilitates sentence decomposition, outputs .segs file """
	cmd = 'python sentparser.py ' + fname + '.xml ' + str(summ_ind)
	os.system(cmd)

def CleanSegmentations(fname, directory):
	print "CLEANING SENTENCE DECOMPOSITION FROM SUMMARY {}".format(getRealName(fname) + '.segs')
	""" Reads in .segs file moves it to its directory in Decomposed Summaries/, cleans file of segment segment_ids """
	segFile = 'DecomposedSummaries/' + getRealName(fname) + '.segs'
	mv = 'mv ' + segFile + ' ' + directory
	os.system(mv)
	segFile = directory +'/' + getRealName(fname) + '.segs'
	with open(segFile, 'r') as f:
		lines = f.readlines()
		segments = [line.split('&')[4] for line in lines]
		seg_ids = ['&'.join(line.split('&')[:4]) for line in lines]
	f.close()
	with open(segFile + '.cl', 'w') as f:
		for segment in segments:
			f.write(segment)
	f.close()
	return segFile, seg_ids

def VectorizeSummary(fname, seg_ids, directory):
	print "VECTORIZING SEGMENTS FROM SUMMARY {}".format(fname + '.cl')
	vectors = vectorize(fname + '.cl')
	fname = directory + '/' + getRealName(fname) + '.ls'
	with open(fname, 'w') as f:
		for n, vec in enumerate(vectors):
			line = seg_ids[n] + '&' + str(vec) + '\n'
			f.write(line)
	f.close()
