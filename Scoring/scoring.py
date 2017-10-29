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
import optparse
import glob
import copy
import csv
import os


"""
============================ Input==============================
"""

parser = optparse.OptionParser()
parser.add_option('-a', '--all', action="store_true", dest="a", default=False)
parser.add_option('-t', '--table', action="store_true", dest="t", default=False)
parser.add_option('-p', '--pyramid', action="store", dest="pyramid", default="pyrs/pyramids/*")
parser.add_option('-o', '--output', action="store", dest='output', default='../results.csv')
parser.add_option('-l', '--log', action='store', dest='log', default=None)
options, args = parser.parse_args()

print_all = options.a
print_table = options.t
pyramid_path = options.pyramid
results_file = options.output
log = options.log

pyramids = list(glob.iglob(pyramid_path + '/*'))

summaries = list(glob.iglob('../Preprocess/peer_summaries/*'))
# See pyrmaid from "Scoring/pyrs/pyramids/" folder
#pyramid = sys.argv[1]
#for testing
# pyramids = list(glob.iglob('pyrs/pyramids/*'))
#pyramids = list(glob.iglob('pyrs/pyramids/*'))
for pyr in pyramids:
    print pyr
f = open(results_file, 'w')
f.close()


"""
================ Scoring Mechanisms ======================
"""
score_tables = ['raw', 'quality', 'coverage', 'comprehension']

"""
==== What is Matter Test Data Set ====
"""
#sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(j[0][:(j[0].rfind('.'))])))]
#RAW = [49,39,33,24,24,49,22,37,23,20,24,21,52,28,39,26,23,39,32,43]

"""
=== DUC Test Data Sets ====
"""
def getName(name):
    num = name.rfind('.')
    name = name[num+1:]
    return name
sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(getName(j[0]))))]

### D0608
#RAW = [8,7,8,6,4,10,20,6,6,4,3,3,2,9,1,3,8,1,3,6,5,6]

### D0624
#RAW = [14,20,22,20,20,18,26,18,19,11,19,16,21,26,20,19,22,19,15,13,19,5]

### D0605
#RAW = [0,15,6, 9, 8,17, 9, 2, 14, 4, 2, 4, 1, 6, 6, 0, 14, 3, 6, 6, 3, 4, ]

### D0615
#RAW = [4,9,8,4,8,7,11,10,6,7,1,3,2,8,8,7,9,6,5,10,6,1]

### D0601
RAW = [9,14,20,11,0,12,23,4,12,6,7,11,20,19,18,2,16,9,11,6,17,8]



"""
====================== Scoring Pipeline ========================
"""

correlation_file = '../D0601_correlation.csv'
corr = open(correlation_file, 'w')
corr_w = csv.writer(corr)
corr_w.writerow(['Pyramid'] + score_tables)
corr.close()


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
            if print_all:
                formatVerboseOutput(summary_name,segment_count,score,quality,coverage,comprehension, results, segment_list,num_sentences,segs,scu_labels,pyramid_name, log)


    #scores = [raw_scores, quality_scores, coverage_scores, comprehension_scores]
    if print_table:
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
                            #print "Raw score for summary ", summary_name, ": ", raw_scores[summary_name]
                            output = [summary_name, raw_scores[summary_name],quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name]]
                            w.writerow(output)
                            print '{:>16} | {:>2} | {:.3f} | {:.3f} | {:.3f}'.format(summary_name, raw_scores[summary_name], quality_scores[summary_name],coverage_scores[summary_name],comprehension_scores[summary_name])
            """
            raw_sc = sort(raw_scores)
            raw_corr = pearson(raw_sc, RAW)[0]
            print('{:>16} | {:>.2f}'.format('Correlation', raw_corr*100))
            print '\n'

    with open(correlation_file, 'a') as f:
        w = csv.writer(f)
        raw_sc = sort(raw_scores)
        raw_corr = pearson(raw_sc, RAW)[0]
        w.writerow([pyramid_name] + [raw_corr])



print '\n'
print 'Results written to %s' % results_file
print '\n'

"""


