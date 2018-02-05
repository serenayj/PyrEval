# Last Update: Jan 23, 2018 
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
import numpy as np
import os
import glob


class Segment:
    def __init__(self,id,seg, vec):
        self.id = id
        self.seg = seg
        self.vec = vec
        self.weight = 0
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
        for n, seg_id in enumerate(seg_ids):
            res[seg_id] = edges[n]
        if graph.size() != 0:
            res['WAS'] = graph.size(weight='weight') / 2
            results.append(res)
    return results




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
                if fn[-5:] == '.segs':
                    seg_fname = fn
            #vec_fname = directory + '/' + d + '.ls'
            #seg_fname = directory + '/' + d + '.segs'
            with open(vec_fname, 'r') as f:
                lines = f.readlines()
                vecs += lines
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
        if len(i) > 2: # filter out the empty line 
            i = i.split('&')
            content.append(i)
    for i in vecs:
        if len(i) > 2:
            i = i.split('&')
            i = i[4].strip('\n').replace('[', '').replace(']', '')
            i = [float(j) for j in i.split(',')]
            vectors.append(i)
    ccontent = {} 
    for n, each in enumerate(content):
        index = '.'.join(each[:4])
        seg = each[4]
        vec = vectors[n]
        x = Segment(index, seg, vec) 
        ccontent[index] = x 
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
    for seg in segmentpool:
        segment = segmentpool[seg]
    #for segment in segmentpool:
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
    for seg in segmentpool:
        segment = segmentpool[seg]
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

# New version: Pyramid_info is a list
def CheckConstraint1(layern_length,n, N,Pyramid_info):
    if n == N:
        yn = Pyramid_info[n-1] 
        if (layern_length < yn) and (layern_length >= 1):
            return True 
        else:
            return False    
    else:
        upper = Pyramid_info[n]
        if upper >= layern_length:
            return False
        else:
            return True

def power_law(n,bf_dict):
    a = bf_dict[0]
    b = bf_dict[1]
    y = a*(math.pow(1.0/n,b)) # 1/n gives an zero 
    if type(y) is float:
        y = math.floor(y)
    return y 
