### This script is for building all graph operations, data structure 
### Author: Yanjun Gao
### Last update: Oct.11, 2017 
### Todo: build adjancency list(possibly linked list) for nodes representation 
### Todo: Design a DFS algorithm for clique decision making 


import networkx as nx
import copy
import math
from itertools import combinations
from sklearn.metrics.pairwise import cosine_similarity as cos
import numpy as np
import os
import glob
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import itertools


"""
=================================== Generate all required components ============================
"""

# Need an adjacency list telling you which sentence is connected 
# Like a path, head is the first node in the list 
class _Path:
	def __init__(self, adjlist,head):
		self.head = head 
		self.path = adjlist  

# Defining the node in adjcency list
"""
class _AdjListNode:
 	def __init__(self, x):
        self.val = x
        self.next = None
"""

# Assuming getting the BigSet2 from previous 
# Build a big graph  
def _BigGraph(BigSet2):
	g = nx.Graph()
	for item in BigSet2:
		node1 = item['seg1id']
		node2 = item['seg2id']
		#aa = float(math.exp(item['WAS']))
		aa  = float(item['WAS'])
		g.add_edge(node1,node2, weight = aa)
	return g 

# Find all complete subgraphs
def ConnectedComponents(G):
	cliques = sorted(list(nx.find_cliques(G)))
	return cliques

class _CU:
	def __init__(self,clique):
		self.valid = True 
		self.members = clique
		self.weight = len(clique)
		self.WAS = 0
		self.commit = False
		#self.visited = False  
	# Check constraints: no two segments from the same document could be placed in a subgraph
	def ValidateSubGraph(self,segmentpool):
		valid_flag = True 
		lst = self.members 
		for i in range(0,len(lst)-1):
			for j in range(i+1,len(lst)):
				first = lst[i]
				second = lst[j]
				if (segmentpool[first].docid != segmentpool[second].docid):
					pass
				else:
					valid_flag = False 
		self.valid = valid_flag

# Temporarily using unscaled WAS 
def Update_WAS(clique,g):
	WAS = 0
	for i in range(0,len(clique)-1):
		for j in range(i+1,len(clique)):
			#print clique[i]," ", clique[j], " ", g[clique[i]][clique[j]]['weight']
			WAS += g[clique[i]][clique[j]]['weight']
	return WAS 

# Class or List/Dict? Which consumes less memory? 
def _Cliquelist(cliques,g,segmentpool):
	result = []
	for item in cliques:
		new = _CU(item)
		new.WAS = Update_WAS(item,g)
		new.ValidateSubGraph(segmentpool)
		if new.valid == True:
			result.append(new)
		else:
			pass
	# SORT LIST BY WAS 
	result = sorted(result, key=lambda x: x.WAS, reverse=True)
	return result 

# See how many candidate cliques in given n layer 
def _ClassifyGraphs(graphlist,n):
	# n is the layer 
	count = 0 
	for sub in graphlist:
		if len(sub.members) == n:
			count += 1
	return count 

#def SplitLayers(graphlist,n):


def Checkpoint(graphlist,N):
	positions = {}
	prev = 0
	# Layer index
	layer = range(2,N+1)
	# ind is the index of layer s
	for ind in reversed(layer):
		curr = _ClassifyGraphs(graphlist,ind)
		positions[ind]=prev+curr
		prev += curr 
	return positions

# Conflict info for segments
# Return is a conlifct seg table
def ConflictSegTable(segmentpool):
	all_segs = []
	for k,v in enumerate(segmentpool):
		if v not in all_segs:
			all_segs.append(v)
	all_combos = itertools.combinations(all_segs,2)

	conflict_seg = {}
	for item in all_combos:
		seg1 = item[0]
		seg2 = item[1]
		# Same sentence, different segmentation
		if (seg1.split('.')[0] == seg2.split('.')[0]) and (seg1.split('.')[1] == seg2.split('.')[1]) and (seg1.split('.')[2] != seg2.split('.')[2]):
			conflict_seg[item] = True
			#print "conflict,", seg1, seg2
		# Same segmentation, same segment
		elif (seg1.split('.')[0] == seg2.split('.')[0]) and (seg1.split('.')[1] == seg2.split('.')[1]) and (seg1.split('.')[2] == seg2.split('.')[2]) and (seg1.split('.')[3] == seg2.split('.')[3]):
			conflict_seg[item] = True
			#print "conflict,", seg1, seg2
		# The only case that is legal: same segmentation, different segment 
		else:
			conflict_seg[item] = False
	return conflict_seg

# Conflict info for CUs, input is the graphlist and output of ConflictSegTable
# Return is a conflict CU table 
def ConflictGraph(graphlist,segtable):
	cu_table = {}
	# indexing CU by their position 
	cu_pos = [i for i in xrange(len(graphlist))]
	cu_combos = list(itertools.combinations(cu_pos,2))

	for combo in cu_combos:
		# Default conflict as false 
		flag = False 
		cu1_members = graphlist[combo[0]].members
		cu2_members = graphlist[combo[1]].members
		segs_combo = list(itertools.product(cu1_members,cu2_members))
		for pair in segs_combo:
			# Very first condition: if one segment exists in two CUs, the two CUs are conflicted
			if pair[0] == pair[1]:
				flag = True
			else:
				# if key exists
				if segtable.has_key(pair):
					if segtable[pair] == False:
						continue
					else:
						flag = True
				# Do a simple swap for the keys 
				else:
					temp = pair[0]
					t1 = pair[1]
					pairs = (t1,temp)
					if segtable[pairs] == False:
						pass
					else:
						flag = True
		cu_table[combo] = flag
	return cu_table, cu_combos

"""
======================================= Graph operations ====================================
"""

# Commiting the graph by making every segment in the subgraph used
# And return flag for indicating if it commits successfully 
def CommitSubGraph(subgraph, segmentpool):
	valid_flag = True  
	for each in subgraph.members:
		item = segmentpool[each]
		if item.commit_invalid == False:
			#item.commit_invalid = True 
			pass 
		else:
			valid_flag = False
	if valid_flag == True:
		subgraph.commit = True 
		for each in subgraph.members:
			segmentpool[each].commit_invalid = True 
	return valid_flag 


def Select_SubGraph(candidate, segmentpool, layer, hitlist):
	#hitlist = [] 
	first_check = False
	for subgraph in candidate:
		if len(hitlist) == 0:
			if CommitSubGraph(subgraph,segmentpool) == True:
				hitlist += [i for i in subgraph.members]
				layer.append(subgraph)
		else:
			for each in subgraph.members:
				for j in hitlist:
					# If two segments coming from the same document, and same sentence but not the same segmentation, that is invalid 
					if (segmentpool[each].docid == segmentpool[j].docid) and (segmentpool[each].sentid == segmentpool[j].sentid):
						# Enforcing the rules where only one segmentation could be consumed 
						if segmentpool[each].segtationid != segmentpool[j].segtationid:
							first_check = True 
						else:
							pass
			if first_check == False:
				if CommitSubGraph(subgraph,segmentpool) == True:
					hitlist += [i for i in subgraph.members]
					layer.append(subgraph)


# function for breaking n-nodes clique down to n-1 cliques 
# return is a list 
def break_cliques(n,graphlist,g):
	hit = []
	new_cliques = [] 
	for sub in graphlist:
		if len(sub.members) == n:
			cand = list(combinations(sub.members,n-1))
			for item in cand:
				if item not in hit:
					hit.append(item)
	for j in hit:
		was = Update_WAS(j,g) 
		new = _CU(list(j))
		new.WAS = was
		new_cliques.append(new)
	return new_cliques 

def UpdateNodeWeight(Bigset2, segmentpool):
	#for k,v in segmentpool.items():
	for item in Bigset2:
		was = item["WAS"]
		share = float(was/2)
		i1 = item["seg1id"]
		i2 = item["seg2id"]
		segmentpool[i1].weight += share
		segmentpool[i2].weight += share
	return segmentpool

# input n, return new list of all CUs weighted n-1 
def Hierarchy(newcliques, graphlist, n):
	new = []
	for i in graphlist:
		if len(i.members) == n-1:
			if i not in new:
				new.append(i)
	for j in newcliques:
		if len(j.members) == n-1:
			if j not in new:
				new.append(j)
	return new

def candidate_grpahs(graphlist,N,g):
	cand_graphs = []
	for i in graphlist:
		if len(i.members) == N:
			cand_graphs.append(i)
	# Break the current graphs into new graphs;
	# Take new graph list and run DFS;
	# Only consider Layer 4 to 2; 
	for layer in range(0,N):
		layer_ind = N - layer
		# No need to break down layer 2
		if layer_ind > 2:
			new_graphs = break_cliques(layer_ind,graphlist,g)
			new_graphs = Hierarchy(new_graphs, graphlist, layer_ind)
			cand_graphs.extend(new_graphs)
		else:
			pass
	return cand_graphs

def ConstraintSeg(seg1,seg2):
	s1 = seg1.split(".")
	s2 = seg2.split(".")
	### e.g. '4.2.0.0' and '4.2.1.0'
	if (s1[0] == s2[0]) and (s1[1] == s2[1]) and (s1[2] != s2[2]):
		return False 
	### e.g. '4.2.0.0' and '4.2.0.0'
	elif (s1[0] == s2[0]) and (s1[1] == s2[1]) and (s1[2] == s2[2]) and (s1[3] == s2[3]):
		return False 
	else:
		return True 

# Pick the left over segment as layer1(noises)
def make_layer1(segmentpool,abovelayer):
	hitid = []
	for item in abovelayer:
		hitid.extend(item.members)
	print "all used segments: ", hitid
	for every in hitid:
		t = segmentpool[every]
		t.status = True 

	for everyid in segmentpool:
		seg_canused = segmentpool[everyid]
		for usedid in hitid:
			segused = segmentpool[usedid]
			# Find the segments from same sentence but different segmentations, make it invalid 
			if (seg_canused.docid == segused.docid) and (seg_canused.sentid == segused.sentid) and (seg_canused.segtationid != segused.segtationid):
				seg_canused.commit_invalid = True 
			else:
				pass
	layer1 = []
	layer1_id = [] 
	usedid = []
	for item in segmentpool:
		if (segmentpool[item].commit_invalid == False) and (segmentpool[item].status == False):
			if len(usedid) == 0:
				layer1.append(segmentpool[item].seg) 
				layer1_id.append(segmentpool[item].id)
				segmentpool[item].status = True 
				usedid.append(segmentpool[item].id) 
			else:
				accept = True 
				for each in usedid:
					if ConstraintSeg(each,segmentpool[item].id):
						pass 
					else:
						accept = False 
				if accept:
					usedid.append(segmentpool[item].id)
					layer1.append(segmentpool[item].seg) 
					layer1_id.append(segmentpool[item].id)
					segmentpool[item].status = True  
	return layer1, layer1_id 


def conflict(cu1_ind, cu2_ind,cu_table):
	#print "cu 1 index: ", cu1_ind, " cu 2 index: ", cu2_ind
	flag = False 
	if cu1_ind == cu2_ind:
		flag = True
		return flag
	else:
		pair = (cu1_ind,cu2_ind)
		if cu_table.has_key(pair):
			flag = cu_table[pair]
		else:
			#swap the index
			pair = (cu2_ind,cu1_ind)
			flag = cu_table[pair]		
	return flag 


"""
======================================= Graph DFS for all possible paths ====================================
"""
# Find all candidate cliques 
# Assume candidate is a connected component 
# Checking if it comes from the same summary or same sentence in the summary
def CompatiblePath(subgraph, candidate):
	flag = False 
	for each in subgraph.members:
		for j in candidate.members:
			# If two segments coming from the same document, and same sentence but not the same segmentation, that is invalid 
			if (segmentpool[each].docid != segmentpool[j].docid):
				pass
			elif (segmentpool[each].sentid != segmentpool[j].sentid):
				pass 
			else:
				flag = True 
	return flag 

# Path should be a dictionary  
# Where key is the souce node, item is list of cliques satisfying the constraints, and the final WAS it achieves; 
# Probably need to iterate the whole graph, each node will find a different path. 
# So right now just think about for a given node as source, what it will find. 
def Children(source, graphlist, path):
	visited = {}
	if len(path) == 0:
		path.append(source)
	for item in graphlist:
		#if visited{item} == False:
		# Probably need a recursive way
		if CompatiblePath(every,item):
			path.append(item)
			visited[item] = False 
	return visited 

#def DFS(source, visited, path):

def AdjancencyMatrix(graphlist,cu_table):
	adj_matrix = {}
	for index in range(0,len(graphlist)-1):
		path = [] 
		for cand in range(index+1,len(graphlist)):
			#pairs = [index,cand]
			#if conflict(index,cand,cu_table):
			#	pass
			tups = (index,cand)
			if conflict(index,cand, cu_table):
				pass
			else:
				path.append(cand)
		adj_matrix[index] = path 
	return adj_matrix










