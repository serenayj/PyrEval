from nltk import sent_tokenize,word_tokenize
import re
import os
import glob 
import sys


inpath = sys.argv[1]
outpath = sys.argv[2]

def stemming(text): 
	#dic = enchant.Dict("en_US")
	text = text.decode("utf-8","ignore")
	tokens = nltk.word_tokenize(text) 
	stems = []
	for item in tokens: 
		stems.append(en.lemma(item.lower()))
	data = " ".join(stems)
	#print "After stemming, take a look at the data---->\n: ",data
	#print "<--------"		
	return data 	#after return, the program won't go down

def removesymbols(text):
	tmp = []
	print "now start to remove symbols! "
	result = ''.join([i for i in text if not i.isdigit()])
	rmv0 = re.findall(r"[\w!,.:;']+",result)
	ele = ' '.join(rmv0)
	return ele

for filename in glob.glob(os.path.join(inpath,"*.txt")):
	content = open(filename).read()
	content = removesymbols(content)
	sent_list = sent_tokenize(content)
	slash = filename.rfind('/')
	fn = outpath+filename[slash:]
	with open(fn,'wb') as wf:
		for i in sent_list:
			wf.write(i+'\n')





