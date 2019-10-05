# Written by: Purushartha Singh
# Last Update: 07/04/19
# The code is written with Yanjun Gao's package by the same name as reference

# Libraries needed: bs4(beautifulSoup4), nltk

# Add import statements
from lib_parser import *

# Command line arguments for filename, output directory, and summary index
fname = sys.argv[1]
ext = sys.argv[3]
summary_index = sys.argv[2]

# Initial input initialization
content = open(fname).read()
fname = getFilename(fname)

ext = ext+"/"+str(summary_index)

if not os.path.exists(ext):
    os.makedirs(ext)

soup = BeautifulSoup(content,'lxml')

basic = []
for links in soup.find_all("dependencies"):
    if links.get("type") == "enhanced-dependencies":
        basic.append(links)

parse = []
for links in soup.find_all("parse"):
    parse.append(links)

tokens = soup.find_all("tokens")

###################################################################################################
# Processing
###################################################################################################

sentence_segmentations = []
dep_sentences = get_depparse(basic)

# Insert write logs?

# Variable Declaration. Check usage

# segments = {}
idseg = {}
# count
lists_nodes = {}
segment_set = {}

output = open(ext+'/'+fname+".segs", 'w')


# Loop for iterating for each sentence
for sentence_num in range(len(dep_sentences)):
    #print ("="*25+"Sentence Number: "+str(sentence_num+1)+" "+"="*25)

    dep_sentence = dep_sentences[sentence_num+1]
    token = tokens[sentence_num]

    tree, treeList, numList = getTreeInfo(parse[sentence_num])

    # print the constituency parse tree
    #tree.pretty_print()
    lists_nodes[sentence_num] = treeList
    segmentation_index = 0
    #print("Segmentation " + str(segmentation_index)+ " : Complete sentence")
    segment_index = 0
    # Outputting the whole sentence as the first segmentation
    outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, numList)
    segmentation_index += 1
    segment_index = 0
    # Splitting the sentence into constituent parts
    s_split = compoundSplit(tree)
    segtreelist = []
    combinations = []
    segments = []

    # If a split takes place
    if len(s_split) > 1:
        segments, segtreelist = makeSubtreeList(s_split, numList)
        #print("Segmentation " + str(segmentation_index) + " : Initial segmenting & combinations (S Sibling splitting)")
        # Outputs the split segments as a separate segmentation
        for i in range(len(s_split)):
            outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, segments[i])
            segment_index += 1
        segmentation_index += 1
        segment_index = 0
        # If there are more than 2 segments, produces output segmentations with adjacent combinations
        if len(s_split) > 2:
            combinations, _ = combineSegs(segments)
            if len(combinations)>5:
                combinations = combinations[:5]
            for x in combinations:
                #print("Segmentation " + str(segmentation_index) + ":")
                for i in range(len(x)):
                    outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, x[i])
                    segment_index += 1
                segmentation_index += 1
                segment_index = 0
    else:
        # If no splits happen, makes the original lists as output
        segtreelist = [[int(item) for item in treeList]]
        s_split = [tree]
        segments = [numList]


    # List of splits that happen due to split rules
    ruleSplits = []

    for i, st in enumerate(s_split):
        # Rule 1 for Verb SBAR (Needs edits for edgecases)
        sbar_ind, sbar = ruleSBAR(st, segments[i])
        if len(sbar) > 0:
            ruleSplits.append([sbar_ind, sbar, i])

        # Rule 2 for checking conjoined VP without nouns
        vpslist = getcvps(st)
        nplist = getnp(st)

        # If VP matching the criteria found
        if len(vpslist) > 0:
            deplist = []

            # Get dependency noun index for each VP
            for each in vpslist:
                dependency = getdependency(each, dep_sentence,segtreelist[i])
                if dependency > 0:

                    # Find the NP associated with the dependency
                    nptree = findnp(dependency, nplist)
                    if nptree is not -1:
                        deplist.append([nptree, each])
            res = []
            res_ind = []
            # Continues to next step if no noun phrase found
            if len(deplist) > 1:
                # Adds the split to the list for prcessing in the next step
                for each in deplist:
                    vpconj, vpconj_list = joinTree(each)
                    res.append(vpconj)
                    res_ind.append(vpconj_list)
                fullres, fullres_ind = addAll(res, res_ind, segtreelist[i], segments[i])
                ruleSplits.append([fullres_ind, fullres, i])
                if len(sbar) > 0:
                    res_index, res, maxsplit_flag = splitAll(sbar_ind, deplist, segments[i])
                    if maxsplit_flag:
                        for i in range(len(res)):
                            outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, res[i])
                            segment_index += 1
                        segmentation_index += 1
                        segment_index = 0



    # Printing out all the rule segments with the rest of the sentence as a separate segmentation
    if len(ruleSplits) > 0:
        #print("Segmentation " + str(segmentation_index) + " : Rule segmenting & combinations (SBAR and Conjoined VP)")
        maxsplit, samesegs = rejoinRuleSplits(ruleSplits, segments)
        if len(maxsplit) > 5:
            maxsplit = maxsplit[:5]
        for segmt in maxsplit:
            for i in range(len(segmt)):
                outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, segmt[i])
                segment_index += 1
            segmentation_index += 1

            segment_index = 0

        # Printing out recombinations of the segments as new segmentations for all possible adjacent combinations
        for i, segmt in enumerate(maxsplit):
            res = combineSplitSegs(segmt, samesegs[i])
            #print("Segmentation " + str(segmentation_index)+" : ")
            if len(res) > 5:
                res = res[:5]
            for sen in res:
                for i in range(len(sen)):
                    outputSegs(output, summary_index, sentence_num+1, segmentation_index, segment_index, sen[i])
                    segment_index += 1
                segmentation_index += 1
                segment_index = 0
output.close()
