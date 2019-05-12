import sys
sys.path.append('src')
import new_data_io, SIF_embedding_lib
import csv 
from allennlp.commands.elmo import ElmoEmbedder
from nltk import word_tokenize
import numpy as np

""" This area should be placed in the main call """
elmo = ElmoEmbedder()

class params(object):
    def __init__(self):
        self.LW = 1e-5
        self.LC = 1e-5
        self.eta = 0.05
    def __str__(self):
        t = "LW", self.LW, ", LC", self.LC, ", eta", self.eta
        t = map(str, t)
        return ' '.join(t)

class ELMO_SIF_master(object):
	def __init__(self):
		self.wordfile = 'glove.6B.100d.txt' # word vector file, can be downloaded from GloVe website
		self.weightfile = 'enwiki_vocab_min200.txt'

	def Initialization(self):
		(self.words, self.We) = new_data_io.getWordmap(self.wordfile)
		self.weightpara = 1e-3
		self.word2weight = new_data_io.getWordWeight(self.weightfile, self.weightpara) # word2weight['str'] is the weight for the word 'str'
		self.weight4ind = new_data_io.getWeight(self.words, self.word2weight)

	def MakeELMOEmbedding(self, cleanfile, params)
		x,m = new_data_io.sentiment2idx(cleanfile, self.words)
		w = new_data_io.seq2weight(x, m, self.weight4ind)
		rmpc = 1
		#params = params()	
		params.rmpc = rmpc
		""" where the function call should start """
		lines = open(cleanfile).readlines()
		newline = [l.strip("\n") for l in lines]
		allembs = [] 
		for l in newline:
			ind = newline.index(l)
			wlst = word_tokenize(l.lower())
			#We = {}
			emb = elmo.embed_sentence(wlst)
			newemb = np.mean(emb,axis=0)
			#for w in wlst:
			embedding = SIF_embedding_lib.SIF_embedding(newemb, x[ind], w[ind], params)
			allembs.append(embedding)
		return allembs



