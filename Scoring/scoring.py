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
options, args = parser.parse_args()

print_all = options.a
print_table = options.t
pyramid_path = options.pyramid
results_file = options.output

pyramids = list(glob.glob(pyramid_path))

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

#getFname = lambda fname: fname[:fname.rfind('.')]
#sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(getFname(j[0]))))]
sort = lambda score_dict: [x[1] for x in list(sorted(score_dict.items(), key=lambda j: int(j[0][:(j[0].rfind('.'))])))]


"""
====================== Scores to Compare With ========================
"""
score_tables = ['raw', 'quality', 'coverage', 'comprehension']
#RAW = [16,43,22,40,34,54,25,46,47,51,26,36,22,10,38,38,19,13,13,60]              
# QUALITY = [0.7705,0.6552,0.5938,0.4231,
#                     0.7188,0.8361,0.7907,0.8571,
#                     0.3333,0.2857,0.5641,0.7037,
#                     0.7714,0.6667,0.8269,0.8,
#                     0.5161,0.6923,0.641,0.8163]

# COVERAGE = [0.5222,0.4222,0.4222,0.2444,
#                         0.5111,0.5667,0.3778,
#                         0.6667,0.1444,
#                         0.1111,
#                         0.2442,
#                         0.2111,0.6,
#                         0.2889,0.4778,0.4889,s

#                         0.1778,0.4,0.2778,0.4444]

# COMP = [0.6463,0.5387,0.508,0.3337,
#                                 0.6149,0.7014,0.5842,
#                                 0.7619,0.2389,
#                                 0.1984,
#                                 0.4042,
#                                 0.4574,0.6857,
#                                 0.4778,0.6523,0.6444,
#                                 0.3469,0.5462,0.4594,0.6303]
RAW = [49,39,33,24,24,49,22,37,23,20,24,21,52,28,39,26,23,39,32,43]

"""
====================== Scoring Pipeline ========================
"""

correlation_file = '../correlation-simple.csv'
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
                formatVerboseOutput(summary_name,segment_count,score,quality,coverage,comprehension, results, segment_list,num_sentences,segs,scu_labels,pyramid_name)


    #scores = [raw_scores, quality_scores, coverage_scores, comprehension_scores]
    if print_table:
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
            raw_sc = sort(raw_scores)
            raw_corr = pearson(raw_sc, RAW)[0]
            w.writerow(['Correlation'] + [raw_corr])
            print('{:>16} | {:>.2f}'.format('Correlation', raw_corr*100))

    with open(correlation_file, 'a') as f:
    #     corr_w = csv.writer(f)
        raw_sc = sort(raw_scores)
    #     #quality_sc = sort(quality_scores)
    #     #coverage_sc = sort(quality_scores)
    #     #comprehension_sc = sort(comprehension_scores)

        raw_corr = pearson(raw_sc, RAW)[0]
        print "\tRaw Pearson Correlation", raw_corr
    #     #quality_corr = pearson(quality_sc, QUALITY)[0]
    #     #coverage_corr = pearson(coverage_sc, COVERAGE)[0]
    #     #comprehension_corr = pearson(comprehension_sc, COMP)[0]

    #     #line = [pyramid_name, raw_corr, quality_corr, coverage_corr, comprehension_corr]
    #     line = [pyramid_name, raw_corr]
    #     corr_w.writerow(line)



print '\n'
print 'Results written to %s' % results_file
print '\n'




