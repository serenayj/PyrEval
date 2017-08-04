import os
import glob
import sys
from lib_preprocessing import getRealName, CoreNLPdecomposition, CleanSegmentations, VectorizeSummary, DecomposeSummary, getRoot
dir1 = sys.argv[1]

"""
=============== MAIN ===================
"""

summaries = list(glob.iglob(dir1+ '/*'))
#summaries = [sys.argv[1]]
peer_summaries = []
wise_crowd = []
test_summaries = []

for n, summary in enumerate(summaries):
	d = os.path.dirname(summary)
	slash = d.rfind('/')
	d = d[slash + 1:]
	print d
	if d == 'peer_summaries':
		peer_summaries.append(summary)
	elif d == 'wise_crowd_summaries':
		wise_crowd.append(summary)
	elif d == 'test_summaries':
		test_summaries.append(summary)
	mkdir = 'mkdir ' + 'DecomposedSummaries/' + getRealName(summary)
	os.system(mkdir)
	directory = 'DecomposedSummaries/' + getRealName(summary)
	CoreNLPdecomposition(summary)
	summary = 'CoreNLP_XMLs/' + getRoot(summary)
	DecomposeSummary(summary, n + 1)
	summary, seg_ids = CleanSegmentations(summary, directory)
	VectorizeSummary(summary, seg_ids, directory)

for summary in peer_summaries:
	to_move = 'DecomposedSummaries/' + getRealName(summary) + '/' + getRealName(summary) + '.ls'
	mv = 'mv ' + to_move + ' ../Processing/peer_summaries'
	print(mv)
	os.system(mv)
for summary in wise_crowd:
	to_move = 'DecomposedSummaries/' + getRealName(summary)
	mv = 'mv ' + to_move + ' ../Pyramid/wise_crowd'
	print(mv)
	os.system(mv)
for summary in test_summaries:
	to_move = 'DecomposedSummaries/' + getRealName(summary) + '/' + getRealName(summary) + '.ls'
	mv = 'mv ' + to_move + ' ../Processing/test_summaries'
	print(mv)
	os.system(mv)