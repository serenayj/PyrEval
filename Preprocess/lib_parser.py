#    Copyright (C) 2017 Yanjun Gao

#    This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Written by: Purushartha Singh
# Last Update: 07/04/19
# The code is written with Yanjun Gao's package by the same name as reference

# Libraries needed: bs4(beautifulSoup4), nltk

###################################################################################################
# Library for the sentparser script
###################################################################################################


import copy
import csv
import itertools
import os
import re
import string
import sys
from bs4 import BeautifulSoup
from nltk.tree import Tree

# GLOBAL LISTS
tensed_verb = ['VBZ','VBD','VBP','MD']
wl = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS',
      'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP',
      'WP$', 'WRB']
subj = ['nsubj','csubj','nsubjpass','csubjpass']
comp = ['comp','acomp','ccomp','xcomp']
sub_conj = ['because', 'while', 'since', 'even', 'if', 'rather']

###################################################################################################
# GENERAL HELPER FUNCTIONS
###################################################################################################

# A function to assist with isolating the filename
# Input: the file name with directory and extension
# Output: The file name with directory and extension removed
def getFilename(name):
    ext = name.rfind('.')
    name = name[:ext]
    if sys.platform == 'win32':
        root = name.rfind('\\')
    else:
        root = name.rfind('/')
    name = name[(root + 1):]
    return name


# Output storing function. Stores the output in the specified file in the right format
# Input: the opened file to store the information in, summary index, sentence index, segmentation index, segment index,
#        and a list of tagged words with each element of the format [num, word]
# Output: None
def outputSegs(file, sum_ind, sent_ind, segmt_ind, seg_ind, textArray):
    text = ""
    textArray.sort(key = lambda x:x[1])
    for i in textArray:
        if i[0] in string.punctuation or text == "":
            text = text + i[0]
        else:
            text = text + " " + i[0]
    file.write(str(sum_ind) + '&' + str(sent_ind) + '&' + str(segmt_ind) + '&' + str(seg_ind) + '&' + text + '\n')
    # print("segment " + str(seg_ind) + " : " + text)


# A function to get the difference and common elements of two lists
# Input: 2 lists
# Output: The set difference and set intersection of the two lists
def difference(list1, list2):
    diff = list(set(list2) - set(list1))
    cover = list(set(list1).intersection(set(list2)))
    # print "cover, ", cover
    return diff, cover


###################################################################################################
# Parsing Helper Functions
###################################################################################################


# Get arcs and nodes from dependency parser
# Input : List containing all the enhanced-dependencies
# Output : A dictionary containing all the sentences, with ids
def get_depparse(enhanced):
    count = 0
    all_sent = {}
    for each in enhanced:
        count += 1
        ttmp = []
        m = each.find_all("dep")
        count_arc = 1
        for i in m:
            tmp = {}
            tmp['arc_id'] = count_arc
            tmp['type'] = i.get("type")
            tmp['gov'] = i.find("governor").get_text()
            tmp['gov_id'] = i.find("governor").get('idx')
            tmp['dep'] = i.find("dependent").get_text()
            tmp['dep_id'] = i.find("dependent").get('idx')
            ttmp.append(tmp)
            count_arc += 1
        all_sent[count] = ttmp

    return all_sent


###################################################################################################
# Tree helper functions
###################################################################################################

# Modifies the tree to include all the node indices in each node alongside list of all the leaves
# and index list of all the leaves
# Input: tree without node indices
# Output: tree with node indices, list of all the indices of the tree, & list of all nodes of tree
def getTreeInfo(tree):
    tree = tree.get_text()
    tree = Tree.fromstring(tree)
    treeList = []
    count = 0
    numList = []

    for st in tree.subtrees():
        if (st.label() in wl) or (st.label() in string.punctuation):
            count += 1
            tmp = [st[-1], count]
            st[-1] = tmp
            treeList.append(str(count))
            numList.append(tmp)

    return tree, treeList, numList


# Splits the input tree into constituent trees for any sibling S or SBAR tags as a child of S
# Input: tree
# Output: list of subtrees which have been split from the original tree as per the rules
def compoundSplit(tree):
    patternSBAR = re.compile("^\(S.*\n(  \(.+\)\n)*  \(SBAR(\n    .*)*(\n  \(.+\))*\n  \(SBAR(\n    .*)*")
    patternS = re.compile("^\(S\n(  \(.+\)\n)*  \(S(\n    .*)*(\n  \(.+\))*\n  \(S(\n    .*)*")
    nosplitflag = False
    splits = []

    # Checks the S sibling relation
    for st in tree.subtrees():
        # print str(st)
        if patternS.match(str(st)):
            for i in range(len(st)):
                if st[i].label() == "S":
                    if len(st[i].leaves()) > 2:
                        splits.append(st[i])

    # Checks for embedded cases and if present removes the parent tree
    for each in splits:
        for tr in splits:
            if each in tr.subtrees() and each != tr:
                splits.remove(tr)

    if len(splits) is 0:
        splits.append(tree)
        nosplitflag = True

    # For each split subtree, checks SBAR sibling relation
    for x in splits:
        for st in x.subtrees():
            if patternSBAR.match(str(st)):
                dellist = []
                skipflag = False
                for i in range(len(st)):
                    if st[i].label() == "SBAR" and len(st[i].leaves()) > 2:
                        splits.append(st[i])
                        dellist.append(i)
                    else:
                        skipflag = True
                dellist.sort(reverse=True)
                for j in dellist:
                    del st[j]
                if skipflag:
                    if len(x.leaves()) > 5:
                        splits.append(x)
                else:
                    if len(x.leaves()) > 3:
                        splits.append(x)

    if nosplitflag:
        splits = splits[1:]
    res = []
    for each in splits:
        if each not in res:
            res.append(each)
    return res


# For each input subtree, makes the list of all the leaves and indices of the leaves
# Input: List of subtrees and list of the root tree nodes
# Output: List of node lists for each segment and list of index list for each segment
def makeSubtreeList(subtrees, numlist):
    sublists = []
    for each in subtrees:
        ele = [item[1] for item in each.leaves()]
        sublists.append(ele)
    sentence_list = [item[1] for item in numlist]
    ind = 0
    segment_list = []
    # Find all the nodes which are not present in any tree
    sublists.sort(key=len)
    while ind < len(sublists):
        sentence_list, cover = difference(sublists[ind], sentence_list)
        segment_list.append(sorted(cover))
        ind += 1

    segment_list = includeAll(segment_list, sentence_list)
    segments = makeSegs(segment_list, numlist)

    return segments, segment_list


# Includes any leftover nodes currently not in any of the segments based on proximity to segments
# Input: List of all the segments, list of root tree nodes, nodes which are not in any segment
# Output: List of all the segments with the leftover nodes appended
def includeAll(segment_list, left):
    left.sort()
    while len(left) > 0:
        for x in left:
            for lst in segment_list:
                if x + 1 in lst or x - 1 in lst:
                    lst.append(x)
                    left.remove(x)
                    break

    return segment_list


# Makes node lists out of node index lists
# Input: List of segment node indices, List of root tree nodes
# Output: List of segment tree nodes
def makeSegs(seglist, numlist):
    segments = []
    for seg in seglist:
        tmp = []
        for element in seg:
            for i in numlist:
                if i[1] == element:
                    tmp.append(i)
        segments.append(tmp)
    return segments


# Recursively combines given segments with adjacent segments
# Input: list of 2 or more segments
# Output: list of segment combinations with all adjacent segments combined,
#         and list of all the segment ids which were combined
def combineSegs(segments):
    result = []
    result_index = []

    # Loop to find permutations of size 2 to (no. of segments - 1)
    for n in range(2, len(segments)):
        tmp = []
        tmp_index = []

        # Generates combinations of segments
        x = itertools.combinations(segments, n)
        y = itertools.combinations(range(len(segments)), n)

        # Joins the combination lists and converts them to list of lists format
        for each in x:
            tmp.append(list(each))
        for each in tmp:
            a = []
            for i in each:
                a = a + i
            result.append(a)
        for each in y:
            result_index.append(list(each))

    # Removes the combinations which are not adjacent
    for i in range((len(result_index) - 1), -1, -1):
        for j in range(len(result_index[i]) - 1):
            if abs(result_index[i][j] - result_index[i][j + 1]) > 1:
                del result[i]
                del result_index[i]
    combineRes = []

    # Makes list of segmentation combinations
    for i, lst in enumerate(result):
        tmp = []
        tmp.append(lst)
        for j, each in enumerate(segments):
            if j not in result_index[i]:
                tmp.append(each)
        combineRes.append(tmp)

    return combineRes, result_index


# Combines multiple segs (including combined segs) into a list contating each segment at least once
# Input: List of all the segments that need to be combined, list of segs which are from the same initial segment
# Output: List of all possible combinations of the segments except the ones which were already in the same seg
def combineSplitSegs(segments, samesegs):
    lsts, lst_combs = combineSegs(segments)
    x = len(lst_combs)-1
    for i in range(x, -1, -1):
        if lst_combs[i] == samesegs:
            del lst_combs[i]
            del lsts[i]
    return lsts

###################################################################################################
# Special Subclauses Rules
###################################################################################################

# Checks for the dependent sub clause rule
# Input: Tree to check the rule in and list of all nodes of the tree
# Output: List of subtrees which are considered dependent subclauses, and list of the subtree indices
def ruleSBAR(tr, numlist):
    candidate = []
    cand_pos = []
    pattern = re.compile("^\(VP\n(  \(.+\)\n)*  \(SBAR.*")
    vp_flag = False
    
    # Checks for non VP child SBAR subtrees to split from the root tree
    for i, st in enumerate(tr.subtrees()):
        if i == 0 or len(st.leaves()) < 3:
            continue
        if pattern.match(str(st)):
            vp_flag = True
        if st.label() == "SBAR" and st not in candidate:
            if vp_flag is True:
                vp_flag = False
                if st.leaves()[0][0] in sub_conj:
                    #print st.leaves()[0][0]
                    pass
                else:
                    continue
            if len(st.leaves()) > 2 and len(st.leaves()) + 2 < len(tr.leaves()):
                candidate.append(st)

    if len(candidate) == 0:
        return [], []
    #print("Number of dependent sbar clauses: " + str(len(candidate)))
    segments = []
    for item in candidate:
        segments.append(item.leaves())
 
    
    # Finds the remaining nodes after removing the split subtree
    valids = []
    for each in segments:
        ele = [item[1] for item in each]
        valids.append(ele)
    list2 = [item[1] for item in numlist]
    ind = 0
    result = []
    valids.sort(key=len)
    while ind < len(valids):
        list2, cover = difference(valids[ind], list2)
        if cover:
            result.append(sorted(cover))
        ind += 1
    result.append(sorted(list2))
    
    
    
    result_val = makeSegs(result, numlist)
    return result, result_val


# Rejoins the split up segments with other segments to make a complete segmentation
# Input: List of all the splits that have occured (with rule split occurance seg number indicated),
#        and list of all the original split segments
# Output: List of all the segments with the rule split segs instead of the non split seg and index list of rule segs
def rejoinRuleSplits(rulesentences, segments):
    result = []
    sameseg = []
    # Loops through eac sentence rule split and makes a list of segments including the split seg instead of the original
    for each in rulesentences:
        tmp = []
        counter = 0
        sameseglst = []
        for i, seg in enumerate(segments):
            if i == each[2]:
                for split in each[1]:
                    tmp.append(split)
                    sameseglst.append(counter)
                    counter += 1
            else:
                tmp.append(seg)
                counter += 1
        result.append(tmp)
        sameseg.append(sameseglst)
    return result, sameseg


# Finds list of subtrees of the tree which are conjoined verb phrases
# Input: Tree
# Output: List of subtrees which are conjoined verb phrases
def getcvps(tree):
    lst = []
    for st in tree.subtrees():
        if st.label() == "VP":
            tmp = []
            count = 0 
            for i in range(len(st)):
                if st[i].label() == "VP" and st[i][0].label() in tensed_verb:
                    count += 1
                    tmp.append(st[i])
            if count > 1:
                for each in tmp:
                    lst.append(each)
    return lst

# Finds all subtrees with noun phrases
# Input: tree
# Output: List of all subtrees with NP as root
def getnp(tree):
    lst = []
    for st in tree.subtrees():
        if st.label() == "NP":
            lst.append(st)

    return lst

# Finds the dependency of the verb in the conjoined VP tree
# Input: the VP tree, list of all the dependencies, and list of indexes in the segment tree
# Output: Returns the value of the dependency if it is in the segment and not in the VP tree itself, else returns -1
def getdependency(tree, dependencies, fulltreelist):
    treelist = [item[1] for item in tree.leaves()]
    for lf in tree.leaves():
        for each in dependencies:
            if str(lf[1]) == each['gov_id'] and each['type'] in subj:
                dependent = int(each['dep_id'])
                if dependent not in treelist and dependent in fulltreelist:
                    return dependent
    return -1


# Finds the NP associated with the dependency id
# Input: the node id and a list of all the NP trees
# Output: the NP containing the node id
def findnp(dep, trees):
    for each in trees:
        nodelist = [item[1] for item in each.leaves()]
        if dep in nodelist:
            return each
    return -1

# Joins the NP tree leaves and VP tree leaves
# Input: list of all the VP and NP pairs
# Output: list of combined pair segments and index list of combined pair segments
def joinTree(trees):
    lst = []
    for each in trees[0].leaves():
        lst.append(each)
    for each in trees[1].leaves():
        lst.append(each)
    lst_ind = [item[1] for item in lst]
    return lst, lst_ind


# Adds the leftover nodes to existing segments
# Input: List of existing segments, list of segment indices, list of root segment indices,
#        and list of root segment nodes
# Output: List of segments with extra nodes appended, Index list of segments with extra nodes appended
def addAll(treelists, treelists_ind, segmentlist, st):
    segcover = []
    for each in treelists_ind:
        segcover = segcover+each
    left = list(set(segmentlist)-set(segcover))
    leftnodes = []
    for each in left:
        for lf in st:
            if lf[1] == each:
                leftnodes.append(lf)
    while len(leftnodes) > 0:
        for node in leftnodes:
            for i, lst in enumerate(treelists_ind):
                if node[1] + 1 in lst or node[1] - 1 in lst:
                    treelists[i].append(node)
                    lst.append(node[1])
                    leftnodes.remove(node)
                    break
    return treelists, treelists_ind

def splitAll(list1, list2, treelist):
    res = []
    splitadd = False
    vpconjlists = []
    for each in list2:
        tmp = []
        for ind in each[1].leaves():
            tmp.append(ind[1])
        vpconjlists.append(tmp)
    leftovers = []
    x = set(vpconjlists[0]) | set(vpconjlists[1])
    if len(vpconjlists) > 2:
        for each in vpconjlists:
            x = x | set(each)
    for each in list1:
        if x.issubset(set(each)):
            leftovers = list(set(each)-x)
            splitadd = True
        else:
            res.append(each)
    if splitadd:
        for each in list2:
            _, vpconj = joinTree(each)
            vpconj = list(set(leftovers + vpconj))
            res.append(vpconj)
        
        res_vals = makeSegs(res, treelist)
        return res, res_vals, True
    else:
        return [],[],False


