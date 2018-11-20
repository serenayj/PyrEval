import collections 
from operator import itemgetter 
import copy
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








