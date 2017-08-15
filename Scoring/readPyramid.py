from bs4 import BeautifulSoup as Soup
import sys
import os
sys.path.append('../Preprocess/')
from weiwei import vectorize

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
	document = []
	scu_ids = []
	scus = sorted(scus.items(), key=lambda x: len(x[1]), reverse=True)
	for scu_id, contributor in scus:
		scu_ids.append((scu_id, len(contributor)))
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
	return reconstruction

def readPyramid(fname):
	soup = getSoup(fname)
	scus = getSCUs(soup)
	scus = vectorizeSCUs(scus)
	return scus








