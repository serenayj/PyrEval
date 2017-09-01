# Author: Yanjun Gao(yug125)
# Last update: Aug 20,2017 

# SETENCE DECOMPOSITION PARSER 
# This is a script for handling the output from Stanford CoreNLP constutiency parser, dependency parser 
# The script is for sentence decomposition. For a given sentence, we extract a few segmentations which contain different segments  
 
# The code has four main modules: 
# Helper functions: Accessories function for processing the tree
# Algorithm starts: Pull out dependency relations from phrase tress and dependency trees, and compose to segment
# Sentence Segmentation: Rearrange the segment into a complete pieces 
# Main Procedure: A complete pipeline  

# TO-DO list:
# csubj case
# subject assignment 


from bs4 import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os
from lib_parser import * 
from rearrange import *

#from draft2 import get_segmentation,rearrangement,reorder

fname = sys.argv[1]
sum_index = sys.argv[2]
outpath = sys.argv[3]

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
sub_conj = ['after', 'although', 'as', 'as if', 'as long as', 'as much as', 'as soon as', 'as though', 'because', 'before', 'even', 'even if', 'even though', 'if', 'if only', 'if when', 'if then', 'inasmuch', 'in order that', 'just as', 'lest', 'now', 'now since', 'now that', 'now when', 'once', 'provided', 'provided that', 'rather that', 'since', 'so that', 'supposing', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'whereas', 'where if', 'wherever', 'whether', 'which', 'while', 'who', 'whoever', 'why','but']

wl = ['CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NNP','NNPS','PDT','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB']

pl = ['ADJP','ADVP','CONJP','FRAG','INTJ','LST','NAC','NP','NX','PP','PRN','PRT','QP','RRC','UCP','VP','WHADJP','WHAVP','WHNP','WHPP','X']

cl = ['S','SBAR','SBARQ','SINV','SQ']

pausing_point = [',',':',';']

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
=========================================Main Procedure====================================
""" 
   

sentence_segmentations = []
all_dep_sent = get_depparse(basic)
write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt', '', 1)
write_log('../ext/' + fname +'_log1-segment-id-readable.txt', '', 1)
write_log('../ext/' + fname +'_log1-segment-id.txt', '', 1)

summary_index = str(sum_index)
seg_dir = outpath +'/'+str(sum_index)
if not os.path.exists(seg_dir):
    os.makedirs(seg_dir)

write_log(seg_dir +'/'+ fname +'.segs', '', 1)

segments = {}
idseg = {}
count = 0 
lists_nodes = {}
segment_set = {}
# Sentence as basic unit, ind is sentence id 
for ind in range(1,len(all_dep_sent)):
    used = False
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
    # Dumb rule: split the sentence by pausing point
    #sl,il,comma_flag = Rule_COMMA(numlist,pausing_point)
    comma_flag = False 
    # Stop using comma flag 
    if comma_flag:
        for comma_ind in range(0,len(sl)):
            output_sentence = "Segment " + str(comma_ind) + " from Sentence "+str(ind)+" :\n " + str(il[comma_ind])+" \n"
            write_log('../ext/' + fname +'_log1-segment-id-readable.txt',output_sentence)
            out_sent = summary_index+'&'+str(ind)+'&'+str(segmentation_count)+'&'+str(comma_ind)+'&'+str(il[comma_ind])+'\n'
            write_log('../ext/' + fname +'_log1-segment-id.txt',out_sent)
            output_sentence1 = "Segmentation " + str(comma_ind) + " from Sentence "+str(ind)+" :\n " + str(sl[comma_ind])+" \n"   
            write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',output_sentence1)
            sentence_segmentations.append(output_sentence1)
            out_sent1 = summary_index+'&'+str(ind)+'&'+str(segmentation_count)+'&'+str(comma_ind)+'&'+str(sl[comma_ind])+'\n'
            write_log(seg_dir +'/'+ fname +'.segs',out_sent1)
            #used = True
            # even though we are able to split the sentence by pausing point, we also need the raw sentence
    #segmentation_count += 1
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
                        #print "nodes id", nodes_id
                        nodes_label = e['dep']
                        #print "nodes label", nodes_label
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag)
                        #print "ids, dep ", ids
                        ##print "ids", ids
                        for each in ids:
                            tmp_ids.append(each)
                    elif e['gov_id'] not in idlist:
                        nodes_id = e['gov_id']
                        nodes_label = e['gov']
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag)
                        #print "ids gov", ids
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
        #result = get_segmentation(all_vpnodes,idseg[ind],tl)
        #res = rearrangement(result,punctuation) 
        #segment_set[ind] = reorder(res)
        _idseg = RemakeSegStructure(idseg[ind])
        seg_combo = get_segmentation3(_idseg)
        new_idseg = Make_New_Segt(seg_combo,_idseg)
        left = get_left(new_idseg,tl)
        segs = Rearrange2(tl,new_idseg,left)
        final = Connect_subj(new_idseg,segs)
        segment_set[ind] = final
        for v in segment_set[ind]:
            output_sentence = "Segment " + str(segment_count) + " from Sentence "+str(ind)+" :\n " + str(v)+" \n"
            write_log(ext+'/' + fname +'_log-segment-id-readable.txt',output_sentence)
            for vv in range(0,len(v)):
                out_sent = summary_index+'&'+str(ind)+'&'+str(segment_count)+'&'+str(vv)+'&'+str(v[vv])+'\n'
                #write_log(ext+'/' + fname +'_log-segment-id.txt',out_sent)
            segment_count += 1
    else:
        # If already considers the subbordinating conjunction case, then no needs to take the raw sentence as segmentation 
        if subconj_flag == True:
            pass
        # Else, the case we just take whatever it is 
        else:
            kk = 0
            output_sentence = "Segment " + str(kk+1) + " from Sentence "+str(ind)+" :\n " + str(tl)+" \n"
            out_sent = summary_index+'&'+str(ind)+'&'+str(segment_count)+ '&'+str(kk)+'&'+str(tl)+'\n'
            write_log('../ext/' + fname +'_log1-segment-id.txt',out_sent)
            segment_count += 1

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

    # The case where there is no tempracted and matched, so just output the whole sentence 
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














