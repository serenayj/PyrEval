import sys
#import data_io, params, SIF_embedding
from lib_preprocessing import getRealName
from embedding_ELMO.elmo_sif_api import * 


def SIF_master(segfile,cleanfile,directory,summ_ind):
	print("segfile: ", segfile)
	print("clean file: ", cleanfile)
	#cleanfile = cleanfile+".ls"
	elmo_engine = ELMO_SIF_master() 
	elmo_engine.Initialization()
	param_engine = params() 
	# get SIF embedding
	embedding = elmo_engine.MakeELMOEmbedding(cleanfile,param_engine) # embedding[i,:] is the embedding for sentence i
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
		print("length doesn't match!! Check if there is empty line!!")
	#fname = directory +'/'+str(summ_ind)+ '/' + getRealName(segfile) + '.ls'
	#fname = directory +'/'+str(summ_ind)+ '/' + segfile + '.ls'
	fname = directory +'/'+str(summ_ind)+ '/' +getRealName(segfile)
	print fname 
	with open(fname+".ls", "w") as file:
		for item in matches:
			file.write(item+"\n")
	print("Write vectors into file successfully {}".format(fname+".ls"))
	#return embedding 