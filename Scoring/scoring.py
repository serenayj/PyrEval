from lib_scoring import sentencesFromSegmentations, buildSCUlist, SummaryGraph, buildSCUcandidateList
from lib_scoring import getScore, getLayerSizes, filename, processResults, scusBySentences, maxRawScore
import glob
import sys
import csv

"""
============================ Input==============================
"""

summaries = list(glob.iglob('test_summaries/*'))
pyramid = sys.argv[1]
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

for summary in summaries:
    summary_slash= summary.rfind('/') + 1
    summary_dot = summary.rfind('.')
    summary_name = int(summary[summary_slash:summary_dot])
    #print '\t\t{}'.format(summary_name)
    sentences = sentencesFromSegmentations(summary)
    scus = buildSCUlist(pyramid)
    Graph = SummaryGraph(sentences, scus)
    independentSet = Graph.independentSet
    candidates = buildSCUcandidateList(independentSet)
    results = processResults(candidates, independentSet)
    rearranged_results = scusBySentences(results)
    score, matched_cus = getScore(rearranged_results, scus)
    size_file = pyramid.replace('.p', '.size').replace('pyramids/', 'sizes/')
    count_by_weight, avg = getLayerSizes(size_file)
    raw_scores[summary_name] = score
    quality = float(score)/maxRawScore(count_by_weight, matched_cus)
    coverage = float(score)/maxRawScore(count_by_weight, avg)
    comprehension = float((quality + coverage)) / 2
    quality_scores[summary_name] = quality
    coverage_scores[summary_name] = coverage
    comprehension_scores[summary_name] = comprehension

raw_scores = sorted(raw_scores.items(), key=lambda x: x[0])
raw_scores = [s[1] for s in raw_scores]
quality_scores = sorted(quality_scores.items(), key=lambda x: x[0])
quality_scores = [s[1] for s in quality_scores]
coverage_scores = sorted(coverage_scores.items(), key=lambda x: x[0])
coverage_scores = [s[1] for s in coverage_scores]
comprehension_scores = sorted(comprehension_scores.items(), key=lambda x: x[0])
comprehension_scores = [s[1] for s in comprehension_scores]

score_tables = ['raw', 'quality', 'coverage', 'comprehension']
scores = [raw_scores, quality_scores, coverage_scores, comprehension_scores]

with open(results_file, 'a') as f:
    w = csv.writer(f)
    w.writerow(['Summary'] + score_tables)
    for n, summary in enumerate(summaries):
    	w.writerow([filename(summary)] + [s[n] for s in scores])
    	print '{} | {:>2} | {:.3f} | {:.3f} | {:.3f}'.format(filename(summary), scores[0][n], scores[1][n], scores[2][n], scores[3][n])
        
