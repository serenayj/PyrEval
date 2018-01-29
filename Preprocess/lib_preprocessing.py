""" Methods for Preprocessing Summaries """
# 	Script for libraries of preprocessing summaries

#    Copyright (C) 2017 Yanjun Gao

#    This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

#def CoreNLPdecomposition(fname):
#	print "RUNNING CoreNLP ON {}".format(fname)
#	""" Takes input file file, creates xml parse using Stanford Core NLP
#		Input -- File in Summaries Directory
#		Output -- xml file to Preprocess Directory
#		Actions -- move xml file to CoreNLP_XMLs """
#	cmd = 'java -cp "CoreNLP/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file ' + fname
#	os.system(cmd)
#	mv = 'mv ' + getRoot(fname) + '.xml' + ' CoreNLP_XMLs/'
#	os.system(mv)

def DecomposeSummary(fname, summ_ind, dir1):
	print "DECOMPOSING SENTENCES FROM SUMMARY {}".format(fname)
	""" Reads in XML file from CoreNLP_XMLs, facilitates sentence decomposition, outputs .segs file """
	#cmd = 'python sentparser.py ' + fname + '.xml ' + str(summ_ind)
	cmd = 'python sentparser.py ' + fname +' ' + str(summ_ind) + ' '+ dir1
	os.system(cmd)

def CleanSegmentations(fname, directory, summ_ind):
	print "CLEANING SENTENCE DECOMPOSITION FROM SUMMARY {}".format(getRealName(fname) + '.segs')
	""" Reads in .segs file moves it to its directory in Decomposed Summaries/, cleans file of segment segment_ids """
	#segFile = 'DecomposedSummaries/' + getRealName(fname) + '.segs'
	#mv = 'mv ' + segFile + ' ' + directory
	#os.system(mv)
	file_dir = directory +'/'+str(summ_ind)
	segFile = file_dir +'/' + getRealName(fname) + '.segs'
	with open(segFile, 'r') as f:
		lines = f.readlines()
		segments = [line.split('&')[4] for line in lines if len(line) >1]
		seg_ids = ['&'.join(line.split('&')[:4]) for line in lines if len(line) >1]
	f.close()
	with open(segFile + '.cl', 'w') as f:
		for segment in segments:
			f.write(segment)
	f.close()
	return segFile, seg_ids

#def VectorizeSummary(fname, seg_ids, directory, summ_ind):
#	print "VECTORIZING SEGMENTS FROM SUMMARY {}".format(fname + '.cl')
#	vectors = vectorize(fname + '.cl')
#	fname = directory +'/'+str(summ_ind)+ '/' + getRealName(fname) + '.ls'
#	with open(fname, 'w') as f:
#		for n, vec in enumerate(vectors):
#			line = seg_ids[n] + '&' + str(vec) + '\n'
#			f.write(line)
#	f.close()

def VectorizeSummary(fname, directory, summ_ind, mode=None):
	print "VECTORIZING SEGMENTS FROM SUMMARY {}".format(fname)
	segFile = directory + '/' + str(summ_ind) + '/' + getRealName(fname) + '.segs'
	vectors = vectorize(segFile, mode)
	fname = directory +'/'+str(summ_ind)+ '/' + getRealName(fname) + '.ls'
	with open(fname, 'w') as f:
		for n, vec in enumerate(vectors):
			f.write(vec + '\n')


