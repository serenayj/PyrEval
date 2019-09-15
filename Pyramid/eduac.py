"""
This is pipeline for running EDUA-C

Full DFS 
"""

from lib_eduac import readFiles, make_segs, pairwise, pairwise_test,power_law
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from time import time
import copy
import glob
import itertools
import xml.etree.cElementTree as ET
from graph import _BigGraph, ConnectedComponents, _ClassifyGraphs, _Cliquelist, Select_SubGraph, break_cliques, Hierarchy, candidate_grpahs, make_layer1,ConflictGraph,ConflictSegTable,Checkpoint, AdjancencyMatrix
#from dfs import dfs_search, Top_k, DFS_Driver
from dfs_search import *
import sys 
from nltk import sent_tokenize
import cProfile 
#from graph import * 
"""
=========================== Pipeline =================================
""" 

#fname = "D614"
#sum_dir = sys.argv[1]

#topic = sum_dir[sum_dir.rfind("/")+1:]
N = 4
k = 10


#directories = list(glob.iglob(sum_dir+'/Preprocess/wise_crowd_summaries/*'))
#segs, vecs, N = readFiles(directories)
directories = list(glob.iglob('../Preprocess/wise_crowd_summaries/*'))


segs, vecs, N = readFiles(directories)
#print("Making Segments")
segpool = make_segs(segs, vecs)
#pairwise_test(segpool, N)
#fname = "0925B"

threshold = 83

fname = "eduac"

# For Demo 
print "========= This is a brand new core for PyrEval =========== "

segmentpool = copy.deepcopy(segpool)
segmentpool_length = len(segmentpool)
        
# For checking if the segment is used 
hitlist = [] 

# Build Pairwise Similarity Set
BigSet2 = pairwise(segmentpool, N, threshold)

# Build global graph 
g = _BigGraph(BigSet2)
cliques = ConnectedComponents(g)
graphlist = _Cliquelist(cliques,g,segmentpool)

# New graphs: break down existing graphs into candidate layer 
cand_graphs = candidate_grpahs(graphlist,N,g)

# Top N-1 layers split point 
check_point = Checkpoint(graphlist,N)

# Before DFS, build a big table for all conflict CUs 
segtable = ConflictSegTable(segmentpool)
cu_table,cu_combos = ConflictGraph(cand_graphs,segtable)

Pyramid = range(N)
Pyramid_info = range(N)

# for n in range(1,N+1):
# 	#y_n = power_law(n, bf_dict)
# 	Pyramid_info[n-1] = y_n

print "Pyramid shapes, from 1 to ", N, " ", Pyramid_info
timer = time()
print "<============== Start DFS ==============> ", time()

adj_matrix = AdjancencyMatrix(cand_graphs,cu_table)
#should be len(cand_graphs-1)   
# Global info about which node is visited 
nodelist = range(len(cand_graphs)-1)

Check = check_point[N-1] + check_point[N]
# Meaning if there are things located in top 2 layers 

if Check > 0:
	# start from 0 
	paths = {}
	for start in range(0,Check):
		path,WAS = Modified_dfs(adj_matrix, start,cand_graphs,cu_table)
		paths[start] =[path,WAS]

done = time()
print('Time: {}'.format(str(done - timer)))


#==============Layer 1=================
#final_selection = max(paths, key = lambda x: paths[x][1][1])
# Return an index
final_selection = sorted(paths,key = lambda x:paths[x][1], reverse =  True)[0]


final = []
for i in paths[final_selection][0]:
#for i in range(0,len(final_selection[0])):
	#if final_selection[0][i] == 1:
	final.append(cand_graphs[i])

#===============Format Output===========
scu_len = len(final)
# Extract segments 
SCUs = {}
for index in range(0,scu_len):
	item = final[index]
	scu_len = len(item.members)
	scu_label  = []
	for ind in range(0,scu_len):
		curr_id = item.members[ind]
		curr_seg = segmentpool[curr_id]
		seg_label = curr_seg.seg 
		scu_label.append(seg_label)
	SCUs[index] = scu_label
	
layer1, layer1id = make_layer1(segmentpool,final)

#for ind in range(9,16):
total_length = len(final)+len(layer1)
init_len = len(final)
for ind in range(init_len,total_length):
	#print "ind", ind 
	iind = ind - init_len
	#print "iind,", iind 
	SCUs[ind] = sent_tokenize(layer1[iind])

Pyramid_size = {}
for k,v in SCUs.items():
	weight = len(v)
	if Pyramid_size.has_key(weight):
		Pyramid_size[weight] += 1 
	else:
		Pyramid_size[weight] = 1 


with open("../Scoring/scu/"+fname+"-readable.pyr",'w') as f:
	for k,v in enumerate(SCUs):
		labels = SCUs[k]
		for ind in range(0,len(labels)):
			line = 'SCU' + '\t' + str(k) + '\t' + str(len(labels)) + '\t' + labels[ind]+'\n'
			f.write(line)


root = ET.Element('Pyramid')
p = 0
#scu = ET.SubElement(root,'scu', uid=str(p))
for j, i in enumerate(SCUs):
	#print j, i
	#if i > p:
	p = i
	scu = ET.SubElement(root,'scu', uid=str(p))
	for ele in range(0,len(SCUs[j])):
		ET.SubElement(scu, 'contributor', label = SCUs[j][ele])

tree = ET.ElementTree(root)
tree.write("../Scoring/pyrs/pyramids/"+fname + '.pyr')
#tree.write("../Scoring/EDUAC-10/"+fname + '.pyr')

with open('../Scoring/sizes/' + fname + '.size', 'w') as f:
	for n,pyr in enumerate(Pyramid_size):
		f.write(str(Pyramid_size[pyr]) + "\n")








