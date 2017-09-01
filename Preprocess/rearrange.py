# Script for rearrranging the segmentations based on the rules 

from bs4 import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os
import itertools

"""
==================================Sentence Segmentation =======================================
"""

class _Segment:
    def __init__(self,subject,predicate):
        _Segment.subj = subject
        _Segment.pred = predicate
        _Segment.find_subj = False 

class _SegCombo:
    def __init__(self,combolist):
        self.size = len(combolist)
        self.combo = combolist

class _Fragment:
    def __init__(self,fragment):
        self.nodes = fragment
        self.used = False 

# Input is _idseg: A set of {predicate and subject} extracted from all vp phrases
# [{'predicate': [2, 3, 4, 5, 6, 7], 'subject': 1}, {'predicate': [2, 3, 4, 5, 6, 7], 'subject': 24}, {'predicate': [14, 15, 16, 17, 18, 19], 'subject': 11}, {'predicate': [14, 15, 16, 17, 18, 19], 'subject': 1}, {'predicate': [14, 15, 16, 17, 18, 19], 'subject': 4}, {'predicate': [17, 18, 19], 'subject': 16}]
def get_segmentation3(_idseg):
    tll = []
    tll2 = []
    tmp = [] 
    # Firstly, find out if it has any overlap 
    overlap = []
    for st in _idseg:   
        i = st['predicate']
        flag = False 
        print "current i: ",i
        if i not in tll:
            if len(tll) == 0:
                tll.append(i)
            else:
                # check if current list has element overllaped with i
                for j in tll:
                    print "current j: ", j 
                    # existing overlap
                    if bool(set(j)&set(i)):
                        overlap.append(i)
                        flag = True
                        print "j is:", j
                        print "i is:", i
                if flag == False:
                    tll.append(i)
    # Secondly, iterating thru all segments in overlap, getting out segmentation from it 
    if len(overlap) !=0 :
        for stt in overlap:
            item = []
            item.append(stt)
            for st in _idseg:   
                i = st['predicate']
                if i not in item:
                    if (bool(set(stt)&set(i)) == False):
                        print "current one, ", stt
                        print "match, ", i
                        item.append(i)
            tll2.append(item) 
    # since tll only has one list         
    tmp.append(tll)
    for j in tll2:
        if len(j) != 0:
            if j not in tmp:
                tmp.append(j)
    # Use class to keep track of the segmentation, that is, a list of segment
    seg_combo = []
    for lst in tmp:
        item = _SegCombo(lst)
        seg_combo.append(item)
    return seg_combo 

# If the combination ever has duplicate element, discard it;
# Called in Make_New_Segt  
def illegal_combo(combolst,n):
    legal = [] 
    for ind, p in enumerate(combolst):
        hitlist = []
        flag = False 
        for iind in range(0,n):
            if p[iind]['predicate'] not in hitlist: 
                hitlist.append(p[iind]['predicate'])
            else:
                flag = True
        if flag == False:
            legal.append(p)
    return legal

# Input is seg_combo, 
def Make_New_Segt(seg_combo,_idseg):
    new_idseg = range(len(seg_combo))
    for ind, i in enumerate(seg_combo):
        ttmp = []
        for j in i.combo:
            for st in _idseg:
                if j == st['predicate']:
                    ttmp.append(st)
        new_idseg[ind] = ttmp
    for ind, i in enumerate(seg_combo):
        n = i.size
        combolst = itertools.combinations(new_idseg[ind],n)
        legal = illegal_combo(combolst,n)
        new_idseg[ind] = legal 
    return new_idseg

def get_left(res,tl):
    left = range(len(res))
    for index,i in enumerate(res):
        nodes = []
        for seg in i:
            for _ind in range(0,len(seg)):
                nodes += [int(seg[_ind]['subject'])]+[int(item) for item in seg[_ind]['predicate']]
        print "all nodes from segmentation", index," ", set(nodes)
        left_nodes = set(tl)-(set(nodes))
        print "left nodes:", left_nodes
        left[index] = sorted(left_nodes)
        #print left_nodes 
    return left 

def Insertion(j,ele,case,tail,head):
    if case == 0:
        for each in j.nodes:
            ele.insert(0,each)
            j.used = True
    elif case == 1:
        position = [iele for iele,x in enumerate(ele) if x == tail+1] 
        for each in j.nodes:
            ele.insert(position[0],each)
            ele = sorted(ele)
            j.used = True
    elif case == 2:
        position = [iele for iele,x in enumerate(ele) if x == head-1] 
        for each in j.nodes:
            ele.insert(position[0],each)
            ele = sorted(ele)
        j.used = True
    elif case == 3:
        for each in j.nodes:
            ele.insert(len(ele)-1,each)
            ele = sorted(ele)
        j.used = True
    elif case == 4:
        #if head not in ele:
        for each in j.nodes:
            ele.insert(0,each)
            ele = sorted(ele)
        #print "this case, ele is", ele
        j.used = True
    elif case == 5:
        absval = [] 
    return ele 


# Need to fix that the subject should be rearrange to an appropriate place
# res is a list of dictionary, containing preprocessed segmentations, where every segment go to an appropriate segmentation with subject 
def Rearrange2(tl,res,left):
    seg = range(len(res)) 
    new_left = range(len(res))
    for index,each in enumerate(left):
        new_left[index] = left_segment(each)
    for ind, st in enumerate(res):
        # Iterating thru segmentations
        # i is each segmentation  
        for i in st:
            # length of each segmentation(#segments in a segmentation)
            tmp = range(len(i))
            print "curr ind", ind
            # Set fragments are false before iterating thru each segmentation 
            # Otherwise, fragments used before won't be considered again!!! 
            for j in new_left[ind]:
                j.used = False 
            #Iterating thru segments 
            for iind in range(0,len(i)):
                # because i is a list of dictionary  
                ele = copy.deepcopy(i[iind]['predicate'])
                #print "current element: ", ele
                for j in new_left[ind]:
                    if j.used == False:
                        #print "current fragment:", j.nodes
                        head = j.nodes[0]
                        tail = j.nodes[len(j.nodes)-1]
                    else:
                        pass
                    # Case 0, special case of case 1, just directly append to the head 
                    # If tails equals the very first word in the very first predicate
                    if (tail+1 == i[iind]['predicate'][0]) and (j.used == False):
                        case = 0
                        Insertion(j,ele,case,tail,head)
                        #print "Hit case 0"
                    else:
                        for iiind in range(0,len(i[iind]['predicate'])):
                            # Case 1, prepend to X+1 
                            if (tail+1 == i[iind]['predicate'][iiind]) and (tail not in ele) and (j.used == False):
                                case = 1
                                ele = Insertion(j,ele,case,tail,head)
                                #print "Hit case 1"
                            # Case 2, append to X-1
                            elif (head-1 ==  i[iind]['predicate'][iiind]) and (head not in ele) and (j.used == False):
                                    case = 2 
                                    ele = Insertion(j,ele,case,tail,head)
                                    #print "Hit case 2"
                            elif (head > i[iind]['predicate'][len(i[iind]['predicate'])-1]) and (j.used == False):
                                    case = 3 
                                    if iind != len(i)-1:
                                        j.used = False 
                                    else:
                                        ele = Insertion(j,ele,case,tail,head)
                                        #print "Hit case 3"
                            elif (tail < i[iind]['predicate'][0]) and (j.used == False):
                                    case = 4
                                    ele = Insertion(j,ele,case,tail,head)
                                    #print "Hit case 4"  
                            else:
                                pass
                print "element after...", ele 
                tmp[iind] = sorted(ele) 
        seg[ind] = tmp
        for final in new_left[ind]:
            if final.used == False:
                print "Fragment in ", ind, " left to be unused: ", final.nodes 
    return seg 

# Connect segments and subject 
def Connect_subj(res, seg):
    final = (range(len(seg)))
    for ind, st in enumerate(res):
        for segt in st:
            tmp = [] 
            for iind, ii in enumerate(segt):
                subj = ii['subject']
                item = [subj]+ seg[ind][iind] 
                print "find match: predicate ",seg[ind][iind], "subject: ",subj
                tmp.append(item)
        final[ind] = tmp 
    return final 

# After seg = Rearrange2
def further_modify(res,seg):
    subjmap = [] 
    for i in res:
        for j in i:
            subj = int(j['subject'])
            if subj not in subjmap:
                subjmap.append(subj)
    new_res = [] 
    for ind in range(0,len(res)):
        ttmp = []
        for iind in range(0,len(res[ind])):
            subj = int(res[ind][iind]['subject'])
            item = seg[ind][iind]
            if subj in item:
                ttmp.append(item)
            # if subj not in item 
            else:
                ttmp.append([subj]+[x for x in item])
        new_res.append(ttmp)
    return new_res 
    
def left_segment(nl):
    ttmp = []
    tmp = []
    for i in range(0,len(nl)):
        if i == 0:
            ttmp.append(nl[0])
            continue
        elif i != len(nl)-1:
            if (nl[i] - nl[i-1]) != 1:
                tmp.append(ttmp)
                ttmp = []
                ttmp.append(nl[i])
            else:
                ttmp.append(nl[i])
        else:
            if (nl[i] - nl[i-1]) != 1:
                tmp.append(ttmp)
                ttmp = []
                ttmp.append(nl[i])
            else:
                ttmp.append(nl[i-1])
                ttmp.append(nl[i])
    non_duplicate = []
    for t in ttmp:
        if t not in non_duplicate:
            non_duplicate.append(t)
    tmp.append(non_duplicate)
    del ttmp 
    fragment = [] 
    for item in tmp:
        _fra = _Fragment(item)
        fragment.append(_fra)
    return fragment 

def reorder(tmp):
    tt = []
    for i in tmp:
        ttt = []
        for j in i:
            ttt.append(sorted(j))
        if ttt not in tt:
            tt.append(ttt)
    return tt 