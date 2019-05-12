"""
Package requirement: python >= 3.6, allennlp  
"""
import csv 
from allennlp.commands.elmo import ElmoEmbedder

elmo = ElmoEmbedder()
tokens = ["I", "ate", "an", "apple", "for", "breakfast"]
"""Return is a list of word vectors """
vectors = elmo.embed_sentence(tokens)

wlst = [] 
with open("word_list.csv","r") as f:
	rea = csv.reader(f)
	for l in rea:
		wlst.append(l)

allvecs = elmo.embed_sentence(wlst)
