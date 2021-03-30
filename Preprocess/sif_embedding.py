import sys
sys.path.append('src')
import data_io, SIF_embedding_lib
#import data_io, params, SIF_embedding
from lib_preprocessing import getRealName


def SIF_master(segfile,cleanfile,directory,summ_ind):
	print ("segfile: ", segfile)
	print ("clean file: ", cleanfile)
	#cleanfile = cleanfile+".ls"
	class params(object):
	    def __init__(self):
	        self.LW = 1e-5
	        self.LC = 1e-5
	        self.eta = 0.05
	    def __str__(self):
	        t = "LW", self.LW, ", LC", self.LC, ", eta", self.eta
	        t = map(str, t)
	        return ' '.join(t)

	# input
	wordfile = 'glove.6B.100d.txt' # word vector file, can be downloaded from GloVe website
	weightfile = 'enwiki_vocab_min200.txt' # each line is a word and its frequency
	weightpara = 1e-3 # the parameter in the SIF weighting scheme, usually in the range [3e-5, 3e-3]
	rmpc = 1 # number of principal components to remove in SIF weighting scheme
	#sentiment_file = '../data/sentiment-test' # sentiment data file
	#cleanfile = "2/D1026-A.M.100.E.10.segs.cl"
	#sentiment_file = '../data/clean-5.txt'
	# load word vectors
	(words, We) = data_io.getWordmap(wordfile)
	# load word weights
	word2weight = data_io.getWordWeight(weightfile, weightpara) # word2weight['str'] is the weight for the word 'str'
	weight4ind = data_io.getWeight(words, word2weight) # weight4ind[i] is the weight for the i-th word
	# load sentences (here use sentiment data as an example)
	#x, m, _ = data_io.sentiment2idx(sentiment_file, words) # x is the array of word indices, m is the binary mask indicating whether there is a word in that location
	x, m = data_io.sentiment2idx(cleanfile, words)
	w = data_io.seq2weight(x, m, weight4ind) # get word weights
	# parameters
	params = params()
	#params = params.params()
	params.rmpc = rmpc

	# get SIF embedding
	embedding = SIF_embedding_lib.SIF_embedding(We, x, w, params) # embedding[i,:] is the embedding for sentence i
	#segfile = segfile+".segs"
	f = open(segfile).readlines()
	indexes = []
	matches = []
	for item in f:
		ind = item.rfind("&")
		indexes.append(item[:ind+1])

	if len(indexes) == len(embedding):
		for ind in range(0,len(indexes)):
			lines = indexes[ind]+str(list(embedding[ind]))
			matches.append(lines)
	else:
		print ("length doesn't match!! Check if there is empty line!!")

	#fname = directory +'/'+str(summ_ind)+ '/' + getRealName(segfile) + '.ls'
	#fname = directory +'/'+str(summ_ind)+ '/' + segfile + '.ls'
	fname = directory +'/'+str(summ_ind)+ '/' +getRealName(segfile)
	print (fname)
	with open(fname+".ls", "w") as file:
		for item in matches:
			file.write(item+"\n")


	return embedding 

#def match_vectors(embedding, segfile):

def vectorize_sif(filename):
	class params(object):
	    def __init__(self):
	        self.LW = 1e-5
	        self.LC = 1e-5
	        self.eta = 0.05
	    def __str__(self):
	        t = "LW", self.LW, ", LC", self.LC, ", eta", self.eta
	        t = map(str, t)
	        return ' '.join(t)

	# input
	wordfile = 'glove.6B.100d.txt' # word vector file, can be downloaded from GloVe website
	weightfile = 'enwiki_vocab_min200.txt' # each line is a word and its frequency
	weightpara = 1e-3 # the parameter in the SIF weighting scheme, usually in the range [3e-5, 3e-3]
	rmpc = 1 # number of principal components to remove in SIF weighting scheme
	#sentiment_file = '../data/sentiment-test' # sentiment data file
	#cleanfile = "2/D1026-A.M.100.E.10.segs.cl"
	#sentiment_file = '../data/clean-5.txt'
	# load word vectors
	(words, We) = data_io.getWordmap(wordfile)
	# load word weights
	word2weight = data_io.getWordWeight(weightfile, weightpara) # word2weight['str'] is the weight for the word 'str'
	weight4ind = data_io.getWeight(words, word2weight) # weight4ind[i] is the weight for the i-th word
	# load sentences (here use sentiment data as an example)
	#x, m, _ = data_io.sentiment2idx(sentiment_file, words) # x is the array of word indices, m is the binary mask indicating whether there is a word in that location
	x, m = data_io.sentiment2idx(filename, words)
	w = data_io.seq2weight(x, m, weight4ind) # get word weights
	# parameters
	params = params()
	#params = params.params()
	params.rmpc = rmpc

	# get SIF embedding
	embedding = SIF_embedding_lib.SIF_embedding(We, x, w, params) # embedding[i,:] is the embedding for sentence i


	return embedding 




