# Author: Yanjun Gao(yug125)
# Last update: July 3,2017 

# SETENCE DECOMPOSITION PARSER 
# This is a script for handling the output from Stanford CoreNLP constutiency parser, dependency parser 
# The script is for sentence decomposition. For a given sentence, we extract a few segmentations which contain different segments  
 
# The code has four main modules: 
# Helper functions: Accessories function for processing the tree
# Algorithm starts: Pull out dependency relations from phrase tress and dependency trees, and compose to segment
# Sentence Segmentation: Rearrange the segment into a complete pieces 
# Main Procedure: A complete pipeline  


from bs4 import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os
#from draft2 import get_segmentation,rearrangement,reorder

fname = sys.argv[1]
sum_index = sys.argv[2]
outpath = sys.argv[3]

summary_index =  sum_index
content = open(fname).read()

#dot = fname.rfind('.')
#fname = fname[:dot]
#dot = fname.rfind('.')
#fname = fname[:dot]
slash = fname.rfind('/')
fname = fname[(slash + 1):]
fname = fname[:-4]
#print fname


obj = ['dobj','iobj','pobj']
subj = ['nsubj','csubj','nsubjpass','csubjpass']
conj = 'conj'
comp = ['comp','acomp','ccomp','xcomp',]
tensed_verb = ['VBZ','VBD','VBP','MD']
sub_conj = ['after', 'although', 'as', 'as if', 'as long as', 'as much as', 'as soon as', 'as though', 'because', 'before', 'even', 'even if', 'even though', 'if', 'if only', 'if when', 'if then', 'inasmuch', 'in order that', 'just as', 'lest', 'now', 'now since', 'now that', 'now when', 'once', 'provided', 'provided that', 'rather that', 'since', 'so that', 'supposing', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'whereas', 'where if', 'wherever', 'whether', 'which', 'while', 'who', 'whoever', 'why']

wl = ['CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NNP','NNPS','PDT','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB']

pl = ['ADJP','ADVP','CONJP','FRAG','INTJ','LST','NAC','NP','NX','PP','PRN','PRT','QP','RRC','UCP','VP','WHADJP','WHAVP','WHNP','WHPP','X']

cl = ['S','SBAR','SBARQ','SINV','SQ']

# Get a set of tags, Pl is phrase tags, Cl is clause tags, Wl is POS tags 
soup = BeautifulSoup(content,'lxml')

basic = []
for links in soup.find_all("dependencies"):
	if links.get("type") == "enhanced-dependencies":
		basic.append(links)

parse = []
for links in soup.find_all("parse"):
	parse.append(links)

"""
=============================== Helper Functions============================
"""
def flatten(sublist):
    return list(chain.from_iterable(item if isinstance(item,Iterable) and not isinstance(item, basestring) else [item] for item in sublist))

# Get arcs and nodes from dependency parser
# Input is a list containing all the enhanced-dependencies
# Output is a dictionary containing all the sentences, with ids 
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

def get_vptree(wholetree):
    tr = wholetree.get_text()
    tr = Tree.fromstring(tr)
    tl,tr,numlist = number_leaves(tr)
    vvps = []
    vps = []
    novps = []
    for subtree in tr.subtrees():
        # if there is vp found, put it into vps
        if subtree.label() == 'VP':
            for i in subtree:
                vps.append(subtree)
                    #vps.append(i)
    # else, if there is no VP found, treat it as own segments  
    if len(vps) == 0:
        for subtree in tr.subtrees():
        # if there is vp found, put it into vps
            if subtree.label() == 'ROOT':
                novps.append(subtree)
    # Filter out those vps with no tensed verbs 
    for i in vps:
        if i[0].label() in tensed_verb:
            vvps.append(i)

    return novps,vvps,tl,tr,numlist 

# Enumerate each leaf in the tree, so the leaves will be [word,number]
# Input is a tree 
# Output is a modified tree:tr, and a list of all nodes:tl  
def number_leaves(tr):
    tl = []
    count = 0
    numlist = []
    for st in tr.subtrees():
        if (st.label() in wl) or (st.label() in string.punctuation):
            count += 1
            ele = [st[-1],count]
            st[-1] = ele
            tl.append(str(count))
            numlist.append(ele)
        else:
            pass 
    return tl, tr, numlist 

#Get a list of node number from subtree, e.g. for i in vps: i, then get_numberlist(i)
def get_numberlist(subtree,tl):
    vpchunk = []
    left_nodes = []
    for i in subtree.leaves():
        if len(i) == 2:
            vpchunk.append(str(i[1]))

    for j in vpchunk:
        if j:
            left_nodes.append(set(tl).difference(set(j))) 
    return vpchunk, left_nodes  

# Get single number list 
def vps_leaf_number(leaves):
    list_id = []
    for i in leaves:
        if len(i) == 2:
            list_id.append(str(i[1]))
    return list_id

def write_log(filename,lines, new_flag=0):
    if new_flag == 1:
        with open(filename, 'w') as f:
            f.write(lines)
    else:
        with open (filename, 'a') as f: 
            f.write(lines)
    f.close()

def write_listlog(filename,lists):
    with open(filename, 'a') as f:
        pickle.dump(lists, f)
    f.close() 


"""
==================================Algorithms Start===========================================
"""
# Very first rule: if there is a subordinating conjunction in the phrase tree, we directly take it as two segments.  
# Indexing to subtrees, find all possible subordinating conjunctions 
def check_IN(tr):
    flag = False 
    sub_sent = []
    for subtree in tr.subtrees():
        if subtree.label() == 'SBAR':
            st = subtree
            if st[0].label() == 'IN':
                if st[0].leaves()[0][0] in sub_conj:
                    sub_sent.append(st)
                    flag = True 
    return flag, sub_sent 
# After making sure there is a subordinating conjunction, start pull it out. 
def Rule_SUBCONJ(sub_sent,tr,tl,numlist):
    seg_ids = []
    seg_sent = []
    for ind in range(0,len(sub_sent)):
        vps,ln = get_numberlist(sub_sent[ind],tl)
        left = list(set(tl)-set(vps))
        vps = [v for v in vps if v != "'"]
        vps = sorted(list(map(int,vps))) 
        left = sorted(list(map(int,left)))  
        seg_ids.append([left,vps])
        seg1 = []
        seg2 = []
        for i in left:
            for j in numlist:
                if j[1] == i:
                    nodes = j[0]
                    seg1.append(nodes)
        for i in vps:
            for j in numlist:
                if j[1] == i:
                    nodes = j[0]
                    seg2.append(nodes)
        seg_sent.append([" ".join(seg1)," ".join(seg2)])  
        return seg_ids, seg_sent


def make_vpsnumber(vps):
    all_nodes = []
    for i in vps:
        if i[0].label() in tensed_verb:
            unit = []
            for j in i.leaves():
                if len(j) == 2:
                    unit.append(str(j[1]))
            all_nodes.append(unit)
    tmp = []
    for i in all_nodes:
        if i not in tmp:
            tmp.append(i)
    return tmp

def pull_vpsnodes(nodes):
    for i in vps:
        for j in i.leaves():
            # Check if it is an empty node
            if len(j) == 2:
                if str(j[1]) == nodes:
                    return j[0]

# New algorithms for finding the arcs, just focus on whether the vps has a subj or obj 
# i is from vps[]
# Output is all dependent(subj,obj,comp,conj) arcs found from all_sents, witharcs is with subj and obj, withoutarcs is with comp and conj 
def find_arcs(i,things,tl):
    # things is from all the dependency parser
    vps_id,left_nodes = get_numberlist(i,tl)
    witharcs = []
    withoutarcs = []
    purevps = []
    for each in things:
        # Iterating inside a vp chunk 
        for every in i.leaves():
            #Case 1, indexing by dep_id
            if len(every) == 2: 
                if str(every[1]) == each['dep_id']:
                    other = each['gov_id']
                    #Check if there is overlap with vps 
                    #Becuase we dont want the noun in vps matched with vps again 
                    if other not in vps_id:
                        if (each['type'] in subj) or (each['type'] == 'expl'):
                            witharcs.append(each)
                        else:
                            # if the type is conj 
                            if (conj in each['type']) or (each['type'] in comp):
                                withoutarcs.append(each)
                            else:
                                purevps.append(each)
                #Case 2, indexing by gov_id
                elif str(every[1]) == each['gov_id']:
                    other = each['dep_id']
                    #Check if there is no overlap with vps  
                    if other not in vps_id:
                        if (each['type'] in subj) or (each['type'] == 'expl'):
                            witharcs.append(each)
                        else:
                            if (conj in each['type']) or (each['type'] in comp):
                                withoutarcs.append(each)
                            else:
                                purevps.append(each)
    return witharcs,withoutarcs, purevps


# Pull out sentences with connection of subj or obj 
# Input should be current node id, and current subtree from vps(leaves are chunks from vps)
# E.G. leaves = i.leaves(), where [[u'contains', 11], [u'both', 12], [u'volume', 13], [u'and', 14], [u'mass', 15]]
def pull_subj_parts(things,leaves,nodes_id,nodes_label,id_list,index,flag):
    all_obj = [] 
    # For connecting the sentences 
    sentmp = []
    # For backup if nothing matched 
    backup = []
    # For recording the ids 
    ids = []
    # For backup if nothing matched 
    backup_id = []
    # Iterating in subtree/leaves  
    anchor = leaves[0][1]
    ##print "anchor of the sentences:",leaves[0][0],anchor 
    for l in leaves:
        if len(l) == 2:
            if (things['dep_id'] == str(l[1])) or (things['gov_id'] == str(l[1])):
                flag = True 
                sentmp.append(nodes_label)
                sentmp.append(" ".join(m[0] for m in leaves))
                ids.append([nodes_id,idlist])
                sentence = "Sentence "+str(index)+" SUBJ/OBJ segment is:" + " ".join(sentmp)+ "\n"
                sent_ids = "cover from:" + str(nodes_id) + ","+ " ".join(id_list) + "\n"
                ##print sentence
                write_log('../ext/' + fname +'_log1.txt',sentence)
                write_log('../ext/' + fname +'_log1.txt',sent_ids)
                all_obj.append([ids, " ".join(sentmp)])
    # If nothing ever got mached, just put it into no-match             
    if flag == False:
        ##print "Not found", " ".join(m[0] for m in leaves)
        write_log('../ext/' + fname +'_log1-no-match.txt'," ".join(m[0] for m in leaves))
        write_log('../ext/' + fname +'_log1-no-match.txt',id_list)
    return ids, all_obj

# Input: woa-without arcs, things-dictionary, leaves-from vps, wordlist-a list of numbers marked as nodes
# Output: all matched id nodes, id nodes and match sentences 
# E.G. leaves = i.leaves(), where [[u'contains', 11], [u'both', 12], [u'volume', 13], [u'and', 14], [u'mass', 15]]
def pull_comp_parts(woa,things,leaves,wordlist,index,flag,nodes_id,nodes_label):
    # For connecting ids with boats 
    all_parts = []
    big_ids = [] 
    backup = []
    backup_id = []
    boat = " ".join(m[0] for m in leaves)
    for k in woa:
        if k['dep_id'] == str(nodes_id):
            # anchor is the verb for connecting arcs and vps 
            anchor = k['gov_id']
            # k['dep_id'], if one of the verb in wordlist, then use the other one to trace the subjects 
            ##print "tracing back by:", anchor
        elif k['gov_id'] == str(nodes_id):
            anchor = k['dep_id']
            # either dep or gov 
            ##print "tracing back by:", anchor
        else:
            anchor = None 
        if anchor is not None:
            for l in things:
                # check if there is an arc marked as subj, expl 
                # A verb with a subject could only be governor 
                if (l['gov_id'] == anchor):
                    if (l['type'] in subj) or (l['type'] == 'expl'):
                        ##print l 
                        flag = True
                        # Find the dependent(subject)! 
                        senten = l['dep'] +" "+ boat
                        big_ids.append([l['dep_id'],wordlist])
                        ##print "COMP/CONJ sentence is", senten
                        ##print "cover from", ids
                        sentence = "Sentence "+str(index)+" COMP/CONJ segment is:" + senten + "\n"
                        sent_ids = "cover from:"+ l['dep_id'] + "," +" ".join(wordlist) + "\n" 
                        write_log('../ext/' + fname +'_log1.txt',sentence)
                        write_log('../ext/' + fname +'_log1.txt',sent_ids)
                        all_parts.append([ids,sentence])
        # If nothing got matched...  
        if flag == False:
            backup.append(boat)
            backup_id.append(wordlist)
            sentence = "Sentence "+str(index)+" segment is:" + boat + "\n"
            sent_ids = "cover from:"+ " ".join(wordlist) + "\n"
            write_log('../ext/' + fname +'_log1-no-match.txt',sentence)
            write_log('../ext/' + fname +'_log1-no-match.txt',sent_ids)
        return big_ids,all_parts 


"""
==================================Sentence Segmentation =======================================
"""
def get_segmentation(all_vpnodes,idseg,tl):
    tmp = []
    result = [] 
    for i in idseg:
        if i not in tmp:
            tmp.append(i)
    idseg = tmp 
    del tmp   
    allvp = []
    for j in all_vpnodes:
        j = [k for k in j if not (k == "'" or k == '`')]
        allvp.append(map(int,j))
    # First pass, check the main vp chunks 
    # Result in final  
    final = {} 
    for i in idseg:
        final = {}
        seg = []
        curr = []
        # Get the current segment 
        # i[0] alwas be the subject connected to the predicates  
        i[1] = [d for d in i[1] if not( d == "'" or d == '`')]
        seg = [int(i[0])]+ [int(item) for item in i[1]]
        ###print "seg", seg
        left = set(tl).difference(set(seg))
        ###print "initial left nodes", left 
        curr.append(seg)
        ###print "initial curr", curr
        for k in allvp:
            if list(left.intersection(set(k))) == k:
                k = set(k)
                for in_curr in curr:
                    k = k.difference(set(in_curr))
                if len(k) != 0:
                    k = list(k)
                    curr.append(k)

        tmp_c = [item for sublist in curr for item in sublist]
        ###print "temp c", tmp_c
        new_left = set(tl).difference(set(tmp_c))
        final['left'] = sorted(list(set(new_left)))  
        final['curr'] = curr
        result.append(final)
    ###print "result:", result 
    return result 

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
    #print ttmp
    for t in ttmp:
        if t not in non_duplicate:
            non_duplicate.append(t)
    #print(non_duplicate)
    tmp.append(non_duplicate)
    #print tmp
    ##print tmp
    return tmp 

def rearrangement(result,punctuation):
    seg = []
    for res in result:
        curr = copy.deepcopy(res['curr'])
        nll = copy.deepcopy(res['left'])
        if nll:
            nl = left_segment(nll)
            ##print "nl",nl 
            tmp = []
            for ind in range(0,len(curr)):
                ele = copy.deepcopy(curr[ind])
                if ind != len(curr)-1:
                    ele2 = copy.deepcopy(curr[ind+1])
                else:
                    ele2 = []
                for j in nl:
                    head = j[0]
                    tail = j[len(j)-1]
                    # Case 0, special case of case 1, just directly append to the head 
                    if tail+1 == curr[ind][0]:
                        for each in j:
                            ele.insert(0,each)
                    else:
                        for iind in range(0,len(curr[ind])):
                            # Case 1, prepend to X+1 
                            if (tail+1 == curr[ind][iind]) and (tail not in ele):
                                position = [i for i,x in enumerate(ele) if x == tail+1]
                                for each in j:
                                    ele.insert(position[0],each)
                            # Case 2, append to X-1
                            elif (head-1 == curr[ind][iind]) and (head not in ele):
                                if ele2:
                                    position = [i for i,x in enumerate(ele2) if x == tail+1]
                                    for each in j:
                                        ele2.insert(0,each)
                                else:
                                    position = [i for i,x in enumerate(ele) if x == head-1]
                                    for each in j:
                                        ele.insert(position[0],each)
                tmp.append(sorted(ele))
            seg.append(tmp)
        else:
            pass 
    ttmp = []
    for i in seg:
        if i not in ttmp:
            ttmp.append(i)
    del seg
    return ttmp

def reorder(tmp):
    tt = []
    for i in tmp:
        ttt = []
        for j in i:
            ttt.append(sorted(j))
        if ttt not in tt:
            tt.append(ttt)
    return tt 

"""
=========================================Main Procedure====================================
""" 
sentence_segmentations = []
all_dep_sent = get_depparse(basic)
write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt', '', 1)
#write_log(outpath +'/'+ fname +'.segs', '', 1)
write_log('../ext/' + fname +'_log1-segment-id-readable.txt', '', 1)
write_log('../ext/' + fname +'_log1-segment-id.txt', '', 1)

seg_dir = outpath +'/'+str(summary_index)
if not os.path.exists(seg_dir):
    os.makedirs(seg_dir)

write_log(seg_dir +'/'+ fname +'.segs', '', 1)

segments = {}
idseg = {}
count = 0 
lists_nodes = {}
segment_set = {}
# Sentence as basic unit
for ind in range(1,len(all_dep_sent)):
    used = False
#for ind in range(1,5):
    tmp_ids = [] 
    tmp = [] 
    things = all_dep_sent[ind]
    novps,vps,tl,tr,numlist = get_vptree(parse[ind-1])
    lists_nodes[ind] = tl  
    all_vpnodes = make_vpsnumber(vps)
    raw_sentence = "===================Raw sentence: "+ " ".join([i[0] for i in numlist]) + " \n"
    write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',raw_sentence)
    raw_sentence = "===================Raw sentence: "+ " ".join([str(i[1]) for i in numlist]) + " \n"
    write_log('../ext/' + fname +'_log1-segment-id-readable.txt',raw_sentence)
    segmentation_count = 0
    segment_count = 0
    # Check the very first case, if there is a subordinating conjunction, if so, write it into log directly 
    subconj_flag,sub_sent = check_IN(tr)
    if subconj_flag == True:
        subconj_seg_ids, subconj_seg_sent = Rule_SUBCONJ(sub_sent,tr,tl,numlist) 
        for kk in range(0,len(subconj_seg_sent[0])):
            output_sentence = "Segment " + str(kk) + " from Sentence "+str(ind)+" :\n " + str(subconj_seg_ids[0][kk])+" \n"
            write_log('../ext/' + fname +'_log1-segment-id-readable.txt',output_sentence)
            # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
            out_sent = summary_index+'&'+str(ind)+'&'+str(segmentation_count)+'&'+str(kk)+'&'+str(subconj_seg_ids[0][kk])+'\n'
            write_log('../ext/' + fname +'_log1-segment-id.txt',out_sent)
            output_sentence1 = "Segmentation " + str(kk) + " from Sentence "+str(ind)+" :\n " + str(subconj_seg_sent[0][kk])+" \n"   
            write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',output_sentence1)
            sentence_segmentations.append(output_sentence1)
            out_sent1 = summary_index+'&'+str(ind)+'&'+str(segmentation_count)+'&'+str(kk)+'&'+str(subconj_seg_sent[0][kk])+'\n'
            write_log(seg_dir +'/'+ fname +'.segs',out_sent1)
            used = True
        segmentation_count += 1 
    # Iterating in a list of vp chunks 
    if vps:
        for i in vps:
            # For indicating if there is a match with current vp chunk 
            flag = False
            # Firstly, get id list 
            idlist = vps_leaf_number(i.leaves())
            # Get three sets of candidates 
            wa,woa,purevps = find_arcs(i,things,tl)
            # For direct subject 
            if len(wa) >0:
                for e in wa:
                    # There must be one of e in the idlist 
                    if e['dep_id'] not in idlist:
                        # a verb used for finding another verb  
                        nodes_id = e['dep_id']
                        nodes_label = e['dep']
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag)
                        ##print "ids", ids
                        for each in ids:
                            tmp_ids.append(each)
                    elif e['gov_id'] not in idlist:
                        nodes_id = e['gov_id']
                        nodes_label = e['gov']
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag)
                        ##print "ids", ids
                        for each in ids:
                            tmp_ids.append(each)
            # For complement, conjunction 
            if len(woa) >0:
                # Mark the current verb as starting node, vp always starts from a verb 
                nodes_id = i.leaves()[0][1]
                nodes_label = i.leaves()[0][0]
                ##print "nodes:", nodes_id, nodes_label
                ids,all_comp = pull_comp_parts(woa,things,i.leaves(),idlist,ind,flag,nodes_id,nodes_label)
                ##print "ids", ids
                for each in ids:
                    tmp_ids.append(each)
            idseg[ind] = tmp_ids
    else:
        idseg[ind] = [int(s) for s in tl] 
    t_seg = []
    for item in idseg[ind]:
        if item not in t_seg:
            t_seg.append(item)
    idseg[ind] = t_seg
    punctuation = int(tl[len(tl)-1])
    tl = map(int,tl)

    # Now, start to pull out the segments from sentences 
    if all_vpnodes:
        segment_count = segmentation_count
        result = get_segmentation(all_vpnodes,idseg[ind],tl)
        res = rearrangement(result,punctuation) 
        #segment_set[ind] = reorder(res)
        segment_set[ind] = res
        for v in segment_set[ind]:
            output_sentence = "Segment " + str(segment_count) + " from Sentence "+str(ind)+" :\n " + str(v)+" \n"
            write_log('../ext/' + fname +'_log1-segment-id-readable.txt',output_sentence)
            for vv in range(0,len(v)):
                out_sent = summary_index+'&'+str(ind)+'&'+str(segment_count)+'&'+str(vv)+'&'+str(v[vv])+'\n'
                write_log('../ext/' + fname +'_log1-segment-id.txt',out_sent)
            segment_count += 1
    else:
        # If already considers the subbordinating conjunction case, then no needs to take the raw sentence as segmentation 
        if subconj_flag == True:
            pass
        # Else, the case we just take whatever it is 
        else:
            kk = 0
            output_sentence = "Segment " + str(kk+1) + " from Sentence "+str(ind)+" :\n " + str(tl)+" \n"
            out_sent = summary_index+'&'+str(ind)+'&'+str(segmentation_count)+ '&'+str(kk)+'&'+str(tl)+'\n'
            write_log('../ext/' + fname +'_log1-segment-id.txt',out_sent)
            segmentation_count += 1

    if all_vpnodes:
        segment_count = segmentation_count
        seg = {}
        for iind in range(0,len(segment_set[ind])):
            unit = []
            for j in segment_set[ind][iind]:
                sent = []
                for every in j:
                    for sin in numlist:
                        if sin[1] == every:
                            sent.append(sin[0])
                sents = " ".join(sent)
                unit.append(sents)
            seg[iind] = unit
        for k,v in seg.items():
            output_sentence = "Segmentation " + str(k+1) + " from Sentence "+str(ind)+" :\n " + str(v)+" \n"   
            write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',output_sentence) 
            for vv in range(0,len(v)):
                # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
                out_sent = summary_index+'&'+str(ind)+'&'+str(segment_count)+'&'+str(vv)+'&'+str(v[vv])+ '\n'  
                write_log(seg_dir +'/'+ fname +'.segs',out_sent)
                used = True
                sentence_segmentations.append(out_sent)

            segment_count += 1

    # The case where there is no vp extracted and matched, so just output the whole sentence 
    else:
        # If already considers the subbordinating conjunction case, then no needs to take the raw sentence as segmentation 
        if subconj_flag == False:
            segmentation_count +=1  
            v = " ".join([item[0] for item in numlist]) 
            output_sentence = "Segmentation 0" + " from Sentence "+str(ind)+" :\n " + v +" \n"
            write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',output_sentence)
            out_sent = summary_index+'&'+str(ind)+'&'+str(segment_count)+'&'+'0'+'&'+v +'\n'
            write_log(seg_dir +'/'+ fname +'.segs',out_sent)
            used = True
            sentence_segmentations.append(out_sent)

        # Else, the case we just take whatever it is 
        else:
            pass 
    if used == False:
        v = " ".join([item[0] for item in numlist]) 
        out_sent = summary_index+'&'+str(ind)+'&'+'0'+'&'+'0'+'&'+v +'\n'
        write_log(seg_dir +'/'+ fname +'.segs',out_sent)














