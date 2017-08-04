from sklearn.metrics.pairwise import cosine_similarity as cos
import pickle
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import copy
import statistics 




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
            scores[scu.id] = scu.averageSimilarity(segment_embedding)
        scores = sorted(scores.items(), key=lambda x:x[1][0], reverse=True)[:2]
        scores = [(score[0], score[1][0]) for score in scores]
        return scores

class Vertex():
    def __init__(self, segment_id, scu_list):
        self.id = segment_id
        self.scu_list = scu_list
        self.neighbors = []
        self.useMe = True
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
    f = open(fname, 'r')
    segments = f.readlines()
    sentences = {}
    for segment in segments:
        segment = segment.split('&')
        if segment[1] in sentences.keys():
            embedding = segment[4].strip('\n').replace('[', '').replace(']', '')
            embedding = [float(i) for i in embedding.split(',')]
            sentences[segment[1]].append({'&'.join(segment[:4]):embedding})
        else:
            embedding = segment[4].strip('\n').replace('[', '').replace(']', '')
            embedding = [float(i) for i in embedding.split(',')]
            sentences[segment[1]] = [{'&'.join(segment[:4]):embedding}]
    sentences = sorted(sentences.items(), key=lambda x: int(x[0]))
    sentences = [sentence[1] for sentence in sentences]
    sents = []
    for sentence in sentences:
        segmentations = {}
        for segment in sentence:
            for segment_id, embedding in segment.items():
                if segment_id.split('&')[2] in segmentations.keys():
                    segmentations[segment_id.split('&')[2]][segment_id] = embedding
                else:
                    segmentations[segment_id.split('&')[2]] = {}
                    segmentations[segment_id.split('&')[2]][segment_id] = embedding
        sents.append(segmentations)
    return dict(enumerate(sents))

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
    for scu, segments in scu_and_segments.items():
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
    return segment_and_scu

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
