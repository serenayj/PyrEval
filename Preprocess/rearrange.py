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

class _CompatibleSeg:
    def __init__(self,anchor):
        self.anchor = anchor 
        self.lst = []
        # Turn it to True if there is a conflict 
        self.conflict = False
    def IsCompatible(self,anchor,candidate):
        self.conflict = False
        for item in self.lst:
            # Simple way to check if two predicates are overlapped 
            if bool(set(item['predicate'])&set(candidate['predicate'])) == False:
                #print "candidate ", candidate, "is Compatible" 
                pass 
            else:
                self.conflict = True 
        if self.conflict == True:
            pass
        else:
            self.lst.append(candidate)
        return self.lst 

# Take long and short and make it as _SegCombo 
def with_segmentation(_idseg):
    tmp = [] 
    for i in range(0,len(_idseg)-1):
        anchor = _idseg[i]
        x = _CompatibleSeg(anchor)
        for j in range(1,len(_idseg)):
            candidate = _idseg[j]
            if bool(set(anchor['predicate'])&set(candidate['predicate'])) == False:
                lst = x.IsCompatible(anchor,candidate)
            else:
                lst = [] 
        item = {'anchor': anchor, 'lst':lst}
        tmp.append(item)
    seg_combo = []
    for each in tmp:
        segmt = []
        segmt.append(each['anchor'])
        segmt += [x for x in each['lst']]
        if segmt not in seg_combo:
            seg_combo.append(segmt)
    return seg_combo 


def get_left(res,tl):
    left = range(len(res))
    for index,i in enumerate(res):
        nodes = []
        for seg in i:
            # irregular segmentation format 
            if type(seg) is tuple:
                for _ind in range(0,len(seg)):
                    nodes += [int(seg[_ind]['subject'])]+[int(item) for item in seg[_ind]['predicate']]
            else:
                nodes += [int(seg['subject'])]+[int(item) for item in seg['predicate']]
        #print "all nodes from segmentation", index," ", set(nodes)
        left_nodes = set(tl)-(set(nodes))
        #print "left nodes:", left_nodes
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
    else:
        pass
    return ele 


# Need to fix that the subject should be rearrange to an appropriate place
# res is a list of dictionary, containing preprocessed segmentations, where every segment go to an appropriate segmentation with subject 
def Rearrange2(tl,res,left):
    seg = range(len(res)) 
    new_left = range(len(res))
    for index,each in enumerate(left):
        new_left[index] = left_segment(each)
    #print new_left
    for ind, st in enumerate(res):
        #print ind
        # Iterating thru segmentations
        # length of each segmentation(#segments in a segmentation)
        tmp = range(len(st))
        if new_left[ind] is not None: 
            for j in new_left[ind]:
                if j is None:
                    pass
                else: 
                    j.used = False
        else:
            pass 
        for iind in range(0,len(st)):
            #print "curr ind", ind
            # Set fragments are false before iterating thru each segmentation 
            # Otherwise, fragments used before won't be considered again!!! 
            #Iterating thru segments 
            #for iind in range(0,len(i)):
                # because i is a list of dictionary  
            ele = copy.deepcopy(st[iind]['predicate'])
            #print ele
            #print "current element: ", ele
            if new_left[ind] is not None: 
                for j in new_left[ind]:
                    if (j.used == False):
                        #print "current fragment:", j.nodes
                        head = j.nodes[0]
                        tail = j.nodes[len(j.nodes)-1]
                    else:
                        pass
                    # Case 0, special case of case 1, just directly append to the head 
                    # If tails equals the very first word in the very first predicate
                    if (tail+1 == st[iind]['predicate'][0]) and (j.used == False):
                        case = 0
                        Insertion(j,ele,case,tail,head)
                        #print "Hit case 0"
                    elif (j is not None):
                        for iiind in range(0,len(st[iind]['predicate'])):
                            # Case 1, prepend to X+1 
                            if (tail+1 == st[iind]['predicate'][iiind]) and (tail not in ele) and (j.used == False):
                                case = 1
                                ele = Insertion(j,ele,case,tail,head)
                                #print "Hit case 1"
                            # Case 2, append to X-1
                            elif (head-1 ==  st[iind]['predicate'][iiind]) and (head not in ele) and (j.used == False):
                                case = 2 
                                ele = Insertion(j,ele,case,tail,head)
                                #print "Hit case 2"
                            elif (head > st[iind]['predicate'][len(st[iind]['predicate'])-1]) and (j.used == False):
                                case = 3 
                                if iind != len(st)-1:
                                    j.used = False 
                                else:
                                    ele = Insertion(j,ele,case,tail,head)
                                    #print "Hit case 3"
                            elif (tail < st[iind]['predicate'][0]) and (j.used == False):
                                case = 4
                                ele = Insertion(j,ele,case,tail,head)
                                #print "Hit case 4"  
                            else:
                                pass
                #print "element after...", ele 
                tmp[iind] = sorted(ele)
                #print tmp[iind]  
            else:
                pass 
        if new_left[ind] is not None:
            seg[ind] = tmp
            for final in new_left[ind]:
                if final.used == False:
                    print "Fragment in ", ind, " left to be unused: ", final.nodes 
        else:
            seg[ind] = None
    return seg 

# Connect segments and subject 
def Connect_subj(res, seg):
    #final = (range(len(seg)))
    final = [] 
    for ind, st in enumerate(res):
        if seg[ind] is not None:
            tmp = []
            for iind,segt in enumerate(st): 
                #for iind, ii in enumerate(segt):
                subj = segt['subject']
                item = [subj]+ seg[ind][iind] 
                #print "find match: predicate ",seg[ind][iind], "subject: ",subj
                tmp.append(item)
            final.append(tmp)
        else:
            pass  
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
    if len(nl) == 0:
        return None 
    else:
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

def Clean_Duplicate(sets):
    final = [] 
    for st in sets:
        if st not in final:
            final.append(st)
    # After removing the duplicated, start removing combintations that sharing same elements 
    length = {}
    for ind in range(0,len(final)):
        curr_len = len(final[ind])
        if length.has_key(curr_len):
            length[curr_len].append(final[ind])
        else:
            length[curr_len] = []
            length[curr_len].append(final[ind])
    t = {}
    tmp = [] 
    for k,v in enumerate(length):
        # How long is this current length? 
        curr_option = length[v]
        # How many segmentations does this current length share?  
        bound = len(curr_option)
        if bound >= 2:
            #print "bound", bound 
            temp = [] 
            #flag = False
            for ind in range(0,bound):
                if curr_option[ind]:
                    if set(curr_option[ind][0]) not in temp:
                        #print "current index", ind 
                        #print curr_option[ind]
                        temp.append(set(curr_option[ind][0]))
                        #temp.append(set(curr_option[ind][1]))
                        tmp.append(curr_option[ind])
                    else:
                        pass 

    return tmp 