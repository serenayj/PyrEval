# Script for running StanfordCoreNLP

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

# Aug 6, 2017
# Step 0, move this file to stanford-corenlp folder 
# mode: 1: peer summries; 2: wise_crowd_summaries, 3:test_summaries 
# Usage: python stanford.py mode 

import os
import sys
from stanfordcorenlp import StanfordCoreNLP
import logging
import glob

class StanfordNLP:
	def __init__(self, host='http://localhost', port = 9000):
		self.nlp = StanfordCoreNLP(host, port = port, timeout = 30000)
		self.props = {
				'annotators': 'tokenize,ssplit,pos,parse,depparse',
				'pipelineLanguage': 'en',
				'outputFormat': 'xml',                
		}
	def annotate(self, sentence):
		return self.nlp.annotate(sentence, properties=self.props)

#from lib_preprocessing import *

#Wasih (02-19-20) Use functions instead of calling script
#path_ = sys.argv[1]
#mode = sys.argv[2]
#pyrEval = sys.argv[3]

#Wasih (02-19-20) Use functions instead of calling script
def stanfordmain(path_, mode, pyrEval):
	
	#Wasih (02-17-20) find Stanford CoreNLP directory
	files = os.listdir(os.path.dirname(os.path.realpath(__file__)))
	print(files)	
	coreNlpDir = ""
	for filename in files:
		if (os.path.isdir(filename) and 'stanford' in filename):
			coreNlpDir = filename
			break
	print (coreNlpDir)

	if len(sys.argv) == 5:
		java_exec = sys.argv[4]
	else:
		java_exec = 'java'


	# Clean Summary before XML dump
	if os.path.isdir(path_):
		for filename in sorted(os.listdir(path_)):
			if filename[0] != '.':
				full_path = os.path.join(path_,filename)
				with open(full_path, 'r') as infile:
					lines = infile.readlines()
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
				with open(full_path, 'w') as outfile:
					for line in clean:
						outfile.write(line)

		filename = os.path.abspath(path_)
		print ("current filename", filename)
		print (mode)
		#Wasih (02-19-20) Use functions instead of calling script (Mode is already integer)    
		if mode == 1:
			outpath = os.path.join(pyrEval, 'Preprocess', 'peer_summaries')
		elif mode == 2:
			outpath = os.path.join(pyrEval, 'Preprocess', 'wise_crowd_summaries')
		#elif int(mode) == 3:
			#outpath = pyrEval + "/Preprocess/test_summaries"
		else:
			print ("Option doesn't exist!!!")
		if outpath:
			print (outpath)
			#Wasih (02-17-20) find Stanford CoreNLP directory	
			os.chdir(coreNlpDir)
			# TODO: Very clunky solution to set max heap size here
			#command2 = java_exec + ' -Xmx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse,depparse -file ' + filename + ' -outputDirectory ' + outpath
			#Wasih 04-16-21: Create a pipeline object and make a call to the server
			files = glob.glob1(filename, "*.txt")
			#print(files)
			f = open(os.path.join(filename, files[0]), 'r')
			text = f.read().strip()
			f.close()
			sNLP = StanfordNLP()
			answer = sNLP.annotate(text)
			#now write the answer to an output file
			if not os.path.exists(outpath):
				os.makedirs(outpath)
			fname = files[0] + '.xml'
			f = open(os.path.join(outpath, fname), 'w')
			f.write(answer)
			f.close()
			#command2 = java_exec + ' -Xmx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,parse,depparse -file ' + filename + ' -outputDirectory ' + outpath + ' -outputFormat xml'
			#os.system(command2)

