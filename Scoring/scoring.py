from lib_scoring import sentencesFromSegmentations, SummaryGraph, buildSCUcandidateList, filename
from lib_scoring import getScore, getLayerSizes, processResults, scusBySentences, maxRawScore, readPyramid
import glob
import copy
import sys
import csv
import os


"""
============================ Input==============================
"""

summaries = list(glob.iglob('../Preprocess/peer_summaries/*'))
# See pyrmaid from "Scoring/pyrs/pyramids/" folder
#pyramid = sys.argv[1]
#for testing

# Input either a pickle file or a human pyramid
pyramid = sys.argv[1]
# 1: pickle, 2: human pyramid

results_file = '../results.csv'
f = open(results_file, 'w')
f.close()

"""
====================== Scoring Pipeline ========================
"""

raw_scores = {}
quality_scores = {}
coverage_scores = {}
comprehension_scores = {}

#print "test"
scus_og = readPyramid(pyramid)
for summary in summaries:
    scus = copy.deepcopy(scus_og)
    if os.path.isdir(summary):
        summ = glob.iglob(summary+'/*')
        for fn in summ:
            #print fn 
            #if str(fn[:-5]) == '.segs':
            if fn.endswith('.ls'):
                print "\tcurrent file, ", fn
                summary_slash= fn.rfind('/') + 1
                summary_dot = fn.rfind('.')
                summary_name = fn[summary_slash:summary_dot]
                sentences = sentencesFromSegmentations(fn)
                Graph = SummaryGraph(sentences, scus)
                independentSet = Graph.independentSet
                candidates = buildSCUcandidateList(independentSet)
                results, possiblyUsed = processResults(candidates, independentSet)
                #for segid, res in results.items():
                    #print '\t{}: {}'.format(segid, res)
                rearranged_results = scusBySentences(results)
                score, matched_cus = getScore(rearranged_results, scus)
                size_file = 'sizes/' + filename(pyramid) + '.size'
                count_by_weight, avg = getLayerSizes(size_file)
                raw_scores[summary_name] = score
                quality = float(score)/maxRawScore(count_by_weight, possiblyUsed)
                coverage = float(score)/maxRawScore(count_by_weight, avg)
                comprehension = float((quality + coverage)) / 2
                quality_scores[summary_name] = quality
                coverage_scores[summary_name] = coverage
                comprehension_scores[summary_name] = comprehension
            else:
                pass

score_tables = ['raw', 'quality', 'coverage', 'comprehension']
#scores = [raw_scores, quality_scores, coverage_scores, comprehension_scores]

with open(results_file, 'a') as f:
    w = csv.writer(f)
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
                    #print "Raw score for summary ", summary_name, ": ", raw_scores[summary_name]
                    output = [summary_name, raw_scores[summary_name],quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name]]
                    w.writerow(output)
                    print '{:>16} | {:>2} | {:.3f} | {:.3f} | {:.3f}'.format(summary_name, raw_scores[summary_name], quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name])
