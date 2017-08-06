import os
import glob
import sys
from lib_preprocessing import getRealName, CoreNLPdecomposition, CleanSegmentations, VectorizeSummary, DecomposeSummary, getRoot
#dir1 = sys.argv[1]
mode = sys.argv[1]

"""
=============== MAIN ===================
"""


#summaries = [sys.argv[1]]
peer_summaries = []
wise_crowd = []
test_summaries = []

if int(mode) == 1:
	dir1 = "../Preprocess/peer_summaries"
elif int(mode) == 2:
	dir1 = "../Preprocess/wise_crowd_summaries"
elif int(mode) == 3:
	dir1 = "../Preprocess/test_summaries"
else:
	dir1 = None
	print "Option doesn't exist!!!"

if (dir1):
	summaries = list(glob.iglob(dir1+ '/*.xml'))
	for n, summary in enumerate(summaries):
		DecomposeSummary(summary, n + 1,dir1)
		summary, seg_ids = CleanSegmentations(summary, dir1)
		VectorizeSummary(summary, seg_ids, dir1)

if int(mode) ==2:
	command = 'mv ../Preprocess/wise_crowd_summaries ../Pyramid/wise_crowd'
	os.system(command)

print "Finish Preprocess!!!"
