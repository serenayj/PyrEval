import os
import glob
import sys
from lib_preprocessing import getRealName, CleanSegmentations, VectorizeSummary, DecomposeSummary, getRoot
mode = sys.argv[1]

#mode = 1

"""
=============== MAIN ===================
"""


#summaries = [sys.argv[1]]
peer_summaries = []
wise_crowd = []
test_summaries = []

error_file = '../Preprocess/errors-file.txt'
errors = [] 
if int(mode) == 1:
	dir1 = "../Preprocess/peer_summaries"
elif int(mode) == 2:
	dir1 = "../Preprocess/wise_crowd_summaries"
#elif int(mode) == 3:
	#dir1 = "../Preprocess/test_summaries"
else:
	dir1 = None
	print "Option doesn't exist!!!"

if (dir1):
	summaries = sorted(list(glob.iglob(dir1+ '/*.xml')))
	for n, summary in enumerate(summaries):
		try:
			DecomposeSummary(summary, n + 1,dir1)
			summary, seg_ids = CleanSegmentations(summary, dir1,n+1)
			VectorizeSummary(summary, seg_ids, dir1,n+1)
		except:
			print "current file failed: ", n, " ", summary
			errors.append(summary)
	
	with open(error_file,'w') as f:
		for each in errors:
			f.write(each)

#if int(mode) ==2:
#	command = 'mv ../Preprocess/wise_crowd_summaries ../Pyramid/wise_crowd'
#	os.system(command)

print "Finish Preprocess!!!"
