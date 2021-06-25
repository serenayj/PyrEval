#Preprocessing xml files from stanford corenlp 
#Copyright (C) 2017  Yanjun Gao

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import glob
import sys
from time import time
from lib_preprocessing import *

#Wasih (02-21-20) Use termcolor to display colored text; user friendly
from termcolor import colored

mode = sys.argv[1]

#mode = 2

"""
=============== MAIN ===================
"""

#Wasih (06-20-21) Read vectorization method from parameters file
PYTHON_VERSION = 2
if sys.version_info[0] == 2:
	import ConfigParser as configparser
else:
	import configparser
	PYTHON_VERSION = 3

config = configparser.ConfigParser()
config.read('../parameters.ini')
#Wasih (06-25-21) Read segmentation method from parameters file
segmentation_method = config.get('Segmentation', 'Method')
vector_method = config.get('Vectorization', 'Method')

#summaries = [sys.argv[1]]
peer_summaries = []
wise_crowd = []
test_summaries = []
timer = time()

error_file = '../Preprocess/errors-file.txt'
errors = [] 
#Wasih (02-19-20) Use functions instead of calling script (mode is already integer)
if int(mode) == 1:
	dir1 = "../Preprocess/peer_summaries"
elif int(mode) == 2:
	dir1 = "../Preprocess/wise_crowd_summaries"
#elif int(mode) == 3:
	#dir1 = "../Preprocess/test_summaries"
else:
	dir1 = None
	print ("Option doesn't exist!!!")

if (dir1):
	summaries = sorted(list(glob.iglob(dir1 + '/*.xml')))
	for n, summary in enumerate(summaries):
		#try:
		DecomposeSummary(summary, n + 1, dir1, segmentation_method)
		#summary, seg_ids = CleanSegmentations(summary, dir1,n+1)
		VectorizeSummary(summary, dir1, n + 1, 'preprocess', vector_method)
		#except:
		#	print "current file failed: ", n, " ", summary
		#	errors.append(summary)
	
	#with open(error_file,'w') as f:
	#	for each in errors:
	#		f.write(each)
done = time()

text = colored(('Time: {}'.format(str(done - timer))), 'blue')
print (text)
#print('Time: {}'.format(str(done - timer)))

#if int(mode) ==2:
#	command = 'mv ../Preprocess/wise_crowd_summaries ../Pyramid/wise_crowd'
#	os.system(command)

