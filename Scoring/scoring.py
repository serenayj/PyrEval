#   Script for scoring summaries by the pyramid

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


from lib_scoring import sentencesFromSegmentations, SummaryGraph, buildSCUcandidateList, filename, getsegsCount
from lib_scoring import getScore, getLayerSizes, processResults, scusBySentences, maxRawScore, readPyramid, new_getlayersize
from scipy.stats import pearsonr as pearson
from scipy.stats import spearmanr as spearman
from printEsumLog import printEsumLogWrapper 
import optparse
import glob
import copy
import csv
import os
import collections
import sys
import pandas as pd


"""
============================ Input==============================
"""
#dir1 = sys.argv[1]

#dataset_ind = sys.argv[1]

parser = optparse.OptionParser()
parser.add_option('-a', '--all', action="store_true", dest="a", default=False)
parser.add_option('-t', '--table', action="store_true", dest="t", default=False)
parser.add_option('-p', '--pyramid', action="store", dest="pyramid", default="pyrs/pyramids")
parser.add_option('-o', '--output', action="store", dest='output', default='../results.csv')
parser.add_option('-l', '--log', action='store', dest='log', default=False)
parser.add_option('-m', '--model', action='store', dest='model', default=1)
#parser.add_option('-n', '--numsmodel', action='store', dest='numsmodel', default=4)
options, args = parser.parse_args()

print_all = options.a
print_table = options.t
pyramid_path = options.pyramid
results_file = options.output
log = options.log
model = options.model


#pyramids = list(glob.iglob(pyramid_path + '*.pyr'))
pyramids = list(glob.iglob(pyramid_path + '/*.pyr'))
#pyramids = list(glob.iglob(dir1+"/*.pyr"))
summaries = list(glob.iglob('../Preprocess/peer_summaries/*'))
numsmodel = len(list(glob.iglob('../Preprocess/wise_crowd_summaries/*.xml')))
#numsmodel = 5
print "Numbers of contributors: ", numsmodel
# See pyrmaid from "Scoring/pyrs/pyramids/" folder
#pyramid = sys.argv[1]
#for testing
# pyramids = list(glob.iglob('pyrs/pyramids/*'))
#pyramids = list(glob.iglob('pyrs/pyramids/*'))
for pyr in pyramids:
    print pyr



"""
================ Scoring Mechanisms ======================
"""
score_tables = ['raw', 'quality', 'coverage', 'Comprehensive']

"""
==== What is Matter Test Data Set ====
"""

"""
Raw scores from scores.csv, a column 
"""

"""
=== DUC Test Data Sets ====
"""


def getName(name):
    num = name.rfind('.')
    name = name[num+1:]
    return name



"""
====================== Scoring Pipeline ========================
"""



for pyramid in pyramids:
    raw_scores = {}
    quality_scores = {}
    coverage_scores = {}
    comprehension_scores = {}
    pyramid_name = pyramid[pyramid.rfind('/') + 1:pyramid.rfind('.')]
    #print "test"
    scus_og, scu_labels = readPyramid(pyramid)
    
    for summary in summaries:
        scus = copy.deepcopy(scus_og)
        if os.path.isdir(summary):
            summ = glob.iglob(summary+'/*')
            #fn is the summary name 
            for fn in summ:
                #print "current filename: ", fn
                if fn.endswith('.ls'):
                    summary_slash= fn.rfind('/') + 1
                    summary_dot = fn.rfind('.')
                    summary_name = fn[summary_slash:summary_dot]
                    if os.path.getsize(fn) == 0:
                        raw_scores[summary_name] = 0
                        quality_scores[summary_name] = 0
                        coverage_scores[summary_name] = 0
                        comprehension_scores[summary_name] = 0
                        continue
                    segs = fn[:fn.rfind('/')] + '/' + summary_name + '.segs'
                    segs = open(segs, 'r').readlines()
                    num_sentences = int(segs[len(segs)-1].split('&')[1])
                    segs = {'&'.join(seg.split('&')[:4]): seg.split('&')[4] for seg in segs}
                    sentences, segment_count, segment_list = sentencesFromSegmentations(fn)
                    Graph = SummaryGraph(sentences, scus)
                    independentSet = Graph.independentSet
                    candidates = buildSCUcandidateList(independentSet)
                    #print "Candidates: ", 
                    results, possiblyUsed = processResults(candidates, independentSet)
                    segcount = getsegsCount(segment_list, results, segs, num_sentences)
                    #print "Possibly used: ", possiblyUsed
                    keys = [res.split('&') for res in results]
                    rearranged_results = scusBySentences(results)
                    score, matched_cus = getScore(rearranged_results, scus)
                    size_file = 'sizes/' + filename(pyramid) + '.size'
                    #count_by_weight, avg = getLayerSizes(size_file)
                    # New get layersize 
                    count_by_weight, avg = new_getlayersize(size_file,numsmodel)
                    #print "AVG SCU: ", avg 
                    raw_scores[summary_name] = score
                    # temporary fix to number of sentences 
                    #q_max = maxRawScore(count_by_weight, possiblyUsed)
                    q_max = maxRawScore(count_by_weight, segcount)
                    #print "MAXSUM for numbers of matched SCU", q_max 
                    c_max = maxRawScore(count_by_weight, avg)

                    #print "MAXSUM for avg scu: ", c_max 
                    #print "score divided by max obtainable scores: ", q_max
                    quality = 0 if not q_max else float(score)/q_max
                    if quality > 1:
                        quality = 1 
                    coverage = 0 if not c_max else float(score)/c_max
                    if coverage > 1:
                        coverage = 1 
                    comprehension = float((quality + coverage)) / 2
                    quality_scores[summary_name] = quality
                    coverage_scores[summary_name] = coverage
                    comprehension_scores[summary_name] = comprehension

                else:
                    pass
            if (print_all) or log:
                #log_f = log + summary_name
                log_f = "../log/"+summary_name
                
                loginput = open("loginput.txt", "w+")
                loginput.write(summary_name+'\n'+str(segcount)+'\n'+str(score)+'\n'+str(quality)+'\n'+str(coverage)+'\n'+str(comprehension)+'\n'+str(results)+'\n'+" ".join(str(segment_list))+'\n'+str(num_sentences)+'\n'+str(segs)+'\n'+str(scu_labels)+'\n'+pyramid_name+'\n'+log_f)
                loginput.close()
                print("Success!!")
                printEsumLogWrapper(summary_name,segcount,score,quality,coverage,comprehension,q_max, c_max, avg, results, segment_list,num_sentences,segs,scu_labels,pyramid_name, log_f)

    #raw_scores = sort(raw_scores)
    #print type(raw_scores)
    #print "raw_scores: ", raw_scores
    scores = [raw_scores, quality_scores, coverage_scores, comprehension_scores]
    print "scores ", scores
    if print_table:
        #results_f = 
        ### For DUC05
        items = pyramid_name.split("_")
        #results_file = "../311-6-1-results/"+str(items[1][1:])+"_"+str(items[2][1:])+"_"+str(items[3][1:])+"-raw.csv"
        ## FOr Duc 05
        #results_file = "results-raw.csv"
        print "Will write into results file!! ", results_file
        # f = open(results_file, 'w')
        # f.close()
        with open(results_file, 'a') as f:
            w = csv.writer(f)
            w.writerow([pyramid_name])
            print pyramid_name
            w.writerow(['Summary'] + score_tables)
            print '{} | {} | {} | {} | {}'.format("summary name", "Raw score", "Quality score", "Coverage score", "Comprehensive score")
            for n, summary in enumerate(summaries):
                #w.writerow([filename(summary)] + [s[n] for s in scores])
                if os.path.isdir(summary):
                    summ = glob.iglob(summary+'/*')
                    for fn in summ:
                        #if fn[:-5] == '.segs':
                         if fn.endswith('.ls'):
                            summary_slash= fn.rfind('/') + 1
                            summary_dot = fn.rfind('.')
                            summary_name = fn[summary_slash:summary_dot]
                            print "Raw score for summary ", summary_name, ": ", raw_scores[summary_name]
                            output = [summary_name, raw_scores[summary_name],quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name]]
                            w.writerow(output)
                            print '{:>16} | {:>2} | {:.3f} | {:.3f} | {:.3f}'.format(summary_name, raw_scores[summary_name], quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name])




print '\n'
print 'Results written to %s' % results_file
print '\n'




