#    Copyright (C) 2017 Yanjun Gao

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import lib_scoring
import os
import textwrap


#Written by Purushartha Singh (05/27/19)
#Puru (11-03-21) Added additional functionality for APCS visibility in output
#Puru (11-03-21) Fixed implementation of the print all tag



file_width = 100

##########################################################################
# Class definitions
##########################################################################

# A class holding all the arguments related to the summary
class Summary():
    def __init__(self, summary_name, segment_count, segment_list, num_sentences, segs):
        self.summary_name = summary_name
        self.segment_count = segment_count
        self.segment_list = segment_list
        self.num_sentences = num_sentences
        self.segs = segs
        self.used_sentence_list = []
        self.check_tups = {}
        

# A class holding all the arguments related to the pyramid

class Pyramid():
    def __init__(self, scu_labels, pyramid_name):
        self.scu_labels = scu_labels
        self.pyramid_name = pyramid_name

# A class holding all the arguments related to scoring
class Scores():
    def __init__(self, score, quality, coverage, comprehension, qmax, cmax, avg):
        self.score = score
        self.quality = quality
        self.coverage = coverage
        self.comprehension = comprehension
        self.qmax = qmax
        self.cmax = cmax
        self.avg = avg

class Value():
    def __init__(self, metadata, value):
        _, self.sentid, self.segid, self.segmtid = metadata.split('&')
        self.scuid = value[0]
        self.apcs = value[1]
        self.scuwt = value[2]
        self.stdapcs = value[3]

##########################################################################
# Helper Functions
##########################################################################
# returns the width of the presently open terminal
def getWidth():
        import fcntl, termios, struct
        th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
        return tw

# Returns true if the segment has the same sentence id and segment id as the args
def segIsEqual(seg, sentence_id, segment_id):
    if seg.sentence_id == sentence_id and seg.segment_id == segment_id:
        return True
    else:
        return False

# Returns the sentence id, segment id, and segmentation id for the given arg line
def getMetadata(x):
    r = x.split('&')
    sentence_id = int(r[1])
    segment_id = int(r[2])
    segmentation_id = int(r[3])
    return sentence_id, segment_id, segmentation_id

# Prints the initial header containing the summary name, Pyramid name, and the number of segments in the summary
def printHeader(summary, pyramid, output, print_screen):
    w = getWidth()
    if print_screen:
        print(os.linesep)
    output.write('\n')
    if print_screen:
        print((summary.summary_name).center(w, '#'))
    output.write(summary.summary_name.center(file_width, '#'))
    output.write('\n')
    if print_screen:
        print((pyramid.pyramid_name).center(w, " "))
    output.write((pyramid.pyramid_name).center(file_width, " "))
    output.write('\n\n')
    if print_screen:
        print("\n{:>40}: {}".format("No. of segments in the summary", summary.segment_count))
    output.write("{:>40}: {}\n".format("No. of segments in the summary", summary.segment_count))

# Prints out all the scoring information
def printScores(scores, output, print_screen):
    if print_screen:
        print("{:>40}: {}".format("Raw", scores.score))
    output.write("{:>40}: {}\n".format("Raw", scores.score))
    if print_screen:
        print("{:>40}: {}".format("Maximum possible score with Raw", scores.qmax))
    output.write("{:>40}: {}\n".format("Maximum possible score with Raw", scores.qmax))
    if print_screen:
        print("{:>40}: {:.4f}".format("Quality", scores.quality))
    output.write("{:>40}: {:.4f}\n".format("Quality", scores.quality))
    if print_screen:
        print("{:>40}: {}".format("Average No. of SCUs", scores.avg))
    output.write("{:>40}: {}\n".format("Average No. of SCUs", scores.avg))
    if print_screen:
        print("{:>40}: {}".format("Maximum score with average No. of SCUs", scores.cmax))
    output.write("{:>40}: {}\n".format("Maximum score with average No. of SCUs", scores.cmax))
    if print_screen:
        print("{:>40}: {:.4f}".format("Coverage", scores.coverage))
    output.write("{:>40}: {:.4f}\n".format("Coverage", scores.coverage))
    if print_screen:
        print("{:>40}: {:.4f}".format("Comprehensive", scores.comprehension))
    output.write("{:>40}: {:.4f}\n".format("Comprehensive", scores.comprehension))


# Prints the footer at the end of the file
def printFooter(output, print_screen):
    w = getWidth()
    if print_screen:
        print(os.linesep)
    output.write('\n')
    if print_screen:
        print("="*w)
    output.write("="*file_width)
    if print_screen:
        print(os.linesep)
    output.write('\n')

# Function that makes a list of all the used and unused segments from the initial segment_list arg and returns the
# unused segments list and the linked scus for the used segments with the text added to the struct
def listSegments(summary, pyramid, results):
    for seg in summary.segment_list:
        #print ("seg" +str(seg.sentence_id) + " " + str(seg.segment_id))
        for res, scu in results.items():
            sentence_id, segment_id, segmentation_id = getMetadata(res)
            #print ("res" +str(sentence_id)+ " " + str(segment_id))# + " " + str(segmentation_id))
            if segIsEqual(seg,sentence_id,segment_id):
                #print ("match")
                check = (sentence_id,segment_id)
                if check in summary.check_tups.keys():
                    #print (check)
                    if segmentation_id not in summary.check_tups[check]:
                        summary.check_tups[check].append(segmentation_id)
                else:
                    summary.check_tups[check] = [segmentation_id]
                    seg.used = True
                seg.scu_text_pairs[segmentation_id] = scu
                if sentence_id not in summary.used_sentence_list:
                    summary.used_sentence_list.append(sentence_id)

    for s in [s for s in summary.segment_list if s.used == True]:
        for seg, segment in summary.segs.items():
            sentence_id, segment_id, segmentation_id = getMetadata(seg)
            if segIsEqual(s, sentence_id, segment_id):
                s.text[segmentation_id] = segment

    usedSegList = [s for s in summary.segment_list if s.used is True]
    scuList = []
    
    for s in usedSegList:
        for seg, text in s.text.items():
            if seg in s.scu_text_pairs.keys():
                scuList.append((s.scu_text_pairs[seg], len(pyramid.scu_labels[s.scu_text_pairs[seg]])))
                
    notused = [s for s in summary.segment_list if s.used == False]

    notusedSegList = []
    #print (summary.used_sentence_list)
    for i in range(1, summary.num_sentences + 1):
        if i not in summary.used_sentence_list:
            #print("not here" + str(i))
            missed = 0
            for each in notused:
                #print (each.sentenceid)
                if each.sentence_id == i:
                    if missed == 0 or len(each.segments) > len(missed.segments):
                        missed = each
            if missed != 0:
                missed.used = True
                notusedSegList.append(missed)
    #print (usedSegList)
    
    for s in notusedSegList:
        for seg, segment in summary.segs.items():
            sentence_id, segment_id, segmentation_id = getMetadata(seg)
            if segIsEqual(s, sentence_id, segment_id):
                s.text[segmentation_id] = segment

    
    newSegList = [s for s in summary.segment_list if s.used is True]
    return newSegList, scuList

# Prints the list of all the SCUs used in the file with their weight
def printScuList(scu_list, printfile, print_screen):
    if len(scu_list) is 0:
        output = 'No linked Content Units'
    else:
        scu_list = sorted(scu_list, key=lambda x:(10 - x[1], x[0]))
        """sorted_cu_list = {}
        for item in scu_list:
            if item[1] in sorted_cu_list.keys():
                sorted_cu_list[int(item[1])].append(item)
            else:
                sorted_cu_list[int(item[1])] = [item]
        cu_list = []
        for i in range(5, 0, -1):
            sorted_cu_list[i] = sorted(sorted_cu_list[i], key=lambda x:int(x[0]))
            scu_list.append(sorted_cu_list[i])
        
        # print(scu_list)"""
        cu_line = ''
        output = '[ID(Weight)]: '
        for scu in scu_list:
            output += (str(scu[0])+'('+str(scu[1])+'), ')
        output = output[:-2]
    if print_screen:
        print("\n{:>20}{} \n\n".format("Content Unit List ", output))
    printfile.write("\n\n{:>20}{} \n\n".format("Content Unit List ", output))

# Prints the segments and associated SCU for each segment of the summary
def printSegments(segList, scuList, pyramid, output, values, print_screen):
    for s in segList:
        if print_screen:
            print("\n\nSentence: {} | Segmentation: {}".format(s.sentence_id, s.segment_id))
        output.write("\n\nSentence: {} | Segmentation: {}".format(s.sentence_id, s.segment_id))

        for seg_index, text in s.text.items():
            if seg_index in s.scu_text_pairs.keys():
                if print_screen:
                    print("\n\tSegment ID: {} | Content Unit: {} [Weight: {}]".format(seg_index,s.scu_text_pairs[seg_index], len(pyramid.scu_labels[s.scu_text_pairs[seg_index]])))
                output.write("\n\n\tSegment ID: {} | Content Unit: {} [Weight: {}]".format(seg_index,s.scu_text_pairs[seg_index], len(pyramid.scu_labels[s.scu_text_pairs[seg_index]])))
                # key = str(s.sentence_id) + '&' + str(s.segment_id) + '&' + str(seg_index)
                # val_list = values[key]
                # match = val_list[0]
                # for val in val_list:
                    # if val.scuid == s.scu_text_pairs[seg_index]:
                        # match = val

                # print("\n\tSegment ID: {} | Content Unit: {} [Weight: {}] | APCS: {:.4f} +/- {:.4f}".format(seg_index,s.scu_text_pairs[seg_index], len(pyramid.scu_labels[s.scu_text_pairs[seg_index]]), val.apcs, val.stdapcs))
                # output.write("\n\n\tSegment ID: {} | Content Unit: {} [Weight: {}] | APCS: {:.4f} +/- {:.4f}".format(seg_index,s.scu_text_pairs[seg_index], len(pyramid.scu_labels[s.scu_text_pairs[seg_index]]), val.apcs, val.stdapcs))

                wrap_seg = textwrap.wrap(s.text[seg_index].strip(), width=getWidth()-38)
                if print_screen:
                    for i, line in enumerate(wrap_seg):
                        if i == 0:
                            print("\tSegment: .................... " + line)
                        else:
                            print("\t"+" "*9+".................... " + line)
                wrap_seg = textwrap.wrap(s.text[seg_index].strip(), width=file_width-34)
                for i, line in enumerate(wrap_seg):
                    if i == 0:
                        output.write("\n\tSegment: .................... " + line)
                    else:
                        output.write("\n\t"+" "*9+".................... " + line)
                # print("\n\tSegment: .................... {}".format(s.text[seg_index].strip()))
                # output.write("\n\tSegment: .................... {}".format(s.text[seg_index].strip()))

                content_unit = pyramid.scu_labels[s.scu_text_pairs[seg_index]]
                for n, cu_part in enumerate(content_unit):
                    wrap_seg = textwrap.wrap(cu_part, width = getWidth()-42)
                    wrap_file = textwrap.wrap(cu_part, width = file_width-38)
                    if n == 0:
                        if print_screen:
                            for i, line in enumerate(wrap_seg):
                                if i == 0:
                                    print("\tContent Unit: ............... ("+str(n+1)+") " + line)
                                else:
                                    print("\t"+" "*14 + "."*15+"     " + line)
                        for i, line in enumerate(wrap_file):
                            if i == 0:
                                output.write("\n\tContent Unit: ............... ("+str(n+1)+") " + line)
                            else:
                                output.write("\n\t"+" "*14 + "."*15+"     " + line)

                        #print("\tContent Unit: ............... ({}) {}".format(n+1, cu_part))
                        #output.write("\n\tContent Unit: ............... ({}) {}".format(n+1, cu_part))
                    else:
                        if print_screen:
                            for i, line in enumerate(wrap_seg):
                                if i == 0:
                                    print("\t              ............... ("+str(n+1)+") " + line)
                                else:
                                    print("\t"+" "*14 + "."*15+"     " + line)
                        for i, line in enumerate(wrap_file):
                            if i == 0:
                                output.write("\n\t              ............... ("+str(n+1)+") " + line)
                            else:
                                output.write("\n\t"+" "*14 + "."*15+"     " + line)

                        #print("\t              ............... ({}) {}".format(n+1, cu_part))
                        #output.write("\n\t              ............... ({}) {}".format(n+1, cu_part))
            else:
                if print_screen:
                    print("\n\tSegment ID: {} | Content Unit: None".format(seg_index))
                output.write("\n\n\tSegment ID: {} | Content Unit: None".format(seg_index))
                wrap_seg = textwrap.wrap(s.text[seg_index].strip(), width=getWidth()-38)
                if print_screen:
                    for i, line in enumerate(wrap_seg):
                        if i == 0:
                            print("\tSegment: .................... " + line)
                        else:
                            print("\t"+" "*9+".................... " + line)
                wrap_seg = textwrap.wrap(s.text[seg_index].strip(), width=file_width-34)
                for i, line in enumerate(wrap_seg):
                    if i == 0:
                        output.write("\n\tSegment: .................... " + line)
                    else:
                        output.write("\n\t"+" "*9+".................... " + line)


def getInfo(values):
    # print(values)
    V = {}
    for value in values:
        sz = len(value[1])
        for i in range(sz):
            if value[0][2:] in V.keys():
                V[value[0][2:]].append(Value(value[0], value[1][i]))
            else:
                V[value[0][2:]] = [Value(value[0], value[1][i])]
    # print(V.keys())
    return V


##########################################################################
####Wrapper Function
##########################################################################

def printEsumLogWrapper(summary_name, segment_count, score, quality, coverage, comprehension, q_max, c_max, avg, results, segment_list, num_sentences, segs, scu_labels, pyramid_name, log_file, values, print_screen):
    # creates instances of the wrapper classes and passes them to the main function
    s = Summary(summary_name, segment_count, segment_list, num_sentences, segs)
    r = Scores(score, quality, coverage, comprehension, q_max, c_max, avg)
    p = Pyramid(scu_labels, pyramid_name)
    v = getInfo(values)
    printEsumLog(s, r, p, v, results, log_file, print_screen)


##########################################################################
# Main Function
##########################################################################
def printEsumLog(summary, scores, pyramid, values, results, log_file, print_screen):

    output = open(log_file, "w+")
    printHeader(summary, pyramid, output, print_screen)
    printScores(scores, output, print_screen)
    
    segList, scuList = listSegments(summary, pyramid, results)

    printScuList(scuList, output, print_screen)
    printSegments(segList, scuList, pyramid, output, values, print_screen)
    printFooter(output, print_screen)
    output.close()


