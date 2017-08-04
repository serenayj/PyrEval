""" Weighted Orthogonal Matrix Factorization """

import os
system = os.system
import sys
sys.path.append('weiwei/')
from test_ormf import getVectorization

def preProcessText(text, MODEL):
	cmd = 'perl weiwei/bin/test.pl %s %s' % (MODEL, text)
	print(cmd)
	system(cmd)
	fname = text + '.ind'
	return fname

def vectorize(text):
	MODEL = 'weiwei/models/train100'
	text_ind = preProcessText(text, MODEL)
	Model = MODEL + '/model.mat'
	vectors = getVectorization(text_ind, Model)
	return vectors



