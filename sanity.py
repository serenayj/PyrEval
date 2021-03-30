#Wasih (02-22-20) Add sanity/confirm smooth run script
#Script to confirm installations
#1. Test installations first

#Wasih (02-26-20) Make conditional imports depending on Python version
import os
import sys
import glob

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser

try:
    import termcolor
except ImportError:
    print ('Please Install termcolor!')
    sys.exit(0)

from termcolor import colored

try:
    import nltk 
except ImportError:
    text = colored('Please Install nltk!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import sklearn 
except ImportError:
    text = colored('Please Install scikit-learn!', 'red', attrs = ['bold'])
    print (text)
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
except ImportError:
    text = colored('Please Install scipy!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import numpy
except ImportError:
    text = colored('Please Install numpy!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import networkx
except ImportError:
    text = colored('Please Install networkx!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import statistics
except ImportError:
    text = colored('Please Install statistics!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import pandas
except ImportError:
    text = colored('Please Install pandas!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

try:
    import theano
except ImportError:
    text = colored('Please Install theano!', 'red', attrs = ['bold'])
    print (text)
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
    text = colored('Stanford CoreNLP not present. Please extract it to %s Directory' % stanford_dir, 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

#3. Check if all necessary directories present or not
raw_peer_dir = config.get('Paths', 'RawPeerDir')
raw_model_dir = config.get('Paths', 'RawModelDir')
preprocess_dir = config.get('Paths', 'PreprocessDir')
pyramid_dir = config.get('Paths', 'PyramidDir')
scoring_dir = config.get('Paths', 'ScoringDir')

if os.path.exists(raw_peer_dir) == False:
    text = colored('Peers directory not present!. Please give some input', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(raw_model_dir) == False:
    text = colored('Model directory not present!. Please give some input', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(raw_model_dir) and len(glob.glob1(raw_model_dir, "*.txt")) < 4:
    text = colored('Model directory contains very few model summaries!. Please give atleast 4 summaries', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(raw_peer_dir) and len(glob.glob1(raw_peer_dir, "*.txt")) == 0:
    text = colored('Peers directory is empty!. Please give atleast a single text summary', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(preprocess_dir) == False:
    text = colored('Preprocess directory not present!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(pyramid_dir) == False:
    text = colored('Pyramid directory not present!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

if os.path.exists(scoring_dir) == False:
    text = colored('Scoring directory not present!', 'red', attrs = ['bold'])
    print (text)
    sys.exit(0)

text = colored('All Good to Go!', 'green', attrs = ['bold'])
print (text)


