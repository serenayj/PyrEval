import collections 
from operator import itemgetter 
import copy
import pandas as pd


### Check which layer the segment committed to 
def check_problem(segmentpool, Pyramid):
	belongs = collections.defaultdict(list)
	allsegs = [s.id for s in segmentpool]
	for _ in range(len(Pyramid)):
		# Remember: _ is the actual pyramid index minus 1 
		layer = Pyramid[_]
		for item in layer:
			#keys = ['seg%did' % (p + 1) for p in range(_)]
			for s in allsegs:
				if s in item.values():
					# The actual sgment id we are looking for 
					if belongs.has_key(s):
						belongs[s].append(_)
					else:
						belongs[s] = [_]
				else:
					continue 

	### Check if a segment is committed to two different layers 
	problem=[]
	for k,v in belongs.items():
		if len(v) >1:
			problem.append(k)
	if len(problem) > 0:
		return True, problem, belongs
	else:
		return False, [],[]  

def navigate_cu(seg,layer):
	return [i for i in layer if seg in i.values()]

def get_weight(cu):
	return (len(cu)-1)/2 

###
"""
###Two things you will need to check:
1. If the segment commited to two layer, which one should be removed
2. After removing the segset, if the constraint still be satisfied 
"""
# As the cursor 
def detail_check(problem,belongs, Pyramid):
	handle = copy.deepcopy(problem) 
	# Pull out all problematic cus 
	problem_cu = [] 
	for i in handle:
		possibles = belongs[i]
		for p in possibles:
			cu = navigate_cu(i,Pyramid[p])
			if cu in problem_cu:
				pass
			else:
				problem_cu.extend(cu)

	### Sort the list
	newlist = sorted(problem_cu, key=itemgetter('WAS'), reverse = True)

	new = []
	for item in newlist:
		item 
		if item not in new:
			new.append(item)
	return new 


### Test dataset 
### [{'WAS': 1.907953073230801, 'seg1id': '3.3.0.0', 'seg2id': '1.5.0.0', 'seg1': 'Apple and Intel helped launch a tech consortium to create new standards to improve content flow between devices .', 'seg2': 'Apple helped launch a consortium designed to create new standards to improve the flow of content between TVs , computers and other devices .'}, {'seg3id': '1.5.0.0', 'seg1': 'Apple and Intel helped launch a tech consortium to create new standards to improve content flow between devices .', 'seg3': 'Apple helped launch a consortium designed to create new standards to improve the flow of content between TVs , computers and other devices .', 'seg2': 'Software developers are working on programs .', 'seg1id': '3.3.0.0', 'seg2id': '4.3.0.1', 'WAS': 1.2149107272672186}, {'WAS': 1.198613645568453, 'seg1id': '2.5.0.0', 'seg2id': '4.3.0.0', 'seg1': 'The new IMacs will be up to two times faster than the older ones using the G chip .', 'seg2': 'that will run on both the Intel and the older Macs'}, {'seg3id': '3.6.0.0', 'seg1': 'that will run on both the Intel and the older Macs', 'seg3': 'The entire line of Macs will shift to Intel by the end of .', 'seg2': 'that Mac will use', 'seg1id': '4.3.0.0', 'seg2id': '2.4.0.0', 'WAS': 0.9388209935888393}, {'WAS': 0.8432655743275445, 'seg1id': '2.4.0.0', 'seg2id': '3.6.0.0', 'seg1': 'that Mac will use', 'seg2': 'The entire line of Macs will shift to Intel by the end of .'}, {'WAS': 0.7530641109539451, 'seg1id': '4.3.0.1', 'seg2id': '1.6.1.0', 'seg1': 'Software developers are working on programs .', 'seg2': 'Speculation is that Apple plans to introduce a Mac Mini computer home entertainment hub .'}]

def Final_Solutions(new, Pyramid, Pyramid_info):
	solutions = [] 
	for _ in range(len(new)):
		item = new[_]
		#current = ListNode(_)
		sol = [_] 
		weight = get_weight(item)
		keys = ['seg%did' % (p + 1) for p in range(weight)]
		used1 = [item[k] for k in keys]
		#print "current sets of segments navigated: ", used1 
		#WAS = item['WAS']
		for i2 in range(_,len(new)):
			item2 = new[i2]
			weight2 = get_weight(item2)
			keys2 = ['seg%did' % (p + 1) for p in range(weight2)]
			used2 = [item2[k] for k in keys2]
			#print "segment set 2: ", used2 
			if set(used2).intersection(set(used1)):
				continue 
			else:
				used1 = used1+ used2
				#print "current sets of segments: ", used1 
				sol.append(i2)
				#compatibles.append([newlist.index(item),newlist.index(item2),item['WAS']+item2['WAS']])
		solutions.append(sol)

	sol_was = range(len(solutions))
	for s in solutions:
		was = 0 
		for ind in s:
			was += new[ind]['WAS']
		sol_was[solutions.index(s)] = was 

	index_max = max(xrange(len(sol_was)), key=sol_was.__getitem__)
	final_solution = solutions[index_max]
	# CUs that will be abandoned 
	abandons = []
	for ind in range(len(new)):
		if ind in final_solution:
			continue
		else:
			abandons.append(new[ind])
	#print "abandons: ", abandons 
	### Construct New Pyramid 
	newpyramid = range(len(Pyramid))
	for _ in range(len(Pyramid)):
		newpyramid[_] = []
		for item in Pyramid[_]:
			if item not in abandons:
				newpyramid[_].append(item)
			else:
				continue
		Pyramid_info[_].id = _
		Pyramid_info[_].size = len(newpyramid)
	return newpyramid, Pyramid_info  

def Pickup_used(Pyramid):
	alls = [] 
	for _ in range(len(Pyramid),0,-1):
		for item in Pyramid[_-1]:
			weight = get_weight(item)
			keys = ['seg%did' % (p + 1) for p in range(weight)]
			used1 = [item[k] for k in keys]
			alls.extend(used1)
	return alls 

def Extract_Segset(df,used):
	test = []
	for i in used:
		d = i.split(".")[0]
		st = i.split(".")[1]
		sgm = i.split(".")[2]
		test.append(df[df.Doc==d][df.Sent==st][df.Segm==sgm])
	return test 

# Build records for all used segments in Pyramid layer N to 2 
def Build_All_Record(segmentpool, Pyramid):
	#segs = [seg.id for seg in segmentpool]
	sumlst = [i.id.split(".")[0] for i in segmentpool]
	sentlst = [i.id.split(".")[1] for i in segmentpool]
	segmtlst = [i.id.split(".")[2] for i in segmentpool]
	seglst = [i.id.split(".")[3] for i in segmentpool]
	data_seg = pd.DataFrame(list(zip(sumlst,sentlst,segmtlst,seglst)),columns=['Doc','Sent','Segm','Seg'])
	used = []
	for _ in range(len(Pyramid),1,-1):
		for item in Pyramid[_-1]:
			weight = get_weight(item)
			keys = ['seg%did' % (p + 1) for p in range(weight)]
			used1 = [item[k] for k in keys]
			used.extend(Extract_Segset(data_seg,used1))
	#print "Build_All_Record" , used 
	return used 

# Clean layer1, remove segments that are not adopted  
def Iterate_Clean_Record(used,Pyramid):
	allshouldbeused = []
	for every in used:
		for ind,r in every.iterrows():
			seg = r['Doc']+"."+r["Sent"]+"."+r["Segm"]+"."+r["Seg"]
			if seg not in allshouldbeused:
				allshouldbeused.append(seg)
	### Next step: filter out the duplicate elements in layer1 
	#print allused 
	layer1segs = [item['seg1id'] for item in Pyramid[0]]
	segshouldberemoved = list(set(layer1segs).difference(set(allshouldbeused)))
	print "segs should be removed: ", segshouldberemoved
	if len(segshouldberemoved) >0:
		candidate = copy.deepcopy(Pyramid[0])
		for s in Pyramid[0]:
			if s['seg1id'] in segshouldberemoved:
				candidate.remove(s)
		Pyramid[0] = candidate 
		#print "Remove segments that are not supposed to be in layer 1"
	return Pyramid[0]


def Getmax(lst):
	lst = map(int,lst)
	return max(set(lst))

def Conflict(seg1, seg2):
	if (seg1.split('.')[0] == seg2.split('.')[0]) and (seg1.split('.')[1] == seg2.split('.')[1]) and (seg1.split('.')[2] != seg2.split('.')[2]):
		return True 
	else:
		return False

def SelectNonconflict(clist):
	#tmp = [] 
	#anchor = list[0]
	#tmp.append(anchor)
	cclst = copy.deepcopy(clist)
	flag = False 
	for i in range(0,len(clist)-1):
		seg1 = clist[i]
		print "seg1: ", seg1 
		for j in range(1,len(clist)):
			seg2 = clist[j]
			if Conflict(seg1,seg2):
				if seg2 in cclst:
					cclst.remove(seg2)
				else:
					continue
	return cclst 

# Build records about documents and their sentences 
def BuildSentenceRecord(data):
	record = {}
	for r,v in data.iterrows():
		doc = v["Doc"]
		if record.has_key(doc):
			if v['Sent'] not in record:
				record[doc].append(v['Sent'])
		else:
			record[doc] = [v["Sent"]]
	return record

# test is a list of df from all used segments  
def CheckleftSentence(sentrecord,test,data):
	#tmp = []
	for docid,v in sentrecord.items():
		doc_sents = copy.deepcopy(v) 
		for each in test:
			for r,vv in each.iterrows():
				if (vv['Doc'] == docid) and (vv['Sent'] in doc_sents):
					#".".join(v.tolist())
					doc_sents.remove(vv['Sent'])
		sentrecord[docid] = doc_sents
	tmp = []
	for docid,v in sentrecord.items():
		if len(v) > 0:
			for sent in v:
				for r, vv in data.iterrows():
					if (vv['Doc'] == docid) and (vv['Sent'] == sent) and (vv['Segm'] == '0'):
						tmp.append(".".join(vv.tolist()))
	return tmp 

def Update_Record(data,alls):
	docs = []
	for i,r in data.iterrows():
		if r['Doc'] not in docs:
			docs.append(r['Doc'])
	test = []
	tmp_docs = []
	test = []
	for i in alls:
		d = i.split(".")[0]
		st = i.split(".")[1]
		sgm = i.split(".")[2]
		test.append(data[data.Doc==d][data.Sent==st][data.Segm==sgm])
		if (d in docs) and (d not in tmp_docs):
			tmp_docs.append(d)
	results = []
	for item in test:
		for ind,r in item.iterrows():
			seg = r['Doc']+"."+r["Sent"]+"."+r["Segm"]+"."+r["Seg"]
			#print "found seg: ", seg
			results.append(seg)
	missings = list(set(results).difference(set(alls)))
	missings_docs = set(docs).difference(set(tmp_docs))
	missings_docs_segs = []
	for each in missings_docs:
		for r,v in data[data.Doc==each].iterrows():
			#print "v: ", v 
			missings.append(".".join(v.tolist()))
	newmissings = SelectNonconflict(missings)
	## Sentence missing from documents 
	sentrecord = BuildSentenceRecord(data)
	missing_sents = CheckleftSentence(sentrecord, test,data)
	newmissings = list(set(newmissings).union(set(missing_sents)))
	return newmissings

def Update_AllocRecord(data,alls):
	docs = []
	for i,r in data.iterrows():
		if r['Doc'] not in docs:
			docs.append(r['Doc'])
	test = []
	tmp_docs = [] 
	for i in alls:
		d = i.split(".")[0]
		st = i.split(".")[1]
		sgm = i.split(".")[2]
		test.append(data[data.Doc==d][data.Sent==st][data.Segm==sgm])
		if (d in docs) and (d not in tmp_docs):
			tmp_docs.append(d)
	results = []
	for item in test:
		for ind,r in item.iterrows():
			seg = r['Doc']+"."+r["Sent"]+"."+r["Segm"]+"."+r["Seg"]
			#print "found seg: ", seg
			results.append(seg)
	missings = list(set(results).difference(set(alls)))
	return missings







