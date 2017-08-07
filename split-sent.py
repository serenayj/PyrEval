from nltk import sent_tokenize
import os
import glob 
import sys


inpath = sys.argv[1]
outpath = sys.argv[2]

for filename in glob.glob(os.path.join(inpath,"*.txt")):
	content = open(filename).read()
	sent_list = sent_tokenize(content)
	slash = filename.rfind('/')
	fn = outpath+filename[slash:]
	with open(fn,'wb') as wf:
		for i in sent_list:
			wf.write(i+'\n')

