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

cleanfile = "test.txt"
wordfile = 'glove.6B.100d.txt' # word vector file, can be downloaded from GloVe website
weightfile = 'enwiki_vocab_min200.txt'

(words, We) = new_data_io.getWordmap(wordfile)
weightpara = 1e-3
word2weight = new_data_io.getWordWeight(weightfile, weightpara) # word2weight['str'] is the weight for the word 'str'
weight4ind = new_data_io.getWeight(words, word2weight)
x, m = new_data_io.sentiment2idx(cleanfile, words)
w = new_data_io.seq2weight(x, m, weight4ind)

rmpc = 1
params = params()
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