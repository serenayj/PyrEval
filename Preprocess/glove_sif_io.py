"""
Glove and SIF for generating sentence vectors 
Input: *.clean from sts 
Output: *_glove.ls 
"""
from sif_embedding import vectorize_sif
import sys

def glove(filename):
	clean_text_path = filename
	out_ls_path= clean_text_path.rsplit('.',1)[0]+".ls"
	#print (out_ls_path)
	vecs = vectorize_sif(clean_text_path) 
	tags_file = clean_text_path.rsplit('.',1)[0]+'.segs'
	tags = []
	with open(tags_file) as f:
		for line in f.readlines():
			tags.append(line.rsplit('&',1)[0])

	with open(out_ls_path,'w') as f:
		for n,vec in enumerate(vecs):
			f.write(tags[n]+'&'+str(vec.tolist())+'\n')


