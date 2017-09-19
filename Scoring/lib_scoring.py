from sklearn.metrics.pairwise import cosine_similarity as cos
import pickle
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import copy
import statistics 
from bs4 import BeautifulSoup as Soup
import sys
import os
sys.path.append('../Preprocess/')
from weiwei import vectorize



"""
===================== Segments =====================
"""

class Segment():
    def __init__(self, sentence_id, segment_id, segments = []):
        self.sentence_id = sentence_id
        self.segment_id = segment_id
        self.segments = segments
        self.length = len(segments)
        self.used = False
        self.text = {}
        self.scu_text_pairs = {}
    def addSegment(self, segment):
        self.segments += segment
    def setText(self, text):
        self.text = text
    def setSCUTextPairs(self, scu_text_pairs):
        self.scu_text_pairs = scu_text_pairs

def parseMaxSegment(segment_list, number_of_sentences, used_sentence_list):
    candidates = [segment for segment in segment_list if segment.used == False]
    return_list = []
    for i in range(1, number_of_sentences + 1):
        if i not in used_sentence_list:
            max_c = 0
            for candidate in candidates:
                if candidate.sentence_id == i:
                    if candidate.length > max_c:
                        max_c = candidate
            if max_c != 0:
                max_c.used = True
                return_list.append(max_c)
    return return_list


"""
===================== SCU ======================
"""

class SCU():
    def __init__(self, scu_id, weight, segment_embeddings):
        self.id = scu_id
        self.embeddings = segment_embeddings
        self.weight = weight
    def averageSimilarity(self, segment_embedding):
        normalizer = len(self.embeddings)
        similarity = 0
        for embedding in self.embeddings:
            similarity += cos(embedding, segment_embedding)[0][0]
        if similarity / normalizer < 0.5:
            return None
        else:
            return [similarity / normalizer, self.weight]


"""
============== Sentence Graph ====================
"""

class SentenceGraph():
    """ Given a Sentence, build a graph from segmentations """
    def __init__(self, sentence_id, segmentations, scus):
        self.sentence_id = sentence_id
        self.segmentations = segmentations
        self.graph = self.buildGraph(scus)
    def buildGraph(self, scus):
        segmentations = self.segmentations
        graph = []
        for segmentation, segments in segmentations.items():
            hypernode = []
            for segment_id, segment_embedding in segments.items():
                scu_list = self.findSCUs(segment_embedding, scus)
                hypernode.append(Vertex(segment_id, scu_list))
            graph.append(hypernode)
        return graph
    def findSCUs(self, segment_embedding, scus):
        scores = {}
        for scu in scus:
            average = scu.averageSimilarity(segment_embedding)
            if average != None:
                scores[scu.id] = average
        scores = sorted(scores.items(), key=lambda x:x[1][0], reverse=True)[:2]
        scores = [(score[0], score[1][0]) for score in scores]
        return scores

class Vertex():
    def __init__(self, segment_id, scu_list):
        self.id = segment_id
        self.scu_list = scu_list
        self.neighbors = []
        self.useMe = True
        self.max = False
        self.used = True
    def getWeight(self):
        ###### Weight Scheme 1
        #return sum([scu[1] for scu in self.scu_list]) / len(self.scu_list)
        ###### Weight Scheme 2
        return sum([scu[0] for scu in self.scu_list])
        ###### Weight Scheme 3
        #return max([scu[1] for scu in self.scu_list])

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        neighbor.we_are_neighbors(self)
    def add_neighbors(self, *args):
        for neighbor in args:
            self.neighbors.append(neighbor)
            neighbor.we_are_neighbors(self)
    def we_are_neighbors(self, neighbor):
        self.neighbors.append(neighbor)
    def delete(self):
        self.useMe = False
        for neighbor in self.neighbors:
            neighbor.useMe = False


class SummaryGraph():
    def __init__(self, sentences, scus):
        self.sentences = [SentenceGraph(n, segmentations, scus) for n, segmentations in sentences.items()]
        for sentence in self.sentences:
            self.buildInnerEdgesList(sentence.graph)
        self.vertices = self.buildOuterEdgesList()
        self.independentSet = self.buildIndependentSet()
    def buildInnerEdgesList(self, sentenceGraph):
        nodes = list(sentenceGraph)
        while len(nodes) > 0:
            node = nodes[0]
            for vertex in node:
                for n in nodes[1:]:
                    for vert in n:
                        vertex.add_neighbor(vert)
            nodes = nodes[1:]
    def buildOuterEdgesList(self):
        sentences = list(self.sentences)
        vertex_list = []
        while (len(sentences) > 0):
            sentence = sentences[0]
            for node in sentence.graph:
                for vertex in node:
                    vertex_list.append(vertex)
                    for sent in sentences[1:]:
                        for n in sent.graph:
                            for vert in n:
                                if set(vertex.scu_list) & set(vert.scu_list):
                                    vertex.add_neighbor(vert)
            sentences.remove(sentence)
        return vertex_list
    def buildIndependentSet(self):
        vertices = copy.deepcopy([vertex for vertex in self.vertices if vertex.useMe == True])
        independentSet = []
        while len(vertices) != 0:
            vertex = max(vertices, key=lambda x: x.getWeight())
            independentSet.append(vertex)
            vertex.delete()
            vertices = [vert for vert in vertices if vert.useMe == True]
        return independentSet


"""
============= Reading Human Pyramids ============
"""

def getSoup(fname):
    handler = open(fname, 'r')
    soup = Soup(handler, 'lxml')
    return soup
def getSCUs(soup):
    scus = {}
    for scu in soup.find_all('scu'):
        labels = []
        scu_id = scu.get('uid')
        children = scu.find_all('contributor')
        for child in children:
            labels.append(child.get('label'))
        scus[int(scu_id)] = labels
    return scus 
def vecotirizationProtocol(fname):
    cwd = os.getcwd()
    os.chdir('../Preprocess/')
    fname = '../Scoring/' + fname
    vecs = vectorize(fname)
    os.chdir(cwd)
    return vecs
def vectorizeSCUs(scus):
    reconstruction = {}
    scs = {}
    document = []
    scu_ids = []
    scus = sorted(scus.items(), key=lambda x: len(x[1]), reverse=True)
    for scu_id, contributor in scus:
        scu_ids.append((scu_id, len(contributor)))
        scs[scu_id] = contributor
        document += contributor
    fname = 'temp/tmp.segs'
    with open(fname, 'w') as f:
        for line in document:
            f.write(line + '\n')
    f.close()
    vecs = vecotirizationProtocol(fname)
    j = 0
    for scu_id, length in scu_ids:
        reconstruction[scu_id] = vecs[j:length]
        vecs = vecs[length:]
    return reconstruction, scs
def readPyramid(fname):
    soup = getSoup(fname)
    scus = getSCUs(soup)
    recon, scus = vectorizeSCUs(scus)
    scu_objects = []
    layer_sizes = []
    for scu_id, labels in recon.items():
        scu_objects.append(SCU(scu_id, len(labels), labels))
    size = max(scu_objects, key=lambda x: x.weight).weight
    j = 0
    for scu in scu_objects:
        if scu.weight < size:
            layer_sizes.append(j)
            j = 1
            size = scu.weight
        else:
            j += 1
    else:
        layer_sizes.append(j)
    fname = 'sizes/' + filename(fname) + '.size'
    with open(fname, 'w') as f:
        for size in layer_sizes:
            f.write(str(size) + '\n')
    f.close()
    return scu_objects, scus



"""
============= Function Definitions ===============
"""

def buildSCUlist(scu_pickle):
    with open(scu_pickle, 'rb') as f:
        SCUs = pickle.load(f)
    f.close()
    scus =[]
    for scu_id, weight_embeddings in SCUs.items():
        scus.append(SCU(scu_id, int(weight_embeddings[0]), weight_embeddings[1]))
    return scus

def sentencesFromSegmentations(fname):
    f = open(fname, 'r') # Read in file
    segments = f.readlines() # Each line is a segment
    sentences = {} # Initialize Empty Directory
    for segment in segments:
        segment = segment.split('&')
        if segment[1] in sentences.keys(): # segment[1] is the sentence identitiy
            embedding = segment[4].strip('\n').replace('[', '').replace(']', '') # rip out the embedding from the line
            embedding = [float(i) for i in embedding.split(',')] # cast elements to float with list comprehension
            sentences[segment[1]].append({'&'.join(segment[:4]):embedding}) # segment id: embedding
        else:
            embedding = segment[4].strip('\n').replace('[', '').replace(']', '')
            embedding = [float(i) for i in embedding.split(',')]
            sentences[segment[1]] = [{'&'.join(segment[:4]):embedding}]
    sentences = sorted(sentences.items(), key=lambda x: int(x[0])) # nested dictionary (sentence_key, sentence_stuff)
    sentences = [sentence[1] for sentence in sentences]
    sents = []
    segmentations_in_summary = 0
    seg_ids = []
    for n, sentence in enumerate(sentences):
        segmentations = {}
        count = {}
        for segment in sentence:
            for segment_id, embedding in segment.items():
                seg_ids += [segment_id]
                if segment_id.split('&')[2] in segmentations.keys():
                    segmentations[segment_id.split('&')[2]][segment_id] = embedding
                    count[segment_id.split('&')[2]] += 1
                else:
                    segmentations[segment_id.split('&')[2]] = {}
                    segmentations[segment_id.split('&')[2]][segment_id] = embedding
                    count[segment_id.split('&')[2]] = 1
        sents.append(segmentations)
        segmentations_in_summary += max(count.items(), key=lambda x: x[1])[1]
    segment_list = sortSegmentations(dict(enumerate(sents)))
    return dict(enumerate(sents)), segmentations_in_summary, segment_list

def sortSegmentations(segmentation_dict):
    segment_list = []
    for sentence, segmentations in segmentation_dict.items():
        sentence_id = int(sentence) + 1
        #print sentence_id
        for segment_id, segmentation_list in segmentations.items():
            for segment_id, segmentation in segmentation_list.items():
                segment_id = int(segment_id.split('&')[2])

                segment_list += [Segment(sentence_id,segment_id, segmentation)]
    return segment_list




def buildSCUcandidateList(vertices):
    scu_and_segments = {}
    vertices = sorted(vertices, key = lambda x: int(x.id.split('&')[1]))
    for vertex in vertices:
        for scu in vertex.scu_list:
            if scu[0] in scu_and_segments.keys():
                scu_and_segments[scu[0]][vertex.id] = scu[1]
            else:
                scu_and_segments[scu[0]] = {}
                scu_and_segments[scu[0]][vertex.id] = scu[1]
    return scu_and_segments

def processResults(scu_and_segments, independentSet):
    scu_and_segments = copy.deepcopy(scu_and_segments)
    chosen = []
    chosen_scus = []
    segment_and_scu = {}
    segment_ids = []
    for scu, segments in scu_and_segments.items():
        segment_ids += segments
        for segment in segments.keys():
            if segment in chosen:
                del segments[segment] 
        if len(segments) != 0:
            median = statistics.median_high(segments.values())
        for segment, value in segments.items():
            if value == median:
                segment_and_scu[segment] = scu
                #print(segment, scu)
                chosen.append(segment)
                chosen_scus.append(scu)
                del segments[segment]
    segment_ids = list(set(segment_ids))
    return segment_and_scu, len(segment_ids)

def scusBySentences(segment_scu):
    sentences = {}
    for segment, scu in segment_scu.items():
        sentence_id = segment.split('&')[1]
        if sentence_id in sentences.keys():
            sentences[sentence_id][segment] = scu
        else:
            sentences[sentence_id] = {}
            sentences[sentence_id][segment] = scu
    return sentences

def getScore(sentences, scus):
    sentence_scores = {}
    matched_cus = 0
    for sentence, segments in sentences.items():
        lil_score = 0
        for segment, scu in segments.items():
            for s in scus:
                if scu == s.id:
                    #print s.weight
                    lil_score += s.weight
                    matched_cus += 1
        sentence_scores[sentence] = lil_score
    return sum(sentence_scores.values()), matched_cus

def filename(fname):
    slash = fname.rfind('/') + 1
    dot = fname.rfind('.')
    return fname[slash:dot]



'''
================== Scores and Results ================
'''

def recall(results, fname):
    path = 'pan/op_' + filename(fname) + 'pan'
    orig_scus = []
    with open(path, 'r') as f:
        for line in f:
            line.split('\t')
            if type(line[0]) == int:
                if line[0] not in orig_scus:
                    orig_scus.append(line[0])

def maxRawScore(count_by_weight, num):
    counts = sorted(count_by_weight.items(), key=lambda x:x[0], reverse=True)
    result = 0
    for count in counts:
        if num >= count[1]:
            num = num - count[1]
            result = result + (count[0]*count[1])
        else:
            result = result + (num*count[0])
            num = 0
    return result

def getLayerSizes(fname):
    f = open(fname, 'r')
    lines = f.readlines()
    count_by_weight = {}
    count = 0
    for n, line in enumerate(lines):
        count_by_weight[n + 1] = int(line.strip())
        count += (n+1) * int(line.strip())
    avg = count/(n+1)
    return count_by_weight, avg

def retrieveSeg(segID, seg_list):
    for seg_id, seg in seg_list.items():
        if segID == seg_id:
            return seg

def formatVerboseOutput(summary_name,segment_count,score,quality,coverage,comprehension, results, segment_list,num_sentences,segs,scu_labels, pyramid_name):
    w,h = terminal_size()
    summary_name_len = len(summary_name)
    
    used_sentence_list = []
    check_tups = {}
    
    for s in segment_list:
        for res, scu in results.items():
            r = res.split('&')
            sentence_id = int(r[1])
            segment_id = int(r[2])
            segtation_id = int(r[3])
        
            if s.sentence_id == sentence_id:
                if s.segment_id == segment_id:
                    check_tup = (s.sentence_id, s.segment_id)
                    if check_tup in check_tups.keys():

                        if segtation_id not in check_tups[check_tup]:
                            check_tups[check_tup].append(segtation_id)
                            s.scu_text_pairs[int(r[3])] = scu
                            if sentence_id not in used_sentence_list:
                                used_sentence_list.append(sentence_id)
                    else:
                        check_tups[check_tup] = [segtation_id]
                        s.used = True
                        s.scu_text_pairs[int(r[3])] = scu
                        if sentence_id not in used_sentence_list:
                                used_sentence_list.append(sentence_id)


    for s in [s for s in segment_list if s.used == True]:
        for segment_id, segment in segs.items():
            sentence_id = int(segment_id.split('&')[1])
            segmentation_id = int(segment_id.split('&')[3])
            segment_id = int(segment_id.split('&')[2])
            if sentence_id == s.sentence_id:
                if segment_id == s.segment_id:
                    s.text[segmentation_id] = segment

    non_used_segments = parseMaxSegment(segment_list, num_sentences, used_sentence_list)
    for s in non_used_segments:
        for segment_id, segment in segs.items():
            sentence_id = int(segment_id.split('&')[1])
            segmentation_id = int(segment_id.split('&')[3])
            segment_id = int(segment_id.split('&')[2])
            if sentence_id == s.sentence_id:
                if segment_id == s.segment_id:
                    s.text[segmentation_id] = segment
    
    newSegmentList = [s for s in segment_list if s.used == True]

    cu_list = []
    for s in newSegmentList:
        for seg_index, text in s.text.items():
            if seg_index in s.scu_text_pairs.keys():
                cu = (s.scu_text_pairs[seg_index], len(scu_labels[s.scu_text_pairs[seg_index]]))
                cu_list.append(cu)
    if len(cu_list) != 0:
        cu_list = sorted(cu_list, key=lambda x:x[1], reverse=True)
        cu_line = ''
        for cu in cu_list[:len(cu_list)-1]:
            cu_line += str(cu[0]) + ': ' + str(cu[1]) + ', '
        cu_line += str(cu_list[len(cu_list)-1][0]) + ': ' + str(cu_list[len(cu_list)-1][1])
    else:
        cu_line = 'No Content Units'



    print '\n' + '#'*(w/2 - summary_name_len + 2) + '  ' + summary_name + '  ' + '#'*(w/2 - summary_name_len + 2) + '\n'
    print 'Pyramid: %s' % pyramid_name
    print 'No. Segments in Summary: {}'.format(segment_count)
    print '{:>17}: {:>10}\n{:>17}: {:>10.3f}\n{:>17}: {:>10.3f}\n{:>17}: {:>10.3f}'.format('Raw', score, 'Quality', quality, 'Coverage', coverage, 'Comprehensive', comprehension)
    print '{:>17}: \t{}\n'.format('Content Unit List', cu_line)


    for s in newSegmentList:
        print "Sentence: %d, Segmentation %d" % (s.sentence_id, s.segment_id)
        for seg_index, text in s.text.items():
            if seg_index in s.scu_text_pairs.keys():
                print "\tSegment: %d | Content Unit: %d [Weight: %d]" % (seg_index, s.scu_text_pairs[seg_index], len(scu_labels[s.scu_text_pairs[seg_index]]))
                print(wrap_string(s.text[seg_index].strip(), '\tSegment: ................. '))
                content_unit = scu_labels[s.scu_text_pairs[seg_index]]
                for n, cu_part in enumerate(content_unit):
                    if n == 0:
                        print wrap_string(cu_part, '\tContent Unit: ............ (%d) ' % (n+1))
                    else:
                        print wrap_string(cu_part, "\t" + " "*13 + " ............ (%d) "  % (n+1))                            
            else:
                print "\tSegment: %d | Content Unit: None" % seg_index
                print(wrap_string(s.text[seg_index].strip(), '\tSegment: ................. '))
        print "\n"
    print "\n"
    print "="*w
    print "\n"


"""
======= etc ==========
"""

def terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def wrap_string(text, starter_text):
    # text is the part of the string that your want to wrap
    # started_text could also be a point about which the text wraps
    w,h = terminal_size()
    text = text.replace('\n', '')
    tabs = starter_text.count('\t')
    new_starter_text = starter_text.replace('\t', '')
    wrap_point = len(new_starter_text) + 8*tabs
    wrap_indicator = int(w) - wrap_point
    num_line_wraps = len(text) / wrap_indicator
    left_over = len(text) % wrap_indicator
    lines = []
    for i in range(num_line_wraps):
        lines.append(text[i:((i+1)*wrap_indicator)] + '\n')
    lines.append(text[-left_over:])
    lines = [starter_text + lines[0]] + [" "*wrap_point + line for line in lines[1:]]
    return ''.join(lines)
















