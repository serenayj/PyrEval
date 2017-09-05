""" Process XML Pyramids """
"""
from bs4 import BeautifulSoup as Soup
import sys

xml_file = sys.argv[1]
handler = open(xml_file).read()

soup = Soup(handler, 'lxml')

scus = soup.find_all('scu')

scu_by_weight = {}
for scu in scus:
	contributors = scu.find_all('contributor')
 	if len(contributors) in scu_by_weight.keys():
 		scu_by_weight[len(contributors)].append([contributor['label'] for contributor in contributors])
 	else:
 		scu_by_weight[len(contributors)] = [[contributor['label'] for contributor in contributors]]



 fname = xml_file[:xml_file.rfind('.')] + '.segs'
 with open(fname, 'w') as f:
 	for weight, scu in scu_by_weight.items():
# 		lines = []
#  		line = str(weight) + '&'
#  		for n, cu in enumerate(scu):
#  			subline = line +'0&' + str(n) + '&'
#  			for j, c in enumerate(cu):
#  				subsubline = subline + str(j) + '&' + c + '\n'
#  				lines.append(subsubline)
#  		for line in lines:
#  			f.write(line)

"""


import sys
inp = sys.argv[1]
import pickle

handler = open(inp, 'r')

lines = handler.readlines()

scus = {}

for line in lines:
	line = line.split('&')
	scu_id = line[0] + '.' + line[2]
	if scu_id in scus.keys():
		vector = line[4].strip('\n').replace('[', '').replace(']', '')
		vector = [float(i) for i in vector.split(',')]
		scus[scu_id].append(vector)
	else:
		scus[scu_id] = []
		vector = line[4].strip('\n').replace('[', '').replace(']', '')
		vector = [float(i) for i in vector.split(',')]
		scus[scu_id].append(vector)

sorted_keys = sorted(scus.keys(), key=lambda x: int(''.join(x.split('.'))))


scu_for_pickle = {}
for n, key in enumerate(sorted_keys):
	vector = scus[key]
	scu_for_pickle[n] = [key.split('.')[0], vector]

pickle_name = inp.replace('.ls', '.p')
with open(pickle_name, 'wb') as f:
	pickle.dump(scu_for_pickle, f)





