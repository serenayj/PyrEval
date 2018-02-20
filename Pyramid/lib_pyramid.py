# Last Update: July 9,2017 
# Author: Yug125

# This is a python script for all the helper functions used in pyramid constructions 
# Finished/Working find:
# Duplicate, PickLowerWAS, HypSetFree, SettleNodes, SortDescendingWAS 

#from pipeline import pairwise
import networkx as nx
import copy
import math
from itertools import combinations
from sklearn.metrics.pairwise import cosine_similarity as cos
#from js_similarity import cos 
import numpy as np
import os
import glob


"""
========================== Class Definitions =========================================
"""
class Segment:
    def __init__(self,id,seg, vec):
        self.id = id
        self.seg = seg
        self.vec = vec
        # For settling the nodes
        self.status = False 
        self.docid= int(id.split('.')[0])
        self.sentid = int(id.split('.')[1])
        self.segtationid = int(id.split('.')[2])
        # If the current segment is commited, then all the segments belongs to this same segmentation will set as False, the segments belong to the other segmentation will be True
        self.commit_invalid = False 

class Layer:
    def __init__(self,id):
        self.id = id 
        # size: # of segments in this layer
        self.size = 0
        # length: # of segsets in this layer 
        self.length = 0
        # capacity: the upper bound of # segsets this layer is able to fit 
        self.capacity = 0 
        self.WAS = 0 
        # constraint1: a status showing if the current layer satisfies the constraint 1 
        self.constraint1 = False



# Two examples of what a BigSet will look like. Here w = 2 


# Probably needs to write as class 
#segmentpool = [{'status': False, 'id': '1.1.0.0.'}, {'status': False, 'id': '1.1.1.0.'}, {'status': False, 'id': '1.1.1.1.'}, {'status': False, 'id': '1.2.1.0.'}, {'status': False, 'id': '1.2.2.0.'}, {'status': False, 'id': '1.3.0.0.'}, {'status': False, 'id': '2.2.0.1.'},{'status': False, 'id': '2.1.2.0.'}, {'status': False, 'id': '2.2.0.1.'}, {'status': False, 'id': '2.7.4.2.'}, {'status': False, 'id': '3.1.1.0.'}, {'status': False, 'id': '2.2.0.0.'}, {'status': False, 'id': '2.2.1.0.'},{'status': False, 'id': '2.16.0.2'}, {'status': False, 'id': '3.1.0.0'}, {'status': False, 'id': '3.1.0.1.'}, {'status': False, 'id': '3.1.1.1.'}, {'status': False, 'id': '3.2.0.0'}]

def Duplicate(i,j):
    #A function checks if SegSet i, j have duplicated segments, return True or False.
    flag = False 
    for k,v in i.items():
        if j[k] == v:
            flag = True 
    return flag 

def PickLowerWAS(i,j):
    # A function takes SegSet i and j and returns the SegSet with higher WAS(Weighted Average Simi-larity).
    lower = min(i['WAS'],j['WAS'])
    if lower == i['WAS']:
        return i
    else:
        return j 

def PickHigherWAS(i,j):
    higher = max(i['WAS'],j['WAS'])
    if higher == i['WAS']:
        return i
    else:
        return j 

def GetSegment(k,BigSegSet):
    # A function finds SegSets that contains Segk from a known BigSegSet, while BigSegSet could be a
    # set of SegSets where weight = n
    candidate = []
    for item in BigSegSet:
        for key,value in item.items():
            if value == k:
                if item not in candidate:
                    candidate.append(item)
    return candidate 


def ComposeSegSets(BigSet2, segmentpool, n):
    candidates = [segment.id for segment in segmentpool if segment.status == False]
    bs2 = copy.deepcopy(BigSet2)
    for pair in BigSet2:
        seg1id = pair['seg1id']
        seg2id = pair['seg2id']
        if seg1id not in candidates or seg2id not in candidates:
            bs2.remove(pair)
    edges = [(pair['seg1id'], pair['seg2id'], pair['WAS']) for pair in bs2]
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    completed_graphs = [s for s in nx.enumerate_all_cliques(G) if len(s) == n]
    graphs = [G.subgraph(g) for g in completed_graphs]
    seg_ids = ['seg%did' % (p + 1) for p in range(n)]
    results = []
    for graph in graphs:
        edges = copy.deepcopy(graph.nodes())
        res = {}
        #for n, seg_id in enumerate(seg_ids):
            #res[seg_id] = edges[n]

        # Modifying by Yanjun: Work for networkx 2.0 
        count = 0 
        for i in edges:
            seg_id = seg_ids[count]
            res[seg_id] = i 
            count += 1 
        if graph.size() != 0:
            #res['WAS'] = graph.size(weight='weight') / 2
            res['WAS'] = float(graph.size(weight='weight')) / graph.size()
            results.append(res)
    return results




def SortDescendingWAS(Sets):
    # A function sorts a given set by WAS in a descending way.
    Sets.sort(key=lambda x:x['WAS'], reverse = True)
    return Sets 

def HypSetFree(SegSet,fakepool):
    # A function hypothetically sets free all Seg in a given SegSet, returns all the segments.
    # Might change if the data strucutre is class 
    copy.deepcopys = []
    # Sets free the given SegSet 
    for k,v in SegSet.items():
        if 'id' in k:
            copy.deepcopys.append(v)
    # Mark newly free segments as False in pool 
    # Can't really mark it as false, set a fakepool 
    for item in fakepool:
        if item.id in copy.deepcopys:
                item.status = False
    return fakepool 
            # Might need some way to index to segment pool, probably using dictionary       # Might need some way to index to segment pool, probably using dictionary  

def BottomUPWAS(layern,n,N, Pyramid_info):
    # A function calculates the overall WAS started from the current layer.
    # Because input might be a fake layer, so we start from summing WAS of fake layer 
    overallWAS = 0
    ### Test by Yanjun 
    for segset in layern:
        overallWAS += segset['WAS']
    if len(layern) != 0:
        overallWAS = float(overallWAS)/len(layern)
    for i in range(n+1,N+1):
        if type(Pyramid_info[i-1]) != int:
            if Pyramid_info[i-1].length !=0:
                temp = float(Pyramid_info[i-1].WAS)/Pyramid_info[i-1].length
                overallWAS += temp
            else:
                overallWAS += Pyramid_info[i-1].WAS
            #overallWAS += Pyramid_info[i-1].WAS
    #print "Update Attration! ", overallWAS
    return overallWAS

def LayerWAS(layern):
    # A function calculates WAS for a given layer, or a set contains a copy.deepcopy of segsets 
    WAS = 0
    for segset in layern:
        WAS += segset['WAS']
    return WAS 

def TracePaths(layern,n):
    # Probably don't need it 
    # A function traces all index of SegSets in a hypothetical pyramid
    # Need to consider the data structure 
    return 0


def ExecuteHypSol(Solution):
    # A function executes the given optimal solutions, and recheck all the constraints.
    return 0

def CheckConstraint1(layern_length,n, N,Pyramid_info):
    if n == N:
        yn = Pyramid_info[n-1].capacity 
        if (layern_length < yn) and (layern_length >= 1):
            return True 
        else:
            return False    
    else:
        upper = Pyramid_info[n]
        if upper.length >= layern_length:
            return False
        else:
            return True

"""
========================== Settle Nodes ================================
"""
def getUsedSegs(layern, N):
    seg_ids = []
    for seg_set in layern:
        seg_ids += [seg_set['seg%did' % (p + 1)] for p in range(N)]
    return seg_ids

def SettleNodes(layern, N, segmentpool):
    usedSegs = getUsedSegs(layern, N)
    newSegmentPool = []
    for segment in segmentpool:
        if segment.id in usedSegs:
            segment.status = True
            newSegmentPool.append(segment)
        elif segment.commit_invalid == True:
            segment.status = True
            newSegmentPool.append(segment)
            
        else:
            newSegmentPool.append(segment)
    return newSegmentPool




"""
================ Segment Construction and BigSet 2 Construction =====================
"""


def readFiles(directories):
    segs = []
    vecs = []
    N = 0
    for directory in directories:
        if os.path.isdir(directory):
            N += 1
            #slash = directory.rfind('/')
            #d = directory[slash + 1:]
            #d = directory[]
            ii = glob.iglob(directory+'/*')
            for fn in ii:
                if fn[-3:] == '.ls':
                    vec_fname = fn
                    #print vec_fname
                if fn[-5:] == '.segs':
                    seg_fname = fn
                    #print seg_fname
            #vec_fname = directory + '/' + d + '.ls'
            #seg_fname = directory + '/' + d + '.segs'
            with open(vec_fname, 'r') as f:
                lines = f.readlines()
                vecs += lines
                #vecs += lines.strip("\n")
            f.close()
            with open(seg_fname, 'r') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                segs += lines
            f.close()
        else:
            pass
    return segs, vecs, N

def make_segs(text, vecs):
    content = []
    vectors = []
    for i in text:
        # By Yanjun: using SIF needs strip out the line breaker 
        if len(i) > 2: # filter out the empty line 
            i = i.split('&')
            content.append(i)
    for i in vecs:
        i = i.strip("\n")
        if len(i) > 2:
            i = i.split('&')
            i = i[4].strip('\n').replace('[', '').replace(']', '')
            i = [float(j) for j in i.split(',')]
            vectors.append(i)
    print len(vectors)
    print len(content)
    ccontent = [] 
    for n, each in enumerate(content):
        index = '.'.join(each[:4])
        seg = each[4]
        vec = vectors[n]
        x = Segment(index, seg, vec) 
        ccontent.append(x)
    return ccontent

def get_text(fname):
    f = open(fname, 'r')
    lines = f.readlines()
    lines = [line.split('&')[4] for line in lines]
    slash = fname.rfind('/')
    dot = fname.rfind('.')
    new_name = 'files/' + fname[slash + 1:dot]
    with open(new_name, 'w') as f:
        for line in lines:
            f.write(line)
    f.close()
    return new_name

def pairwise(segmentpool, N, threshold):
    result = []
    summs = [[] for i in range(N)]
    for segment in segmentpool:
        doc = segment.docid - 1
        summs[doc].append(segment)
    summ_pairs = combinations(summs, 2)
    scores = []

    for summ_pair in summ_pairs:
        for segment in summ_pair[0]:
            if type(segment.vec) is list:
                segment.vec = np.array([segment.vec])
                segment.vec.reshape(-1,1)
            else:
                if segment.vec.shape == (1,100):
                    segment.vec.reshape(-1,1)
                else:
                    pass 
            #segment.vec = np.array([segment.vec])
            #segment.vec.reshape(-1,1)
            for seg in summ_pair[1]:
                if type(seg.vec) is list:
                    seg.vec = np.array([seg.vec])
                    seg.vec.reshape(-1,1)
                else:
                    if seg.vec.shape == (1,100):
                        seg.vec.reshape(-1,1)
                    else:
                        pass 
                sc = cos(segment.vec, seg.vec)[0][0]
                #print sc
                #sc = cos(segment.vec, seg.vec)
                scores.append(sc)
                result.append( {'seg1id': segment.id, 'seg2id': seg.id, 'seg1': segment.seg, 'seg2': seg.seg, 'WAS': sc*2})
    Q3 = np.percentile(np.asarray(scores), threshold)
    fifty = np.percentile(np.asarray(scores), 50)
    print fifty
    #print('\tCosine Score for Quantile: %.3f' % Q3)
    rresult = []
    for res in result:
        if (res['WAS'] / 2) > Q3:
            rresult.append(res)
    return rresult

def pairwise_test(segmentpool,N):
    result = []
    summs = [[] for i in range(N)]
    for segment in segmentpool:
        doc = segment.docid - 1
        summs[doc].append(segment)
    summ_pairs = combinations(summs, 2)

    for summ_pair in summ_pairs:
        for segment in summ_pair[0]:
            if type(segment.vec) is list:
                segment.vec = np.array([segment.vec])
                segment.vec.reshape(-1,1)
            else:
                if segment.vec.shape == (1,100):
                    segment.vec.reshape(-1,1)
                else:
                    pass 
            #segment.vec = np.array([segment.vec])
            #segment.vec.reshape(-1,1)
            #print "segment shape", segment.vec.shape
            for seg in summ_pair[1]:
                if type(seg.vec) is list:
                    seg.vec = np.array([seg.vec])
                    seg.vec.reshape(-1,1)
                else:
                    if seg.vec.shape == (1,100):
                        seg.vec.reshape(-1,1)
                    else:
                        pass 
                #print "seg shape", seg.vec.shape 
                sc = cos(segment.vec, seg.vec)[0][0]
                #sc = cos(segment.vec,seg.vec)
                #if sc > 0.5:
                #result.append( {'seg1id': segment.id, 'seg2id': seg.id, 'seg1': segment.seg, 'seg2': seg.seg, 'WAS': sc*2})
                result.append(sc)
    with open("scores.txt",'w') as f:
        for i in result:
            lines = str(i)+"\n"
            f.write(lines)
    return result


"""
========================================= Power Law ==================================
"""

def BruteForceLaw(segs,N):
    combination = [] 
    brange = np.arange(1,3.0,0.5)
    for a in range(200,400):
        for b in brange:
            sum_y = 0
            for n in range(1,N):
                y = a*(math.pow(1.0/n,b)) 
                sum_y += y
            if sum_y > segs:
                pair = {'a':a,'b':b,'sum':sum_y}
                combination.append(pair)
            else:
                pass 
    #print combination 
    final = min(combination, key=lambda x:abs(x['sum']-segs))

    return final 

def power_law(n,bf_dict):
    a = bf_dict[0]
    b = bf_dict[1]
    y = a*(math.pow(1.0/n,b)) # 1/n gives an zero 
    if type(y) is float:
        y = math.floor(y)
    return y 

# def power_law(n, tup):
#     a = tup[0]
#     b = tup[1]
#     print 'a:', a, 'b:', b
#     y = a*(math.pow(1.0/n,b)) # 1/n gives an zero 
#     if type(y) is float:
#         y = math.floor(y)
#     return y 




"""
========================================= Best Fit =================================
"""

def BestFit(layern, n, segmentpool,capacity):
    segments_in_layer = []
    layer_copy = copy.deepcopy(layern)
    if n == 4 and capacity == 1:
        capacity = 2
    while (len(segments_in_layer) + 1 < capacity) and (len(layer_copy) != 0):
            # While Condition : We are below (or at) capacity and we arent searching an empty set
        max_seg_set = layer_copy[0]
        segments_in_layer.append(max_seg_set)
        seg_ids_we_cant_use = [max_seg_set['seg%did' % (p + 1)] for p in range(n)]
        docs_and_segs = {seg_id.split('.')[0]: [seg_id.split('.')[1], seg_id.split('.')[2]] for seg_id in seg_ids_we_cant_use}
        docs = [seg_id.split('.')[0] for seg_id in seg_ids_we_cant_use]
        to_remove = set()
        ids_to_remove = set(max_seg_set['seg%did' % (p + 1)] for p in range(n))
        layer_copy.remove(max_seg_set)
        layer_set = set()
        for seg_set in layern[1:]:
            layer_set.add(tuple(seg_set.values()))
            # We Should Not start at the maximum
            seg_ids = [seg_set['seg%did' % (p + 1)] for p in range(n)]
            for seg_id in seg_ids:
                if seg_id in seg_ids_we_cant_use:
                    to_remove.add(tuple(seg_set.values()))
                    ids_to_remove.add(seg_id)
                elif seg_id.split('.')[0] in docs:
                    sent_and_segt = docs_and_segs[seg_id.split('.')[0]]
                    if sent_and_segt[0] == seg_id.split('.')[1]: # If the sentence ID of the seg_set we are looking at is the same as the one we cant use
                        if sent_and_segt[1] == seg_id.split('.')[2]: # If they are the same segmentation, we can keep this seg_set in the seg_set pool
                            pass
                        else:
                            to_remove.add(tuple(seg_set.values()))
                            ids_to_remove.add(seg_id)
        if len(to_remove) == 0:
            # If there is nothing to remove, and the length of the layer_copy is not empty, we need to break
            layer_copy = layer_copy[1:]
        else:
            layer_set = layer_set.difference(to_remove)
            layer_copy = [seg_set for seg_set in layer_copy if tuple(seg_set.values()) in layer_set]

        for segment in segmentpool:
            if segment.id in ids_to_remove:
                segment.commit_invalid = True
    for seg_set in segments_in_layer:
        seg_ids = [seg_set['seg%did' % (p + 1)] for p in range(n)]
        seg_ph = ['seg%did' % (p + 1) for p in range(n)]
        for j, seg_id in enumerate(seg_ids):
            seg = findSegFromID(seg_id, segmentpool)
            seg_num = seg_ph[j][3]
            seg_set['seg%s' % seg_num] = seg
    return segments_in_layer


def findSegFromID(segID, segmentpool):
    for segment in segmentpool:
        if segment.id == segID:
            return segment.seg
    else:
        return None


"""
======================= Local Backtracking =============================
"""


def segSetTrueInFakePool(SegSet, fakepool):
    copy.deepcopys = []
    for k, v in SegSet.items():
        if 'id' in k:
            copy.deepcopys.append(v)
    for item in fakepool:
        if item.id in copy.deepcopys:
            item.status = True
    return fakepool

def execute_solutions(BigSet2, fakepool, n, segmentpool, bf_dict):
    newFullyCompletedCurrentLayer = ComposeSegSets(BigSet2, fakepool, n+1)
    newFullyCompletedCurrentLayer = SortDescendingWAS(newFullyCompletedCurrentLayer) 
    current = BestFit(newFullyCompletedCurrentLayer, n+1, segmentpool, bf_dict)
    return current
def getSolutionMap(direction, fakepool, Pyramid, n, BigSet2, Pyramid_info, N, segmentpool, bf_dict):
    solution_map = []
    for j, seg_set in enumerate(Pyramid[direction]):
        #temp_solution = [segSet, was, direction]
        temp_solution = [[], [], []]
        fakepool = HypSetFree(seg_set, fakepool)
        newLayer = ComposeSegSets(BigSet2, fakepool, n+1)
        newLayer = SortDescendingWAS(newLayer)
        newLayer = BestFit(newLayer, n+1, segmentpool, bf_dict)
        was = BottomUPWAS(newLayer,n+1, N, Pyramid_info)
        temp_solution[0] = seg_set; temp_solution[1] = was; temp_solution[2] = direction
        fakepool = segSetTrueInFakePool(seg_set, fakepool)
        solution_map.append(temp_solution)
    return solution_map
def CheckConstraintsForDirection(length, direction, Pyramid_info, N = 5):
    truth = CheckConstraint1(length, direction + 1, N, Pyramid_info)
    return truth

def CheckCurrentConstraint(current_len, n, lengths):
    bools = []
    if (n + 1) in lengths.keys():
        if current_len <= lengths[n+1]:
            bools.append(False)
    elif (n - 1) in lengths.keys():
        if current_len >= lengths[n-1]:
            bools.append(False)
    return all(bools)
def checkDirections(other_layer_len, n_other, Pyramid_info, Pyramid):
    if n_other + 1 < len(Pyramid):
        #print '\t\tChecking Layer', n_other + 1, 'against Layer', n_other + 2
        #print '\t\t\tLength of Layer', n_other + 1, ': ', other_layer_len
        #print '\t\t\tLength of Layer', n_other + 2, ': ', Pyramid_info[n_other + 1].length
        if other_layer_len <= Pyramid_info[n_other + 1].length:
            return False
        else:
            return True
    else:
        #print '\t\tLayer', n_other + 1, 'is the topmost layer'
        #print '\t\t\tLength of Top Layer', other_layer_len
        if other_layer_len != 1:
            return True
        elif other_layer_len > Pyramid_info[n_other].length:
            return True
        else:
            return False
def checkNeighbors(current_len, n, segmentpool, Pyramid_info, Pyramid, N):
    if 0 <= n + 1 < len(Pyramid_info): # Is there an abover layer (i.e., are we checking layer 5?)
        if type(Pyramid[n+1]) != int:  # Has the above layer been set as an instance of Layer?
            above_layer = Pyramid_info[n + 1]
            ##print "above_layer length", above_layer.length
        else:
            above_layer = False # There is no above_layer
    else:
        above_layer = False # There is no above_layer
    if 0 <= n -1 < len(Pyramid_info): # Is ther a below layer (i.e, are we checking the bottom layer?)
        if type(Pyramid_info[n-1]) != int:
            below_layer = Pyramid_info[n - 1]
            ##print "below_layer length", below_layer.length
        else:
            below_layer = False
    else:
        below_layer = False
    Directions = []
    if n == 0:
        Directions.append(1) 
    else:
        if above_layer:
            if above_layer.length > 0:
                    Directions.append(n + 1)
        if below_layer:
            if below_layer.length > 0:
                    if below_layer.length - 1 > current_len:
                        Directions.append(n - 1)
    return Directions

def localBackTracking(current, n, segmentpool, Pyramid_info, Pyramid, BigSet2, N, bf_dict):

    n = n - 1
    Directions = checkNeighbors(len(current), n, segmentpool, Pyramid_info, Pyramid, N)
    #print '\tRunning Local BackTracking On Layer', n+1

    if len(Directions) == 0:
        flag = False

    else:
        ##print '\t\tDirections to be Checked are: ', [d + 1 for d in Directions]
        ##print '\t\tBefore Running...'
        ##print '\t\t\tLength of Layer', n + 1, ': ', len(current)
        #for direction in Directions:
            ##print '\t\t\tLength of Layer', direction + 1, ': ', Pyramid_info[direction].length

        global_solutions = []
        lengths = {}
        fakepool = copy.deepcopy(segmentpool)
        for seg_set in current:
            seg_ids = [seg_set['seg%did' % (p + 1)] for p in range(n+1)]
            for seg_id in seg_ids:
                for segment in fakepool:
                    if segment.id == seg_id:
                        segment.status = False
        #print 'Segment Pool At Beginning', len([segment for segment in fakepool if segment.status == False])


        current_len = len(current)
        segSets_we_may_use = []

        for direction in Directions:
            global_solutions += getSolutionMap(direction, fakepool, Pyramid,  n, BigSet2, Pyramid_info, N, segmentpool, bf_dict)
            lengths[direction] = Pyramid_info[direction].length
        
        max_was = max(global_solutions, key=lambda x:x[1])
        newCurrent = []
        pyramid_copy = copy.deepcopy(Pyramid)
        pyramid_info_copy = copy.deepcopy(Pyramid_info)

        while (CheckCurrentConstraint(current_len, n, lengths) == False) and len(Directions) != 0:
            #print('\t\tInterchanged a Segment Set')
            fakepool = HypSetFree(max_was[0], fakepool)
            newCurrent = execute_solutions(BigSet2, fakepool, n, fakepool, bf_dict)

            current_len = len(newCurrent)
            current = newCurrent

            #print '\t\t\tLength of Layer', n + 1, ': ', current_len
            lengths[max_was[2]] -= 1
            #print '\t\t\tLength of Layer', max_was[2] + 1, ': ',  lengths[max_was[2]]
            seg_ids = [max_was[0]['seg%did' % (p + 1)] for p in range(max_was[2]+1)]
            #was = [max_was[0]['WAS']]
            #overall_was = max_was[1]
            #print '\t\t\t\tMoved {} from Layer {} to Layer {}: overall WAS {}'.format([seg_ids + was], max_was[2] + 1, n + 1, overall_was)
            global_solutions.remove(max_was)
            segSets_we_may_use.append(max_was)
            pyramid_copy[max_was[2]].remove(max_was[0])
            obj = pyramid_info_copy[max_was[2]]
            obj.length = lengths[max_was[2]]
            obj.size = obj.length * (max_was[2] + 1)
            pyramid_info_copy[max_was[2]] = obj

            ans = checkDirections(lengths[max_was[2]], max_was[2], pyramid_info_copy, pyramid_copy) 
            if ans == False:
                
                    flag, fakepool, pyramid_copy, pyramid_info_copy, new_other_layer = localBackTracking(pyramid_copy[max_was[2]], 
                                                                                                            max_was[2] + 1, 
                                                                                                            fakepool, 
                                                                                                            pyramid_info_copy, 
                                                                                                            pyramid_copy, 
                                                                                                            BigSet2, N, bf_dict)
                    if flag:
                        obj = pyramid_info_copy[max_was[2]]
                        obj.length = len(new_other_layer)
                        obj.size = len(new_other_layer) * (max_was[2]+1)
                        lengths[max_was[2]] = obj.length
                        obj.constraint1 = True
                        pyramid_copy[max_was[2]] = new_other_layer
                        pyramid_info_copy[max_was[2]] = obj
                        global_solutions = [solution for solution in global_solutions if solution[2] != max_was[2]]
                        global_solutions += getSolutionMap(max_was[2], fakepool, pyramid_copy,  n, BigSet2, pyramid_info_copy, N, segmentpool, bf_dict)
                        max_was = max(global_solutions, key=lambda x:x[1])
                        continue
                    else:
                 
                    #print '\t\tCannot Back Track from Layer', max_was[2] + 1
                        del lengths[max_was[2]]
                        Directions.remove(max_was[2])
                        global_solutions = [solution for solution in global_solutions if solution[2] != max_was[2]]

            if len(global_solutions) != 0:
                max_was = max(global_solutions, key=lambda x:x[1])
        else:
            flag = True    
            Pyramid = pyramid_copy
            Pyramid_info = pyramid_info_copy
            segmentpool = fakepool
    #print 'Segment Pool At End', len([segment for segment in segmentpool if segment.status == False])

    #print '\tDone Running Local Backtracking on Layer', n + 1
    return flag, segmentpool, Pyramid, Pyramid_info, current



"""
=============================Global BackTracking=================================
"""

def GLobalBT(Pyramid_info,Pyramid, N, segmentpool, bf_dict, BigSet2):
    # First, if there is any layer marked as False, go back and start local backtracking

    for n in range(len(Pyramid_info) - 1):
        if Pyramid_info[n].length <= Pyramid_info[n + 1].length:
            Pyramid_info[n].constraint1 = False
        else:
            Pyramid_info[n].constraint1 = True
    for ind in range(0,N):
        current = Pyramid_info[ind]
        #print(current)
        #print(current.constraint1)
        if current.constraint1 == False:
            try:
                flag, segmentpool, Pyramid, Pyramid_info, current = localBackTracking(Pyramid[ind], ind+1, segmentpool, Pyramid_info, Pyramid, BigSet2, N, bf_dict)
                layer = current
                length = len(layer)
                obj = Pyramid_info[ind]
                obj.length = length
                obj.size = length * n
                Pyramid_info[ind] = obj
                Pyramid[ind] = layer
                segmentpool = SettleNodes(layer, ind + 1, segmentpool)
            except ValueError:
                pass
    # Second, if there is any segment marked as False, feed them into layer1 
    for seg in segmentpool:
        if seg.status == False:
            #layer1 = Pyramid[0] 
            item = {'seg1':seg.seg,'seg1id':seg.id,'WAS':1}
            Pyramid[0].append(item)
        # Settle all the segments 
        segmentpool = SettleNodes(Pyramid[0], 1, segmentpool)
        obj = Pyramid_info[0]
        obj.length = len(Pyramid[0])
        obj.size = obj.length * 1
        Pyramid_info[0] = obj
    # Thirdly, check if the total numbers of the segments
    totalsegs = 0
    upperbound = 0 
    # Summation of all segments across all layers 
    for k,layer in enumerate(Pyramid):
        totalsegs += len(layer) * (k+1)
    # Summation of yn * n, for n in range(0,N)
    for obj in Pyramid_info:
        upperbound += obj.capacity * obj.id 
    #if totalsegs <= upperbound:
    #   #print "Termination!"
    #else:
    #    localBackTracking(Pyramid[1], 1, segmentpool, Pyramid_info[1],Pyramid, BigSet2)
    return segmentpool, Pyramid_info, Pyramid

"""
======================== Layer Building ==================================
"""
def ComposeLayer2(BigSet2, segmentpool):
    candidates = [segment.id for segment in segmentpool if segment.status == False]
    bs2 = copy.deepcopy(BigSet2)
    for pair in BigSet2:
        seg1id = pair['seg1id']
        seg2id = pair['seg2id']
        if seg1id not in candidates or seg2id not in candidates:
            bs2.remove(pair)
        elif pair in bs2:
            bs2[bs2.index(pair)]['WAS'] /= 2
    return bs2

def ComposeLayer1(segmentpool):
    segpool = [segment for segment in segmentpool if segment.status == False]
    segpool_copy = copy.deepcopy(segpool)
    bs1 = []
    while len(segpool_copy) != 0:
        segment = segpool_copy[0]
        to_remove = [segment]
        sentence_family = {}
        for seg in segpool_copy:
            if seg.docid == segment.docid:
                if seg.sentid == segment.sentid:
                    if seg.segtationid in sentence_family.keys():
                        sentence_family[seg.segtationid].append(seg)
                    else:
                        sentence_family[seg.segtationid] = [seg]
                    to_remove.append(seg)
        else:
            if len(to_remove) == 0:
                segpool_copy = segpool_copy[1:]
            else:
                segpool_copy = [seg for seg in segpool_copy if seg not in to_remove]
                most_segs = max(sentence_family.values(), key=lambda val: len(val))
                bs1 += [{'seg1id': seg.id, 'seg1': seg.seg, 'WAS': 1} for seg in most_segs]
                for s in most_segs:
                    for seg in segmentpool:
                        if seg.id == s.id:
                            seg.status = True
                    s.status = True
                for k, v in sentence_family.items():
                    if v != most_segs:
                        for s in v:
                            for seg in segmentpool:
                                if s.id == seg.id:
                                    seg.status = True
                for seg in to_remove:
                    for s in segmentpool:
                        if s.id == seg.id:
                            s.status = True
    return bs1, segmentpool


def RecursiveSettling(Pyramid, segmentpool):
    for segment in segmentpool:
        segment.status = False
    for n, layer in enumerate(Pyramid):
        if type(layer) != int:
            segmentpool = SettleNodes(layer, n + 1, segmentpool)
    return segmentpool









