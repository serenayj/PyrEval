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


from lib_scoring import sentencesFromSegmentations, SummaryGraph, buildSCUcandidateList, filename, formatVerboseOutput
from lib_scoring import getScore, getLayerSizes, processResults, scusBySentences, maxRawScore, readPyramid
from scipy.stats import pearsonr as pearson
from scipy.stats import spearmanr as spearman 
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
# See pyrmaid from "Scoring/pyrs/pyramids/" folder
#pyramid = sys.argv[1]
#for testing
# pyramids = list(glob.iglob('pyrs/pyramids/*'))
#pyramids = list(glob.iglob('pyrs/pyramids/*'))
for pyr in pyramids:
    print pyr



#dataset_ind = 'D0614'
"""
================ Scoring Mechanisms ======================
"""
score_tables = ['raw', 'quality', 'coverage', 'comprehension']

"""
==== What is Matter Test Data Set ====
"""
#sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(j[0][:(j[0].rfind('.'))])))]
"""
Raw scores from scores.csv, a column 
"""

"""
=== DUC Test Data Sets ====
"""

# data = pd.read_csv("/Users/Serena/Desktop/Dataset/LREC-datasets/DUC06/scores.csv",index_col = 0)
# RAW = [data[dataset_ind][i] for i in range(0,22)]

def getName(name):
    num = name.rfind('.')
    name = name[num+1:]
    return name

#sort = lambda score_dict: [x[1].index(type(x),x) for x in list(sorted(score_dict.items(), key=lambda j: int(getName(j[0]))))]
#sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(getName(j[0])) if str(getName(j[0])).isdigit()) + sorted(score_dict.items(), key=lambda j: str(getName(j[0])) if not str(getName(j[0])).isdigit()))]

#sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(getName(j[0]))))]


"""
====================== Scoring Pipeline ========================
"""

"""
for TAC
"""
#data = pd.read_csv("/Users/Serena/Desktop/Dataset/LREC-datasets/TAC10/scores.csv",index_col = 0)
#RAW = [data[dataset_ind][i] for i in range(1,43)]

#RAW = [4,13,19,14,30,18,14,12,14,7,7,17,12,26,11,8,15,21,14,14,20,8]
## For D05
#correlation_file =  "1004testcorrelation.csv"
#correlation_file = '../311correlation-6-1-sp.csv'
# correlation_file = "../614-corr.csv"
# corr = open(correlation_file, 'w')
# corr_w = csv.writer(corr)
# corr_w.writerow(['Pyramid'] + score_tables)
# corr.close()


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
                if fn.endswith('.ls'):
                    summary_slash= fn.rfind('/') + 1
                    summary_dot = fn.rfind('.')
                    summary_name = fn[summary_slash:summary_dot]
                    segs = fn[:fn.rfind('/')] + '/' + summary_name + '.segs'
                    segs = open(segs, 'r').readlines()
                    num_sentences = int(segs[len(segs)-1].split('&')[1])
                    segs = {'&'.join(seg.split('&')[:4]): seg.split('&')[4] for seg in segs}
                    sentences, segment_count, segment_list = sentencesFromSegmentations(fn)
                    Graph = SummaryGraph(sentences, scus)
                    independentSet = Graph.independentSet
                    candidates = buildSCUcandidateList(independentSet)
                    results, possiblyUsed = processResults(candidates, independentSet)
                    keys = [res.split('&') for res in results]
                    rearranged_results = scusBySentences(results)
                    score, matched_cus = getScore(rearranged_results, scus)
                    size_file = 'sizes/' + filename(pyramid) + '.size'
                    count_by_weight, avg = getLayerSizes(size_file)
                    raw_scores[summary_name] = score
                    q_max = maxRawScore(count_by_weight, possiblyUsed)
                    c_max = maxRawScore(count_by_weight, avg)
                    quality = 0 if not q_max else float(score)/q_max
                    coverage = 0 if not c_max else float(score)/c_max
                    comprehension = float((quality + coverage)) / 2
                    quality_scores[summary_name] = quality
                    coverage_scores[summary_name] = coverage
                    comprehension_scores[summary_name] = comprehension

                else:
                    pass
            if (print_all) or log:
                #log_f = log + summary_name
                log_f = "../log/"+summary_name
                formatVerboseOutput(summary_name,segment_count,score,quality,coverage,comprehension, results, segment_list,num_sentences,segs,scu_labels,pyramid_name, log_f)

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
            print '{} | {} | {} | {} | {}'.format("summary name", "Raw score", "Quality score", "Coverage score", "Comprehension score")
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
            
            #print "sorted raw scores, ", raw_scores
            #raw_sc = sort(raw_scores)
            # raw_corr = pearson(raw_sc, RAW)[0]
            #raw_corr = spearman(new_raw_sc, RAW)[0]
            # print "Sorted Pan file scores, ", RAW
            # print('{:>16} | {:>.2f}'.format('Correlation', raw_corr*100))
            # print '\n'

            """
            Changes for DUC05
            """
            # raw_sc = collections.OrderedDict(sorted(raw_scores.items()))
            # print "sorted raw scroes", raw_scores
            # new_raw_sc = []
            # for k,v in enumerate(raw_sc):
            #     print k,v, raw_sc[v]
            #     new_raw_sc.append(raw_sc[v])

            # print "sorted raw scores, ", new_raw_sc
            # raw_corr = pearson(new_raw_sc, RAW)[0]
            # #raw_corr = spearman(new_raw_sc, RAW)[0]
            # print "Sorted Pan file scores, ", RAW
            # print('{:>16} | {:>.2f}'.format('Correlation', raw_corr*100))
            # print '\n'

    # with open(correlation_file, 'a') as f:
    #     w = csv.writer(f)
    #     raw_sc = collections.OrderedDict(sorted(raw_scores.items()))
    #     print raw_sc
    #     new_raw_sc = []
    #     for k,v in enumerate(raw_sc):
    #         print k,v, raw_sc[v]
    #         new_raw_sc.append(raw_sc[v])
    #     #raw_corr = spearman(new_raw_sc, RAW)[0]
    #     raw_corr = pearson(new_raw_sc, RAW)[0]
    #     w.writerow([pyramid_name] + [raw_corr])



print '\n'
print 'Results written to %s' % results_file
print '\n'




