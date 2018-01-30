import scipy.io as sio
import numpy as np
import string
import re
import os
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer

# Initialize Objects
stemmer = SnowballStemmer("english")

# Initialize PATHs
model = 'ormf/models/train100/model.mat'
vocab = 'ormf/models/train100/vocab'
idf = 'ormf/models/train100/idf'


# Read in Vocab File, return dictionary {key=word, value=index}
def readVocab(vocab_file):
	vocab = {}
	with open(vocab_file, 'r') as v:
		for word_ind in v:
			word_ind = word_ind.replace('\n', '').split('\t')
			vocab[word_ind[0]] = int(word_ind[1])
	return vocab

# Read in IDF File, return dictionary {key=index, value=idf}
def readIDF(idf_file):
	idf = {}
	with open(idf_file, 'r') as v:
		for ind_idf in v:
			ind_idf = ind_idf.replace('\n', '').split()
			idf[int(ind_idf[0])] = float(ind_idf[1])
	return idf


class Segment():
	def __init__(self, segmentID, segment):
		self.segmentID = segmentID
		self.segment = self.__preprocess__(segment)
		self.vector = []
	def getSegmentID(self):
		return self.segmentID
	def getSegment(self):
		return self.segment
	def getWordIndices(self):
		segment = self.segment.split(' ')
		indices = []
		for word in segment:
			try:
				indices.append(vocab[word])
			except KeyError:
				pass
		return sorted(list(set(indices))) # Sorted list of indices for the words in the segment
	def getIDF(self):
		indices = self.getWordIndices()
		ind_idf = {}
		for index in indices:
			try:
				ind_idf[index] = idf[index]
			except KeyError:
				pass
		tuples = sorted(ind_idf.items(), key=lambda x: x[0])
		return [t[1] for t in tuples] # List, sorted by index value, of idf scores for words in segment
	def getIndexIDF_format(self):
		indices = self.getWordIndices()
		idfs = self.getIDF()
		return map(lambda ind, idf: [ind, idf], indices, idfs)
	def setVector(self, vector):
		self.vector = vector
	def __preprocess__(self, segment):
		exclude = re.compile('[%s]' % re.escape(string.punctuation))
		segment = exclude.sub('', segment)
		return self.__stemSegment__(self.__tokenizeSegment__(segment))
	def __tokenizeSegment__(self, segment):
		tokenizedSegment = word_tokenize(segment)
		return tokenizedSegment
	def __stemSegment__(self, tokenizedSegment):
		stemmedSegment = [stemmer.stem(word) for word in tokenizedSegment]
		return ' '.join(stemmedSegment)


class SegmentSet():
	def __init__(self, fname):
		self.segments = self.__readFile__(fname)
	def __readFile__(self, fname):
		segments = []
		with open(fname, 'r') as f:
			for line in f:
				segmentID, segment = self.__splitSegment__(line)
				segments.append(Segment(segmentID, segment))
		return segments
	def __splitSegment__(self,line):
		line = line.split('&')
		segmentID = '&'.join(line[:4])
		try:
			segment = line[4]
		except IndexError:
			segment = line[0]
		return segmentID, segment
	def __getitem__(self, ind):
		return self.segments[ind]
	def setVectors(self, model):
		lam_identity = np.identity(model.dimension)*model.lam # identity matrix with diagonal values equal to model.lam
		for j, segment in enumerate(self.segments):
			cols = [index - 1 for index in segment.getWordIndices()] # get all of the word indices to index the word vectors
			vals = np.array(segment.getIDF())	# get all of the idf scores for each word
			pv = model.p[:, cols]	# pv is a matrix of word vectors
			pv_dot = np.matmul(pv, pv.transpose())*(1-model.w_m)
			num = model.pptw_w_m + pv_dot + lam_identity
			den = (np.matmul(pv, vals))
			segment.setVector(np.linalg.lstsq(num, den)[0])

class Model():
	def __init__(self, model):
		self.model = sio.loadmat(model)
		self.p = self.model['P']
		self.w_m = self.model['w_m'][0][0]
		self.lam = self.model['lambda'][0][0]
		self.vars = sio.whosmat(model)
		self.dimension = list(self.vars[5][1])[0]
		self.pptw_w_m = self.__pptw_x_w_m__()
	def __pptw__(self):
		p = self.p
		return p.dot(p.transpose())
	def __pptw_x_w_m__(self):
		w_m = self.w_m
		pptw = self.__pptw__()
		return pptw * w_m


cwd = "../Preprocess/"
#cwd = '/Users/andrewwarner/Developer/NLP/testing_package/PyrEval/Preprocess'
vocab = readVocab(cwd+vocab)
idf = readIDF(cwd+idf)
model = Model(cwd+model)








