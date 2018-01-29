""" Weighted Orthogonal Matrix Factorization """

import os
system = os.system
import sys
sys.path.append('ormf/')
from ormf.ormf import model, SegmentSet

# def preProcessText(text, MODEL):
# 	cmd = 'perl ormf/bin/test.pl %s %s' % (MODEL, text)
# 	print(cmd)
# 	system(cmd)
# 	fname = text + '.ind'
# 	return fname

# def vectorize(text):
# 	MODEL = 'ormf/models/train100'
# 	text_ind = preProcessText(text, MODEL)
# 	Model = MODEL + '/model.mat'
# 	vectors = getVectorization(text_ind, Model)
# 	return vectors

format_vector = lambda segment: '%s&%s' % (segment.segmentID, segment.vector.tolist())
def vectorize(text, mode=None):
	segments = SegmentSet(text)
	segments.setVectors(model)
	if mode == 'preprocess':
		return [format_vector(segment) for segment in segments]
	else:
		return [segment.vector.tolist() for segment in segments]




