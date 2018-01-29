# Author: Yanjun Gao(yug125)
# Last update: Aug 20,2017 

# SETENCE DECOMPOSITION PARSER 
# This is a script for handling the output from Stanford CoreNLP constutiency parser, dependency parser 
# The script is for sentence decomposition. For a given sentence, we extract a few segmentations which contain different segments  

#Copyright (C) 2017  Yanjun Gao

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

 
# The code has four main modules: 
# Helper functions: Accessories function for processing the tree
# Algorithm starts: Pull out dependency relations from phrase tress and dependency trees, and compose to segment
# Sentence Segmentation: Rearrange the segment into a complete pieces 
# Main Procedure: A complete pipeline  




from bs4 import BeautifulSoup
#import BeautifulSoup
import csv
from nltk.tree import Tree 
import string
import pickle
import copy
import sys
import os
from lib_parser import * 
from rearrange import *
from sbar import * 

#from draft2 import get_segmentation,rearrangement,reorder

fname = sys.argv[1]
sum_index = sys.argv[2]
outpath = sys.argv[3]

#fname = "wise_crowd_summaries/2.stseg.txt.xml"
#sum_index = 2 
#outpath = 'wise_crowd_summaries'+ str(2)+'/'
content = open(fname).read()

#dot = fname.rfind('.')
#fname = fname[:dot]
#dot = fname.rfind('.')
#fname = fname[:dot]
slash = fname.rfind('/')
fname = fname[(slash + 1):]
fname = fname[:-4]
#print fname



# Get a set of tags, Pl is phrase tags, Cl is clause tags, Wl is POS tags 
soup = BeautifulSoup(content,'lxml')

basic = []
for links in soup.find_all("dependencies"):
    if links.get("type") == "enhanced-dependencies":
        basic.append(links)

parse = []
for links in soup.find_all("parse"):
    parse.append(links)

tokens = soup.find_all("tokens")

"""
=========================================Main Procedure====================================
""" 
   

sentence_segmentations = []
all_dep_sent = get_depparse(basic)
#write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt', '', 1)
#write_log('../ext/' + fname +'_log1-segment-id-readable.txt', '', 1)
#write_log('../ext/' + fname +'_log1-segment-id.txt', '', 1)

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
for ind in range(1,len(all_dep_sent)+1):
    default_rule = False 
    used = False
    tmp_ids = [] 
    tmp = [] 
    things = all_dep_sent[ind]
    # New: POS tags 
    token = tokens[ind-1]
    taglist = POS_Tags(token)
    novps,vps,embedvps,tl,tr,numlist = get_vptree(parse[ind-1])
    lists_nodes[ind] = tl  
    all_vpnodes = make_vpsnumber(vps)
    raw_sentence = "===================Raw sentence: "+ " ".join([i[0] for i in numlist]) + " \n"
    #write_log('../ext/' + fname +'_log1-segment-sentence-readable.txt',raw_sentence)
    raw_sentence = "===================Raw sentence: "+ " ".join([str(i[1]) for i in numlist]) + " \n"
    #write_log('../ext/' + fname +'_log1-segment-id-readable.txt',raw_sentence)
    segmentation_count = 0
    #segment_count = 0
    # Check the very first case, if there is a subordinating conjunction, if so, write it into log directly 
    # New rule: subordinating conjunction + sbars, as long as there is a subclauses 
    valid_sbar = Valid_SubClauses(tr, taglist)
    if len(valid_sbar) >0:
        #print "subconj!!"
        used = True
        subconj_seg_sent,subconj_seg_ids = Rule_SBAR(valid_sbar,numlist)
        for segmt in range(0,len(subconj_seg_sent)): 
            #for kk in range(0,len(subconj_seg_sent[segmt])):
            output_sentence = Format_Sentence(1,subconj_seg_ids[segmt],summary_index,ind,segmentation_count,segmt)
            #write_log('../ext/' + fname +'_log-segment-id-readable.txt',output_sentence)
                # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
            out_sent = Format_Sentence(3,subconj_seg_sent[segmt],summary_index,ind,segmentation_count,segmt)
            output_sentence1 = Format_Sentence(2,subconj_seg_sent[segmt],summary_index,ind,segmentation_count,segmt) 
            #write_log('../ext/'+ fname +'_log-segment-label-readable.txt',output_sentence1)
            write_log(seg_dir+'/'+ fname +'.segs',out_sent)
        segmentation_count += 1  

    #Rule 2: [NP/VP, SBAR]
    # Parallel NP/VP SBAR
    sbar_flag,sbar = get_SBAR(tr)
    if sbar_flag == True:
        used = True 
        #print "embedded vps! "
        sbar_ids, sbar_sent = Rule_NPSBAR(tr,tl,sbar,numlist)
        for segmt in range(0,len(sbar_sent)): 
            for kk in range(0,len(sbar_sent[segmt])):
                output_sentence = Format_Sentence(1,sbar_ids[segmt][kk],summary_index,ind,segmentation_count+segmt,kk)
                #write_log('../ext'+'/' + fname +'_log-segment-id-readable.txt',output_sentence) 
                out_sent = Format_Sentence(3,sbar_sent[segmt][kk],summary_index,ind,segmentation_count+segmt,kk)
                output_sentence1 = Format_Sentence(2,sbar_sent[segmt][kk],summary_index,ind,segmentation_count+segmt,kk) 
                #write_log('../ext'+'/'+ fname +'_log-segment-label-readable.txt',output_sentence1)
                write_log(seg_dir+'/' + fname +'.segs',out_sent)
        segmentation_count += len(sbar)

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
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
                        for each in ids:
                            tmp_ids.append(each)
                    elif e['gov_id'] not in idlist:
                        nodes_id = e['gov_id']
                        nodes_label = e['gov']
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
                        #print "ids gov", ids
                        for each in ids:
                            tmp_ids.append(each)
            # For complement, conjunction 
            if len(woa) >0:
                # Mark the current verb as starting node, vp always starts from a verb 
                nodes_id = i.leaves()[0][1]
                nodes_label = i.leaves()[0][0]
                ids,all_comp = pull_comp_parts(woa,things,i.leaves(),idlist,ind,flag,nodes_id,nodes_label,fname)
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
    if len(embedvps) != 0:
        _embedfinal = Rule_EmbeddedVP(embedvps,tr,tl,numlist,things,ind,fname)
        idseg[ind] += _embedfinal 
    else:
        pass 

    # Now, start to pull out the segments from sentences 
    if all_vpnodes:
        used = True
        _idseg = RemakeSegStructure(idseg[ind])
        seg_combo = with_segmentation(_idseg)
        left = get_left(seg_combo,tl)
        segs = Rearrange2(tl,seg_combo,left)
        final = Connect_subj(seg_combo,segs)
        final = Clean_Duplicate(final)
        segment_set[ind] = final
        if len(segment_set[ind]) != 0:
            for k,v in enumerate(segment_set[ind]):
                for vv in range(0,len(v)):
                    sentence = Format_Sentence(1, v[vv], summary_index,ind,segmentation_count+k,vv)
                    #write_log('../ext'+'/' + fname +'_log-segment-id-readable.txt',sentence)
                    #write_log(ext+'/' + fname +'_log-segment-id.txt',out_sent)
            seg = Pull_Words(segment_set,ind,numlist)
            for k,v in seg.items():
                for vv in range(0,len(v)):
                    # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
                    sentence = Format_Sentence(2, v[vv], summary_index,ind,segmentation_count+k,vv)
                    #write_log('../ext'+'/' + fname +'_log-segment-label-readable.txt',sentence) 
                    sent = Format_Sentence(3,v[vv],summary_index,ind,segmentation_count+k,vv)
                    #print "segment ", vv, " label: ", v[vv]
                    write_log(seg_dir+'/' + fname +'.segs',sent)
            segmentation_count += len(seg)
    else:
        # If already considers the subbordinating conjunction case, then no needs to take the raw sentence as segmentation 
        #if subconj_flag == True:
        #    pass
        pass 
    #if used == False:
    if segmentation_count == 0:
        #Just output whatever it is 
        print "defalut rule! "
        defalut_rule = True 
        if defalut_rule:
            v = " ".join([item[0] for item in numlist]) 
            sentence = Format_Sentence(3,v,summary_index,ind,segmentation_count,0)
            #if sentence.split('&')[4].strip() != '.':
            write_log(seg_dir +'/'+ fname +'.segs',sentence)
    else:
        pass

# Remove empty lines to prevent WTMF errors 
ffname = seg_dir +'/'+ fname +'.segs'

all_text = open(ffname).readlines()
all_text[len(all_text)-1] = all_text[len(all_text)-1].replace("\n","")

with open(ffname,'wb') as f:
    for i in all_text:
        f.write(i)
f.close()

print "Sentence decomposition parser done with cleaning files!"
















