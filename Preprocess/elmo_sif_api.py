from __future__ import print_function
import sys
from SIF_embedding_lib import *
import csv 
from allennlp.commands.elmo import ElmoEmbedder
from nltk import word_tokenize
import numpy as np
import pickle
#from tree import tree
from sklearn import tree

weightfile = 'commoncrawl2012_00_19_vocab.txt'

def prepare_data(list_of_seqs):
    lengths = [len(s) for s in list_of_seqs]
    n_samples = len(list_of_seqs)
    maxlen = np.max(lengths)
    x = np.zeros((n_samples, maxlen)).astype('int32')
    x_mask = np.zeros((n_samples, maxlen)).astype('float32')
    for idx, s in enumerate(list_of_seqs):
        x[idx, :lengths[idx]] = s
        x_mask[idx, :lengths[idx]] = 1.
    x_mask = np.asarray(x_mask, dtype='float32')
    return x, x_mask


def getSeq(p1,words):
    p1 = p1.split()
    X1 = []
    for i in p1:
        X1.append(lookupIDX(words,i))
    return X1

def lookupIDX(words,w):
    w = w.lower()
    if len(w) > 1 and w[0] == '#':
        w = w.replace("#","")
    if w in words:
        return words[w]
    elif 'UUUNKKK' in words:
        return words['UUUNKKK']
    else:
        return len(words) - 1


def seq2weight(seq, mask, weight4ind):
    weight = np.zeros(seq.shape).astype('float32')
    for i in range(seq.shape[0]):
        for j in range(seq.shape[1]):
            if mask[i,j] > 0 and seq[i,j] >= 0:
                weight[i,j] = weight4ind[seq[i,j]]
    weight = np.asarray(weight, dtype='float32')
    return weight

def getWordmap(textfile):
    words={}
    We = []
    f = open(textfile,'r')
    lines = f.readlines()
    for (n,i) in enumerate(lines):
        i=i.split()
        j = 1
        v = []
        while j < len(i):
            v.append(float(i[j]))
            j += 1
        words[i[0]]=n
        We.append(v)
    return (words, np.array(We))


def sentiment2idx(sentiment_file, words):
    """
    Read sentiment data file, output array of word indices that can be fed into the algorithms.
    :param sentiment_file: file name
    :param words: a dictionary, words['str'] is the indices of the word 'str'
    :return: x1, m1, golds. x1[i, :] is the word indices in sentence i, m1[i,:] is the mask for sentence i (0 means no word at the location), golds[i] is the label (0 or 1) for sentence i.
    """
    f = open(sentiment_file,'r')
    lines = f.readlines()
    golds = []
    seq1 = []
    #print("first line in %s" % sentiment_file)
    #print(lines[0])
    #count = 0
    for i in lines:
        i = i.split("\t")
        #p1 = i[0]; score = int(i[1]) # score are labels 0 and 1
        p1 = i[0]
        X1 = getSeq(p1,words)
        #if count == 0:
        #    out_of_vocab = [out for out in p1.split() if out not in words]
        #    print(out_of_vocab)
        #    print(float(len(out_of_vocab))/ len(p1.split()))
        #count = count + 1

        seq1.append(X1)
        #golds.append(score)
    x1,m1 = prepare_data(seq1)
    return x1,m1 

def getWordWeight(weightfile, a=1e-3):
    if a <=0: # when the parameter makes no sense, use unweighted
        a = 1.0

    word2weight = {}
    with open(weightfile) as f:
        lines = f.readlines()
    N = 0
    for i in lines:
        i=i.strip()
        if(len(i) > 0):
            i=i.split()
            if(len(i) == 2):
                word2weight[i[0]] = float(i[1])
                N += float(i[1])
            else:
                print(i)
    for key, value in word2weight.items():
        word2weight[key] = a / (a + value/N) # By Yanjun: where it applies a/(a+p(w))
    return word2weight

def getWeight(words, word2weight):
    weight4ind = {}
    for word, ind in words.items():
        if word in word2weight:
            weight4ind[ind] = word2weight[word]
        else:
            weight4ind[ind] = 1.0
    return weight4ind



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

	def MakeELMOEmbedding(self, cleanfile, params):
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



