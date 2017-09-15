
from lib_pyramid import readFiles, make_segs, pairwise, power_law, ComposeLayer2
from lib_pyramid import ComposeSegSets, SortDescendingWAS, BestFit, CheckConstraint1
from lib_pyramid import localBackTracking, RecursiveSettling, ComposeLayer1, Layer, GLobalBT
from lib_pyramid import pairwise_test
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from time import time
import copy
import glob
import xml.etree.cElementTree as ET

"""
=========================== Pipeline =================================
""" 

#print("Reading Content")
#directories = glob.iglob('wise_crowd/*')
directories = list(glob.iglob('../Preprocess/wise_crowd_summaries/*'))
segs, vecs, N = readFiles(directories)
#print("Making Segments")
segpool = make_segs(segs, vecs)
pairwise_test(segpool, N)

# thresholds = [73,72,71,70,69,68,67]
# tups = [(64., 1.5), (64., 1.75), (64., 2.0), 
#         (64., 2.25), (64., 2.5), (80., 1.5), 
#         (80., 1.75), (80., 2.0), (80., 2.25), 
#         (80., 2.5), (90., 1.5), (90., 1.75), 
#         (90., 2.0), (90., 2.25), (90., 2.5), 
#         (100., 1.5), (100., 1.75), (100., 2.0), 
#         (100., 2.25), (100., 2.5), (110., 1.5), 
#         (110., 1.75), (110., 2.0), (110., 2.25), 
#         (110., 2.5), (120., 1.5), (120., 1.75), 
#         (120., 2.0), (120., 2.25), (120., 2.5)]

thresholds = [77]
tups = [(175., 2.0)]

for threshold in thresholds:
    for tup in tups:
        #print('Using Threshold {}\n\ta = {} and b = {}'.format(threshold, tup[0], tup[1]))
        
        # Make Deep Copy of Segment Pool
        segmentpool = copy.deepcopy(segpool)
        segmentpool_length = len(segmentpool)
        
        
        # Build Pairwise Similarity Set
        BigSet2 = pairwise(segmentpool, N, threshold)

        # For getting the coefficients combinations 
        #bf_dict = BruteForceLaw(len(segmentpool),5)
        bf_dict = tup
        '''            
        ================= Pyramid Building ==================
        '''
        timer = time()
    
        # N is the number of summaries used, indicates number of layers in pyramid
        
        # Pyramid is a list of lists and Pyramid_info is a list of Layer() objects
        Pyramid = range(N)
        Pyramid_info = range(N)

        # Build the first N -> 2 Layers of the Pyramid
        for n in range(N,1, -1):
            #print "Building Layer %d" % n

            y_n = power_law(n, bf_dict)
            
            # If we are building the second layer of the Pyramid
            if n == 2:
                layer = ComposeLayer2(BigSet2, segmentpool)
                
            # Else, build pyramid using Clique Algorithm
            else:
                layer = ComposeSegSets(BigSet2, segmentpool, n)
                
            # Sorting Algorithm for Segment Sets and Yield Best Fitting Layer
            layer = SortDescendingWAS(layer)
            layer = BestFit(layer, n, segmentpool, y_n)
            
            # Set Properties of Layer Object
            length = len(layer)
            obj = Layer(n)
            obj.length = length
            obj.size = length * n
            obj.capacity = y_n
            
            # Assign objects to lists
            Pyramid[n-1] = layer
            Pyramid_info[n-1] = obj
            
            # Check whether the given layer respects contraints
            constraint = CheckConstraint1(length,n, N,Pyramid_info)
            obj.constraint1 = constraint
            
            # If we are looking at any layer between N-1 and 2 and the contraint is False...
            if (constraint == False) and (n != N):
                #print("\tCalling Local Backtracking")
                status, segmentpool, Pyramid, Pyramid_info, current = localBackTracking(layer, n,
                                                                                      segmentpool,
                                                                                      Pyramid_info,
                                                                                      Pyramid, BigSet2,
                                                                                      N, bf_dict)
                if status: # Local Backtracking Ran Succesfully
                    layer = current
                    length = len(layer)
                    obj = Pyramid_info[n-1]
                    obj.length = length
                    obj.size = length * n
                    obj.constraint1 = True
                    Pyramid_info[n-1] = obj
                    Pyramid[n-1] = layer
                    
            # Settle Nodes Recursively because some layers were changed in Local Backtracking
            segmentpool = RecursiveSettling(Pyramid, segmentpool)

        # Build Layer 1
        #print "Building Layer 1"
        bs1, segmentpool = ComposeLayer1(segmentpool)
        Pyramid[0] = bs1
        bottom = Layer(0)
        bottom.length = len(bs1)
        bottom.size = bottom.length
        bottom.constraint1 = True
        bottom.capacity = power_law(1, bf_dict)
        Pyramid_info[0] = bottom

        # print('Active Segments: %d' % len([segment for segment in segmentpool if 
        #                                    segment.status == False]))
        
        # Global Backtracking settles contraints problems in all Layers
        segmentpool, Pyramid_info, Pyramid = GLobalBT(Pyramid_info, Pyramid, 
                                                      N, segmentpool, bf_dict, BigSet2)
        # DONE!
        done = time()

        
        
        '''
        ================= Format Output =================
        '''
        
        # Get total Number of Segments used in the Pyramid
        length = 0
        for p in Pyramid:
            length += len(p)

        # lists and variables to be used for readable output of pyramid
        cu_ids = []
        weights = []
        labels = []
        all_seg_ids = []
        count = 0
        was = 0
        cost = 0
        scu_vecs = {}

        score = 0
        
        # Iterate through Pyramid, make list assignments, update variables
        for n, p in enumerate(reversed(Pyramid)):
            cost += float(len(Pyramid[n])) * (1 / float(n+1))
            for j, scu in enumerate(p):
                was += scu['WAS']
                l = len(Pyramid) - n
                if l > 1:
                    l = l * (l - 1)
                    l = l / 2
                score += scu['WAS']/l
                for _ in range(len(Pyramid) - n):
                    cu_ids.append(count)
                    weights.append(str(len(Pyramid)-n))
                segs = [scu['seg%d' % (p + 1)] for p in range(len(Pyramid) - n)]
                seg_ids = [scu['seg%did' % (p + 1)] for p in range(len(Pyramid) - n)]
                all_seg_ids += seg_ids
                for j, seg in enumerate(segs):
                    labels.append(str(seg))
                seg_ids = [scu['seg%did' % (p + 1)] for p in range(len(Pyramid) - n)]
                vectors_to_find = []
                for seg_id in seg_ids:
                    vectors_to_find.append(seg_id)
                scu_vecs[count] = vectors_to_find
                count += 1
        
        # Writing Readable version of Pyramid
        fname = 'pyramid_t{}_a{}_b{}'.format(threshold, tup[0], tup[1])
        lines = []
        if cu_ids:
            for j, i in enumerate(cu_ids):
                line = 'SCU' + '\t' + str(i) + '\t' + str(weights[j]) + '\t' + labels[j]
                #print(line)
                lines.append(line)
        with open('scu/' + fname + '.pyr', 'w') as f:
            for line in lines:
                #print(line)
                f.write(line + '\n')
        f.close()

        root = ET.Element('Pyramid')
        p = 0
        scu = ET.SubElement(root,'scu', uid=str(p))
        for j, i in enumerate(cu_ids):
            if i > p:
                p = i
                scu = ET.SubElement(root,'scu', uid=str(p))
            ET.SubElement(scu, 'contributor', label = labels[j])
        tree = ET.ElementTree(root)
        tree.write('../Scoring/pyrs/pyramids/' + fname + '.pyr')
                  
        # Console Output
        # print('With Threshold {}%'.format(threshold))
        # print('a: {} | b: {}').format(tup[0], tup[1])  
        # print('cost: %.2f' % cost)
        # print('was: %.2f' % was)
        print('Pyramid: %s' % fname)
        print('Time: {}'.format(str(done - timer)))
        print('Pyramid .pyr file stored in PyrEval/Scoring/pyrs/pyramid')
        print('Pyramid .size file stored in PyrEval/Scoring/sizes')
        print('Readable pyramid file stored in PyrEval/Scoring/scus')
        # for n, pyr in enumerate(Pyramid_info):
        #     print('Layer {} has size {} | Upperbound {}'.format(n+1, pyr.length, pyr.capacity))
        # if len(all_seg_ids) == len(set(all_seg_ids)):
        #     print('Length of Segment Pool as Beginning: {} vs Length at End {}'.format(segmentpool_length,
        #                                                                               len(segmentpool)))
        #     print('Number of Segments Used: %d' % len(all_seg_ids))
        #     print('All Segment IDs are Unique')




    
