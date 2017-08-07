
from lib_pyramid import readFiles, make_segs, pairwise, power_law, ComposeLayer2
from lib_pyramid import ComposeSegSets, SortDescendingWAS, BestFit, CheckConstraint1
from lib_pyramid import localBackTracking, RecursiveSettling, ComposeLayer1, Layer, GLobalBT
from lib_pyramid import pairwise_test
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from time import time
import copy
import pickle
import glob
import os


"""
=========================== Pipeline =================================
""" 

print("Reading Content")
#directories = glob.iglob('wise_crowd/*')
directories = glob.iglob('../Preprocess/wise_crowd_summaries/*')
segs, vecs = readFiles(directories)
print("Making Segments")
segpool = make_segs(segs, vecs)
pairwise_test(segpool, 5)

# thresholds = [85, 82, 80, 78, 75, 72, 70]
# tups = [(125, 1.0), (125, 1.5), (125, 2.0), (125, 2.5), (125, 3.0), 
#         (150, 1.0), (150, 1.5), (150, 2.0), (150, 2.5), (150, 3.0), 
#         (175, 1.0), (175, 1.5), (175, 2.0), (175, 2.5), (175, 3.0), 
#         (200, 1.0), (200, 1.5), (200, 2.0), (200, 2.5), (200, 3.0), 
#         (225, 1.0), (225, 1.5), (225, 2.0), (225, 2.5), (225, 3.0), 
#         (250, 1.0), (250, 1.5), (250, 2.0), (250, 2.5), (250, 3.0) ]

thresholds = [77]
tups = [(175, 2.0)]

for threshold in thresholds:
    for tup in tups:
        print('Using Threshold {}\n\ta = {} and b = {}'.format(threshold, tup[0], tup[1]))
        
        # Make Deep Copy of Segment Pool
        segmentpool = copy.deepcopy(segpool)
        segmentpool_length = len(segmentpool)
        
        
        # Build Pairwise Similarity Set
        BigSet2 = pairwise(segmentpool, 5, threshold)

        # For getting the coefficients combinations 
        #bf_dict = BruteForceLaw(len(segmentpool),5)
        bf_dict = tup
        '''            
        ================= Pyramid Building ==================
        '''
        timer = time()
    
        # N is the number of summaries used, indicates number of layers in pyramid
        N = 5
        
        # Pyramid is a list of lists and Pyramid_info is a list of Layer() objects
        Pyramid = range(5)
        Pyramid_info = range(5)

        # Build the first N -> 2 Layers of the Pyramid
        for n in range(N,1, -1):
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

        # Pickle Dump of Pyramid
        weight_dict = {}
        for n, weight in enumerate(weights):
            weight_dict[cu_ids[n]] = weight
        scu_with_vecs = {}
        for scu_id, vec_to_find_list in scu_vecs.items():
            vectors = []
            for vector_to_find in vec_to_find_list:
                for segment in segmentpool:
                    if segment.id == vector_to_find:
                        vectors.append(segment.vec)
            scu_with_vecs[scu_id] = [weight_dict[scu_id], vectors]
        with open('../Scoring/pyrs/pyramids/' + fname + '.p', 'wb') as f:
            pickle.dump(scu_with_vecs, f)
        f.close()

        # Print out sizes
        with open('../Scoring/sizes/' + fname + '.size', 'w') as f:
            for n, pyr in enumerate(Pyramid_info):
                  f.write(str(pyr.length) + '\n')
        f.close()
                  
        # Console Output
        print('With Threshold {}%'.format(threshold))
        print('a: {} | b: {}').format(tup[0], tup[1])  
        print('cost: %.2f' % cost)
        print('was: %.2f' % was)
        print('Time: {}'.format(str(done - timer)))
        for n, pyr in enumerate(Pyramid_info):
            print('Layer {} has size {} | Upperbound {}'.format(n+1, pyr.length, pyr.capacity))
        if len(all_seg_ids) == len(set(all_seg_ids)):
            print('Length of Segment Pool as Beginning: {} vs Length at End{}'.format(segmentpool_length,
                                                                                      len(segmentpool)))
            print('Number of Segments Used: %d' % len(all_seg_ids))
            print('All Segment IDs are Unique')




    
