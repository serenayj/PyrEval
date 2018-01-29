from bs4 import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os


tensed_verb = ['VBZ','VBD','VBP','MD']
#sub_conj = ['after', 'although', 'as', 'because', 'before', 'even','if', 'inasmuch', 'lest', 'now', 'once', 'provided', 'since', 'supposing', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'whereas', 'where if', 'wherever', 'whether', 'which', 'while', 'who', 'whoever', 'why']

wrb = ['WHADJP','WHAVP','WHNP','WHPP']

# Input is a tokens[ind]
def POS_Tags(tokens):
	taglist = {} 
	res = tokens.find_all("token")
	for ind in range(0,len(res)):
		item = res[ind].find("word").get_text()
		tag = res[ind].find("pos").get_text()
		taglist[ind+1] = tag 
		#taglist.append([ind+1,item,tag])
	return taglist

# Possibly need recursion in this step
def Valid_SubClauses(tr, taglist):
	candidate = [] 
	cand_pos = []
	# Step 1: Pull out all SBAR 
	for st in tr.subtrees():
		if st.label() == "SBAR":
			if st not in candidate:
				candidate.append(st)
	# Step 2: Extract the scopes of each valid SBAR 
	valid_sbar = [] 
	for item in candidate:
		# Quick way to extract all leaves in a subtree 
		leaves = item.leaves()
		for node in leaves:
			# Sbar must contain a phrase with tensed verb 
			# Need to check if the key exists
			if taglist.has_key(node[1]):
				if taglist[node[1]] in tensed_verb:
					if leaves not in valid_sbar:
						valid_sbar.append(leaves)
			else:
				pass
	# return lists of leaves or trees? 
	return valid_sbar

# Helper function 
# len(list1) < len(list2) 
# Return a leftover list, and a current segment(cover) 
def Difference(list1, list2):
	diff = list(set(list2)-set(list1))  
	cover = list(set(list1).intersection(set(list2)))
	#print "cover, ", cover
	return diff,cover   

def Find_Words(ids, numlist):
	sent = []
	for item in ids:
		for j in numlist:
			if j[1] == item:
				sent.append(j[0])
	sents = " ".join(sent)
	return sents 

# Process the valid sbar 
def Rule_SBAR(valid_sbar,numlist):
	# Step 1: Pull out each segment
	#valid_sbar.sort(key=len)
	valids = [] 
	for each in valid_sbar:
		ele = [item[1] for item in each]
		valids.append(ele)
	lst2 = [item[1] for item in numlist]
	ind = 0
	segments = []
	valids = sorted(valids,key=len)
	while ind < len(valids):
		#print "current lst2, ", lst2 
		#print "current valids, ", valids[ind]
		lst2,cover = Difference(valids[ind],lst2)
		segments.append(sorted(cover))
		ind += 1
	segments.append(sorted(lst2))
	# Step2: Pull out words from segment 
	ind = 0 
	segt = []
	for seg in segments:
		segt.append(Find_Words(seg, numlist))
	# return segment, and segment id 
	return segt, segments  



