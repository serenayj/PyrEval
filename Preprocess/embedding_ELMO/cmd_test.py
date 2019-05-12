import sys
sys.path.append('src')
import data_io, SIF_embedding_lib
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
#word2weight = data_io.getWordWeight(weightfile, weightpara) # word2weight['str'] is the weight for the word 'str'
#weight4ind = data_io.getWeight(words, word2weight)
filename = "test.txt"
word2weight = data_io.getWordWeight(weightfile, weightpara) # word2weight['str'] is the weight for the word 'str'
weight4ind = data_io.getWeight(words, word2weight) # weight4ind[i] is the weight for the i-th word
# load sentences (here use sentiment data as an example)
#x, m, _ = data_io.sentiment2idx(sentiment_file, words) # x is the array of word indices, m is the binary mask indicating whether there is a word in that location
x, m = data_io.sentiment2idx(filename, words)