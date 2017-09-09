from bs4 import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os


obj = ['dobj','iobj','pobj']
subj = ['nsubj','csubj','nsubjpass','csubjpass']
conj = 'conj'
comp = ['comp','acomp','ccomp','xcomp',]
tensed_verb = ['VBZ','VBD','VBP','MD']
sub_conj = ['after', 'although', 'as', 'because', 'before', 'even','if', 'inasmuch', 'lest', 'now', 'once', 'provided', 'since', 'supposing', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'whereas', 'where if', 'wherever', 'whether', 'which', 'while', 'who', 'whoever', 'why']

wrb = ['WHADJP','WHAVP','WHNP','WHPP']

wl = ['CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NNP','NNPS','PDT','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB']

pl = ['ADJP','ADVP','CONJP','FRAG','INTJ','LST','NAC','NP','NX','PP','PRN','PRT','QP','RRC','UCP','VP','WHADJP','WHAVP','WHNP','WHPP','X']

cl = ['S','SBAR','SBARQ','SINV','SQ']


"""
=============================== Helper Functions============================
"""

class SubVerbPhrase():
    def __init__(self,child,parent,subject):
        self.child = child
        self.parent = parent
        self.subject = subject
    def IsSubPhrase(self):
        if set(self.parent) > set(self.child):
            return True 
        else:
            return False

            
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
    embed_vps =[]
    for subtree in tr.subtrees():
        # if there is vp found, put it into vps
        if subtree.label() == 'VP':
            for i in subtree:
                vps.append(subtree)
                if i.label() == 'VP':
                    embed_vps.append(i)
                    #vps.append(i)
    # else, if there is no VP found, treat it as own segments  
    if len(vps) == 0:
        for subtree in tr.subtrees():
        # if there is vp found, put it into vps
            if subtree.label() == 'ROOT':
                novps.append(subtree)
    # Filter out those vps with no tensed verbs 
    for i in vps:
        if (i[0].label() in tensed_verb) and (i not in vvps):
            vvps.append(i)
    return novps,vvps,embed_vps,tl,tr,numlist

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

def Make_SubVP(embedvps):
    embed_vps = make_vpsnumber(embedvps)
    tmp = [] 
    for i in range(0,len(embed_vps[:-1])):
        for j in range(1,len(embed_vps)-1):
            if len(embed_vps[i]) > len(embed_vps[j]):
                subvp = SubVerbPhrase(embed_vps[j],embed_vps[i],None)           
                if subvp.IsSubPhrase() == True:
                    tmp.append(subvp)
            else:
                subvp = SubVerbPhrase(embed_vps[i],embed_vps[j],None)
                if subvp.IsSubPhrase() == True:    
                    tmp.append(subvp)
    return tmp 

def Update_Parent_Subject(ids,sub_vps):
    for lst in ids:
        predicate = lst[1]
        subject = lst[0]
        for subvp in sub_vps:
            parent = subvp.parent
            if predicate == parent:
                subvp.subject = subject
    return sub_vps 

def Update_Child_Subject(ids,sub_vps):
    final = [] 
    for lst in ids:
        predicate = lst[1]
        subject = lst[0]
        for subvp in sub_vps:
            child = subvp.child
            if predicate == child:
                subject = subvp.subject
            else:
                pass
        item = [subject,predicate]
        if item not in final:
            final.append(item)
    return final 

def get_SBAR(tr):
    class _Node:
        def __init__(self, data, next):
            self.node = data
            self.neighbor = next
        def isCousin(self):
            # Although most cases SBAR will be on the right-hand side of NP 
            if (self.node == "NP") and (self.neighbor == "SBAR"):
                return True 
            elif (self.node == "VP") and (self.neighbor == "SBAR"):
                return True 
            else:
                return False

    sbar = [] 
    flag = False 
    for st in tr.subtrees():
        if len(st) > 1:
            for ind in range(len(st)):
                if ind != (len(st)-1): 
                    node = st[ind].label()
                    next = st[ind+1].label()
                    nodes = _Node(node,next)
                    if nodes.isCousin() == True:
                        flag = True 
                        if st[ind].label() == 'SBAR':
                            sbar.append(st[ind])
                        elif st[ind+1].label() == 'SBAR':
                            sbar.append(st[ind+1])
    return flag,sbar


def Pull_Words(segment_set,ind,numlist):
    seg = {}
    for iind in range(0,len(segment_set[ind])):
        unit = []   
        for j in segment_set[ind][iind]:
            sent = []
            for every in j:
                for single in numlist:
                    if single[1] == every:
                        sent.append(single[0])
                sents = " ".join(sent)
            unit.append(sents)
        seg[iind] = unit
    return seg 

def Format_Sentence(mode, label, sum_ind,sent_ind,segmt_ind,seg_ind):
    # Sentence for id-readable file
    if mode == 1:
        sentence = "Segment " + str(seg_ind) + " from Sentence "+str(sent_ind)+" :\n " + str(label)+" \n"
    # Sentence for sent-readable file 
    elif mode == 2:
        sentence = "Segmentation " + str(segmt_ind) + " from Sentence "+str(sent_ind)+" :\n " + str(label)+" \n"  
    # Sentence for segment file 
    elif mode == 3:
        sentence = str(sum_ind)+'&'+str(sent_ind)+'&'+str(segmt_ind)+'&'+str(seg_ind)+'&'+str(label)+'\n'
    return sentence  

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
                    print "Found subbordinating conjunction!!!:", st[0].leaves()[0][0]
                    sub_sent.append(st)
                    flag = True 
    return flag, sub_sent 

# Also dumb rule: if there is comma conjunction, we split the sentence by comma 
def Rule_COMMA(numlist,pausing_point):
    sl = [] 
    il = []
    flag = False 
    raw_sent = " ".join(str(i[0]) for i in numlist)
    for pt in pausing_point:
        if pt in raw_sent:
            flag = True 
    if flag:
        ii=0
        for j in range(0,len(numlist)):
            if numlist[j][0] in pausing_point:
                sl.append(" ".join([str(i[0]) for i in numlist[ii:numlist[j][1]]]))
                il.append([i[1] for i in numlist[ii:numlist[j][1]]])
                ii = j+1
            if j == len(numlist)-1:
                sl.append(" ".join([str(i[0]) for i in numlist[ii:]]))
                il.append([i[1] for i in numlist[ii:]])
    return sl,il,flag    

# After making sure there is a subordinating conjunction, start pull it out. 
def Rule_SUBCONJ(sub_sent,tr,tl,numlist):
    seg_ids = []
    seg_sent = []
    for ind in range(0,len(sub_sent)):
        vps,ln = get_numberlist(sub_sent[ind],tl)
        left = list(set(tl)-set(vps))
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

# sbar_flag, sbar = get_SBAR(tr)
# if sbar_flag == True
def Rule_NPSBAR(tr,tl,sbar,numlist):
    seg_ids = []
    seg_sent = []
    # In case it contains multiple 
    seg_sbar = [] 
    for ind in range(0,len(sbar)):
        vps,ln = get_numberlist(sbar[ind],tl)
        left = list(set(tl)-set(vps))
        vps = sorted(list(map(int,vps))) 
        left = sorted(list(map(int,left)))  
        #print left 
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
def pull_subj_parts(things,leaves,nodes_id,nodes_label,id_list,index,flag,fname):
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
                ids.append([nodes_id,id_list])
                #print "current ids", ids
                sentence = "Sentence "+str(index)+" SUBJ/OBJ segment is:" + " ".join(sentmp)+ "\n"
                sent_ids = "cover from:" + str(nodes_id) + ","+ " ".join(id_list) + "\n"
                print sentence
                write_log('../ext/' + fname +'_log1.txt',sentence)
                write_log('../ext/' + fname +'_log1.txt',sent_ids)
                all_obj.append([ids, " ".join(sentmp)])
                #print "what is inside all_obj", all_obj
    # If nothing ever got mached, just put it into no-match             
    if flag == False:
        ##print "Not found", " ".join(m[0] for m in leaves)
        write_log('../ext/' + fname +'_log1-no-match.txt'," ".join(m[0] for m in leaves))
        write_log('../ext/' + fname +'_log1-no-match.txt',id_list)
    return ids, all_obj

# Input: woa-without arcs, things-dictionary, leaves-from vps, wordlist-a list of numbers marked as nodes
# Output: all matched id nodes, id nodes and match sentences 
# E.G. leaves = i.leaves(), where [[u'contains', 11], [u'both', 12], [u'volume', 13], [u'and', 14], [u'mass', 15]]
def pull_comp_parts(woa,things,leaves,wordlist,index,flag,nodes_id,nodes_label,fname):
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
            #print "tracing back by: dep", anchor
        elif k['gov_id'] == str(nodes_id):
            anchor = k['dep_id']
            # either dep or gov 
            #print "tracing back by: gov", anchor
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
                        sentence = "Sentence "+str(index)+" COMP/CONJ segment is:" + senten + "\n"
                        sent_ids = "cover from:"+ l['dep_id'] + "," +" ".join(wordlist) + "\n" 
                        write_log('../ext/' + fname +'_log1.txt',sentence)
                        write_log('../ext/' + fname +'_log1.txt',sent_ids)
                        all_parts.append([big_ids,sentence])
        # If nothing got matched...  
        if flag == False:
            backup.append(boat)
            backup_id.append(wordlist)
            sentence = "Sentence "+str(index)+" segment is:" + boat + "\n"
            sent_ids = "cover from:"+ " ".join(wordlist) + "\n"
            write_log('../ext/' + fname +'_log1-no-match.txt',sentence)
            write_log('../ext/' + fname +'_log1-no-match.txt',sent_ids)
        return big_ids,all_parts 

def Rule_EmbeddedVP(embedvps,tr,tl,numlist,things,ind,fname):
    sub_vps = Make_SubVP(embedvps) 
    tmp_ids = []
    # Step 0:
    main_clause = [] 
    subconj_flag, sub_sent = check_IN(tr)
    if subconj_flag == True:
        for ind in range(0,len(sub_sent)):
            part,ln = get_numberlist(sub_sent[ind],tl)
            prefix = list(set(tl).difference(set((map(int,part)))))
            tmp_subj = pull_subj(things,prefix)
            tmp_pred = [x for x in prefix if x != tmp_subj]
            _struct = [str(tmp_subj),map(str,tmp_pred)] 
            main_clause.append(_struct)
    else:
        pass 
    #the i here is a subtree 
    # Step 1: select subject from arcs relations
    flag = False 
    for i in embedvps:
        idlist = vps_leaf_number(i.leaves())
        wa,woa,purevps = find_arcs(i,things,tl)
        if len(wa) >0:
            for e in wa:
                # There must be one of e in the idlist 
                if e['dep_id'] not in idlist:
                    # a verb used for finding another verb  
                    nodes_id = e['dep_id']
                    nodes_label = e['dep']
                    ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
                    print ids 
                    for each in ids:
                        tmp_ids.append(each)
                elif e['gov_id'] not in idlist:
                    nodes_id = e['gov_id']
                    nodes_label = e['gov']
                    ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
                    for each in ids:
                        tmp_ids.append(each)
        # For complement, conjunction 
        if len(woa) >0:
            # Mark the current verb as starting node, vp always starts from a verb 
            nodes_id = i.leaves()[0][1]
            nodes_label = i.leaves()[0][0]
            ids,all_comp = pull_comp_parts(woa,things,i.leaves(),idlist,ind,flag,nodes_id,nodes_label,ext,fname)
            for each in ids:
                tmp_ids.append(each)
    # Step 2: settle down subjects from embeded vp relations
    sub_vps = Update_Parent_Subject(tmp_ids,sub_vps)
    final = Update_Child_Subject(tmp_ids,sub_vps)
    if subconj_flag == True:
        final += main_clause
    else:
        pass
    return final  

def RemakeSegStructure(idseg):
    tmp = []
    for i in idseg:
        print "test i", i
        pre = [int(x) for x in i[1]]
        item = {'subject':int(i[0]),'predicate':pre}
        tmp.append(item)
    return tmp 