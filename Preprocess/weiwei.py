""" Weighted Orthogonal Matrix Factorization """

import os
system = os.system
import sys
sys.path.append('ormf/')
from ormf.test_ormf import getVectorization

def preProcessText(text, MODEL):
	cmd = 'perl ormf/bin/test.pl %s %s' % (MODEL, text)
	print(cmd)
	system(cmd)
	fname = text + '.ind'
	return fname

def vectorize(text):
	MODEL = 'ormf/models/train100'
	text_ind = preProcessText(text, MODEL)
	Model = MODEL + '/model.mat'
	vectors = getVectorization(text_ind, Model)
	return vectors



