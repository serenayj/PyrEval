# Author: Yanjun Gao(yug125)
# Last update: July 3,2017 

# SETENCE DECOMPOSITION PARSER 
# <Script for main modules of Sentence Decomposition Parser> 
# Copyright (C) 2017  Yanjun Gao

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# For any question, please contact yanjungao@cse.psu.edu 

import os
import glob
from lib_parser import *
#from helpers import *
from rearrange import *
from sbarnew import *


fname = sys.argv[1]
sum_index = sys.argv[2]
outpath = sys.argv[3]



# Correct way to build summary_index 
summary_index = str(sum_index)
#summary_index =  str(1)
seg_dir = outpath +'/'+str(sum_index)
#ext = os.getcwd() + '/'


#fname = "/Users/kylebradley/Desktop/Kyle/Batch2/" + ext
#for fname in fnames:
content = open(fname).read()
#print content
#dot = fname.rfind('.')
#fname = fname[:dot]
dot = fname.rfind('.')
fname = fname[:dot]
slash = fname.rfind('/')
fname = fname[(slash + 1):dot]
#print fname

if not os.path.exists(seg_dir):
    os.makedirs(seg_dir)

print "current filename: ", fname 
soup = BeautifulSoup(content,'lxml')

basic = []
for links in soup.find_all("dependencies"):
        if links.get("type") == "enhanced-dependencies":
                basic.append(links)

parse = []
for links in soup.find_all("parse"):
        parse.append(links)

tokens = soup.find_all("tokens")

#print parse, basic
"""
=========================================Main Procedure====================================
""" 




sentence_segmentations = []
all_dep_sent = get_depparse(basic)

#write_log(ext+'/' + fname +'_log-segment-label-readable.txt', '', 1)
write_log(seg_dir+'/' + fname +'.segs', '', 1)
#write_log(ext+'/' + fname +'_log-segment-id-readable.txt', '', 1)
#write_log(ext+'/' + fname +'_log-segment-id.txt', '', 1)

segments = {}
idseg = {}
count = 0 
lists_nodes = {}
segment_set = {}
# Sentence as basic unit
# No index 0, all starts from 1
for ind in range(1,len(all_dep_sent)+1):
#for ind in range(4,5):
    #print "============ Currnet Sentence, ", ind, "============"
    used = False
    tmp_ids = [] 
    tmp = [] 
    things = all_dep_sent[ind]
    # New: POS tags 
    token = tokens[ind-1]
    taglist = POS_Tags(token)
    novps,vps,embedvps,tl,tr,numlist = get_vptree(parse[ind-1])
    #tr.pretty_print() 
    lists_nodes[ind] = tl  
    all_vpnodes = make_vpsnumber(vps)
    raw_sentence = "===================Raw sentence: "+ " ".join([i[0] for i in numlist]) + " \n"
    #write_log(ext+'/' + fname +'_log-segment-label-readable.txt',raw_sentence)
    raw_sentence = "===================Raw sentence: "+ " ".join([str(i[1]) for i in numlist]) + " \n"
    #write_log(ext+'/' + fname +'_log-segment-id-readable.txt',raw_sentence)
    segmentation_count = 0
    segment_count = 0 
    # Check the very first case, if there is a subordinating conjunction, if so, write it into log directly 
    # New rule: subordinating conjunction + sbars, as long as there is a subclauses 
    #print tr
    valid_sbar = Valid_SubClauses(tr, taglist)
    #print valid_sbar
    if len(valid_sbar) >0:
        #print "subconj!!"
        used = True
        subconj_seg_sent,subconj_seg_ids = Rule_SBAR(valid_sbar,numlist,taglist, tr)
        for segmt in range(0,len(subconj_seg_sent)):
            if segmt == []:
                continue
            #for kk in range(0,len(subconj_seg_sent[segmt])):
            output_sentence = Format_Sentence(1,subconj_seg_ids[segmt],summary_index,ind,segmentation_count,segmt)
            #write_log(ext+'/' + fname +'_log-segment-id-readable.txt',output_sentence)
                # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
            out_sent = Format_Sentence(3,subconj_seg_sent[segmt],summary_index,ind,segmentation_count,segmt)
            output_sentence1 = Format_Sentence(2,subconj_seg_sent[segmt],summary_index,ind,segmentation_count,segmt) 
            write_log(seg_dir+'/' + fname +'.segs',out_sent)
        segmentation_count += 1  

    # Check the parallel [NP,SBAR]
    sbar_flag,sbar = get_SBAR(tr)
    if sbar_flag == True:
        #print "sbar!!"
        sbar_ids, sbar_sent = Rule_NPSBAR(tr,tl,sbar,numlist)
        for segmt in range(0,len(sbar_sent)): 
            for kk in range(0,len(sbar_sent[segmt])):
                output_sentence = Format_Sentence(1,sbar_ids[segmt][kk],summary_index,ind,segmentation_count+segmt,kk)
                #write_log(ext+'/' + fname +'_log-segment-id-readable.txt',output_sentence) 
                out_sent = Format_Sentence(3,sbar_sent[segmt][kk],summary_index,ind,segmentation_count+segmt,kk)
                output_sentence1 = Format_Sentence(2,sbar_sent[segmt][kk],summary_index,ind,segmentation_count+segmt,kk) 
                #write_log(ext+'/'+ fname +'_log-segment-label-readable.txt',output_sentence1)
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
                        nodes_label = e['dep']
                        #ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
                        ids,parts = pull_subj_parts(e,i.leaves(),nodes_id,nodes_label,idlist,ind,flag,fname)
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
                #ids,all_comp = pull_comp_parts(woa,things,i.leaves(),idlist,ind,flag,nodes_id,nodes_label,fname)
                ids,all_comp = pull_comp_parts(woa,things,i.leaves(),idlist,ind,flag,nodes_id,nodes_label,fname)
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
    if len(embedvps) != 0:
        _embedfinal = Rule_EmbeddedVP(embedvps,tr,tl,numlist,things,ind,fname)
        if len(_embedfinal) != 0:
            idseg[ind] += _embedfinal 
        else:
            pass
    else:
        pass 

    # Now, start to pull out the segments from sentences 
    if all_vpnodes:
        used = True 
        # In case segmentation being rewrited 
        _idseg = RemakeSegStructure(idseg[ind])
        seg_combo = with_segmentation(_idseg)
        left = get_left(seg_combo,tl)
        segs = Rearrange2(tl,seg_combo,left)
        final = Connect_subj(seg_combo,segs)
        final = Clean_Duplicate(final)
        segment_set[ind] = final
        # segment_set is with ids 
        if len(segment_set[ind]) != 0:
            for k,v in enumerate(segment_set[ind]):
                #print "Segmentation: ", k 
                for vv in range(0,len(v)):
                    sentence = Format_Sentence(1, v[vv], summary_index,ind,segmentation_count+k,vv)
                    #print "segment ", vv, " label: ", v[vv]
            # Match with actual words 
            # seg is with actual words 
            seg = Pull_Words(segment_set,ind,numlist)
            #segmentation_count = tmp_count 
            for k,v in seg.items():
                #print "Segmentation: ", k   
                for vv in range(0,len(v)):
                    # Format: summary_index&sentence_index&segmentation_index$segment_index$segment 
                    sentence = Format_Sentence(2, v[vv], summary_index,ind,segmentation_count+k,vv)
                    sent = Format_Sentence(3,v[vv],summary_index,ind,segmentation_count+k,vv)
                    #print "segment ", vv, " label: ", v[vv] 
                    write_log(seg_dir+'/' + fname +'.segs',sent)
                    #sentence_segmentations.append(out_sent)
        segmentation_count += len(segment_set[ind])
    else:
        pass
        # If already considers the subbordinating conjunction case, then no needs to take the raw sentence as segmentation 
        #if subconj_flag == True:
        #    pass
        # Else, the case we just take whatever it is 
    # The case where there is no vp extracted and matched, so just output the whole sentence 
    #if used == False:
    if segmentation_count == 0:
        v = " ".join([item[0] for item in numlist]) 
        sentence = Format_Sentence(3,v,summary_index,ind,segmentation_count,0)
        write_log(seg_dir +'/'+ fname +'.segs',sentence)
        #print "Special case2: segmentation ", segmentation_count, " label: ", v 
    else:
        pass

        













