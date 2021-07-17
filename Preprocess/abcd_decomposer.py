import os
import sys
import pickle
from lib_parser import *

'''
input arguments:
<coreNLP_name>: coreNLP output
<summary_ind>: index of summary
<dir1>: directory of output (../Preprocess/peer etc.)
<sentence_file>: sentence file name
<abcd_dir>: location of ABCD code
<glove_dir>: location of glove file (glove.6B.100d.txt)
'''

coreNLP_name = sys.argv[1]
summary_ind = sys.argv[2]
dir1 = sys.argv[3]
sentence_file = sys.argv[4]
abcd_dir = sys.argv[5]
glove_dir = sys.argv[6]

# create output file name which is a '.segs' file
output_dir = os.path.join(dir1, summary_ind)
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

output_file_name = os.path.join(output_dir, getFilename(coreNLP_name) + '.segs')

# now create a temporary output file, test.pkl as required by process_test.py in abcd code
temp_file_name = os.path.join(output_dir, 'test')
current_dir = os.getcwd()
os.chdir(abcd_dir)

# for process_test.py, inputs: sentence_file, coreNLP_file, output_file
command = 'python3 process_test.py ' + sentence_file + ' ' + coreNLP_name + ' ' + temp_file_name
os.system(command)

# now need to run test.py, inputs: test.pkl, glove_dir, output_file
output_dict_file_name = os.path.join(output_dir, 'output.pkl')
temp_file_name = temp_file_name + '.pkl'
command = 'python3 test.py ' + temp_file_name + ' ' + glove_dir + ' ' + output_dict_file_name
os.system(command)

# now, output.pkl is created: parse it and make the segmentation file
# first get a list of sentences
f = open(sentence_file, 'r')
sentences = f.readlines()
f.close()
sentences = [s.strip() for s in sentences]

# open the dictionary, output.pkl
f2 = open(output_dict_file_name, 'rb')
output_dict = pickle.load(f2)
f2.close()

with open(output_file_name, 'w') as handle:
	for sent_num, values in output_dict.items():
		segments = values['pred_strs']
		if len(segments) > 1:
			# need to write two segmentations: 1st one is default of the complete sentence
			handle.write(str(summary_ind) + '&' + str(sent_num + 1) + '&' + '0' + '&' + '0' + '&' + sentences[sent_num] + '\n')
			seg_num = 0
			for seg in segments:
				handle.write(str(summary_ind) + '&' + str(sent_num + 1) + '&' + '1' + '&' + str(seg_num) + '&' + seg + '\n')
				seg_num += 1
		else:
			handle.write(str(summary_ind) + '&' + str(sent_num + 1) + '&' + '0' + '&' + '0' + '&' + sentences[sent_num] + '\n')

# finally delete the temporary files: test and output.pkl
os.remove(temp_file_name)
os.remove(output_dict_file_name)
