#Wasih (02-22-20) Add sanity/confirm smooth run script
#Script to confirm installations
#1. Test installations first
import ConfigParser as configparser
import os
import sys

try:
    import nltk 
except ImportError, e:
    print 'Please Install nltk!'
    sys.exit(0)

try:
    import sklearn 
except ImportError, e:
    print 'Please Install scikit-learn!'
    sys.exit(0)
'''
try:
    import beautifulsoup4
except ImportError, e:
    print 'Please Install beautifulsoup4!'
    sys.exit(0)
'''
try:
    import scipy 
except ImportError, e:
    print 'Please Install scipy!'
    sys.exit(0)
try:
    import numpy
except ImportError, e:
    print 'Please Install numpy!'
    sys.exit(0)
try:
    import networkx
except ImportError, e:
    print 'Please Install networkx!'
    sys.exit(0)
try:
    import statistics
except ImportError, e:
    print 'Please Install statistics!'
    sys.exit(0)
try:
    import pandas
except ImportError, e:
    print 'Please Install pandas!'
    sys.exit(0)
try:
    import theano
except ImportError, e:
    print 'Please Install theano!'
    sys.exit(0)
try:
    import termcolor
except ImportError, e:
    print 'Please Install termcolor!'
    sys.exit(0)

#2. Check stanford corenlp present or not
config = configparser.ConfigParser()
config.read('parameters.ini')
stanford_dir = config.get('Paths', 'StanfordDir')
coreNlpDir = ""
for filename in os.listdir(stanford_dir):
    if (os.path.isdir(os.path.join(stanford_dir, filename)) and 'stanford' in filename):
        coreNlpDir = filename
        break
if coreNlpDir == "":
    print 'Stanford CoreNLP not present. Please extract it to %s Directory' % stanford_dir
    sys.exit(0)

#3. Check if all necessary directories present or not
raw_peer_dir = config.get('Paths', 'RawPeerDir')
raw_model_dir = config.get('Paths', 'RawModelDir')
preprocess_dir = config.get('Paths', 'PreprocessDir')
pyramid_dir = config.get('Paths', 'PyramidDir')
scoring_dir = config.get('Paths', 'ScoringDir')

if os.path.exists(raw_peer_dir) == False:
    print 'Peers directory not present!. Please give some input'
    sys.exit(0)

if os.path.exists(raw_model_dir) == False:
    print 'Model directory not present!. Please give some input'
    sys.exit(0)

if os.path.exists(raw_model_dir) and len(os.listdir(raw_model_dir)) < 5:
    print 'Model directory contains very few model summaries!. Please give atleast 4 summaries'
    sys.exit(0)

if os.path.exists(preprocess_dir) == False:
    print 'Preprocess directory not present!'
    sys.exit(0)

if os.path.exists(pyramid_dir) == False:
    print 'Pyramid directory not present!'
    sys.exit(0)

if os.path.exists(scoring_dir) == False:
    print 'Scoring directory not present!'
    sys.exit(0)

from termcolor import colored
text = colored('All Good to Go!', 'green', attrs = ['bold'])
print text


