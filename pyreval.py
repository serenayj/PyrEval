import os
import sys
import shutil
from subprocess import call
#Wasih (02-19-20) Use functions instead of calling script
from splitsent import *
from Stanford.stanford import *
from Pyramid.pyramid import pyramidmain

#Wasih (02-26-20) Make conditional imports depending on Python version
#Wasih (02-27-20) Define a variable for python version & then use it
PYTHON_VERSION = 2
if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser
    PYTHON_VERSION = 3

#Wasih (02-21-20) Use termcolor to display colored text
from termcolor import colored

#Wasih (02-27-20) Use imports of traceback and logging to print any exception
import logging
import traceback

INPUT_STR = '>>> '

INSTRUCTIONS = """
Welcome to the PyrEval Launcher.

NOTES:
- All model summary files should be in ./Raw/model/
- All peer summary files should be in ./Raw/peers/
- The Stanford Core NLP Tools package should be in ./Stanford/

0: Automatic mode (not recommended)

1: Preprocess - Split sentences
2: Run Stanford Core NLP Tools
3: Preprocess - Main
4: Build pyramids
5: Score pyramids
Score Flags (Usage: 5 <flag>):
-a: Print verbose output on terminal and store in PyrEval/log directory
-l: Equivalent to -a
-t: Print scoring results to terminal and save in Results.csv file

c: Clean directories
i: Change python interpreter

To quit, type q.
"""
#Wasih (02-21-21) more convenient quitting

def autorun(params):
    splitsent(params)
    stanford(params)
    preprocess(params)
    pyramid(params)
    score(params)

def splitsent(params):
    #call(py_interp + [split_script, raw_peer_dir, split_peer_dir])
    #call(py_interp + [split_script, raw_model_dir, split_model_dir])
    #Wasih (02-19-21) Use functions instead of calling script
    #Wasih (02-21-21) Add user friendly lines
    try:
        #Wasih (02-21-21) Check for split directory present or not, if not then create it
        if not os.path.exists(split_peer_dir):
            os.makedirs(split_peer_dir)
        
        if not os.path.exists(split_model_dir):
            os.makedirs(split_model_dir)
        
        split(raw_peer_dir, split_peer_dir)
        split(raw_model_dir, split_model_dir)
        text = colored('\n\n********************Splitting of Sentences/normalization completed!********************\n\n', 'green', attrs = ['bold'])
        print (text)	
    except Exception as e:
        text = colored('\n\n********************Splitting of Sentences/normalization Threw an Error!********************\n\n', 'red', attrs = ['bold'])
        logging.error(traceback.format_exc())
        #print(e)
        print (text)
    
def stanford(params):
    os.chdir(stanford_dir)
    #call(py_interp + [stanford_script, split_peer_dir, '1', base_dir])
    #call(py_interp + [stanford_script, split_model_dir, '2', base_dir])
    
    #Wasih (02-19-21) Use functions instead of calling script
    try:
        try:
            stanfordmain(split_peer_dir, 1, base_dir, seg_method)
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
            text = colored('\n\n********************Stanford Pipelining of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
            print (text)
    
        os.chdir(stanford_dir)
        try:
            stanfordmain(split_model_dir, 2, base_dir, seg_method)
            text = colored('\n\n********************Stanford Pipelining of Sentences completed!********************\n\n', 'green', attrs = ['bold'])
            print (text)
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
            text = colored('\n\n********************Stanford Pipelining of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
            print (text)    
       	
    except Exception as e:
        logging.error(traceback.format_exc())
        print(e)
        text = colored('\n\n********************Stanford Pipelining of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
        print (text)    
    os.chdir(base_dir)

def preprocess(params):
    os.chdir(preprocess_dir)
    try:
        try:
            call(py_interp + [preprocess_script, '1', ' '.join(py_interp)])
            #prepro('1')
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
            text = colored('\n\n********************Preprocessing of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
            print (text)
        try:
            call(py_interp + [preprocess_script, '2', ' '.join(py_interp)])
            #prepro('2')
            text = colored('\n\n********************Preprocessing of Sentences completed!********************\n\n', 'green', attrs = ['bold'])
            print (text)
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
            text = colored('\n\n********************Preprocessing of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
            print (text)
	
    except Exception as e:
        logging.error(traceback.format_exc())
        print(e)
        text = colored('\n\n********************Preprocessing of Sentences threw an Error!********************\n\n', 'red', attrs = ['bold'])
        print (text)
    os.chdir(base_dir)

def pyramid(params):
    os.chdir(pyramid_dir)
    #call(py_interp + [pyramid_script])
    try:
        #Wasih (02-21-21) Deep Clean (folders scu, sizes, pyrs/pyramids too)
        if not os.path.exists(os.path.join(scoring_dir, 'scu')):
            os.makedirs(os.path.join(scoring_dir, 'scu'))
        
        if not os.path.exists(os.path.join(scoring_dir, 'sizes')):
            os.makedirs(os.path.join(scoring_dir, 'sizes'))

        if not os.path.exists(os.path.join(scoring_dir, 'pyrs', 'pyramids')):
            os.makedirs(os.path.join(scoring_dir, 'pyrs', 'pyramids'))
        
        if not os.path.exists(os.path.join(scoring_dir,'temp')):
            os.makedirs(os.path.join(scoring_dir, 'temp'))

        if not os.path.exists(os.path.join(scoring_dir,'temp')):
            os.makedirs(os.path.join(scoring_dir, 'temp'))
        #Wasih (02-19-21) Use functions instead of calling script
        #Wasih (06-13-21) Create user specified pyramid file
        pyramidmain(pyramid_name)
        text = colored('\n\n********************Pyramid Building of Reference summaries completed!********************\n\n', 'green', attrs = ['bold'])
        print (text)	
    except Exception as e:
        logging.error(traceback.format_exc())
        print(e)
        text = colored('\n\n********************Pyramid Building of Reference summaries threw an Error!********************\n\n', 'red', attrs = ['bold'])

        print (text)
    os.chdir(base_dir)

def score(params):
    os.chdir(scoring_dir)
    try:
        call_s = py_interp + [scoring_script] + params
        call(call_s)
        text = colored('\n\n********************Scoring of summaries completed!********************\n\n', 'green', attrs = ['bold'])
    except Exception as e:
        logging.error(traceback.format_exc())
        print(e)
        text = colored('\n\n********************Scoring of summaries threw an Error!********************\n\n', 'red', attrs = ['bold'])
        print (text)

    os.chdir(base_dir)

def clean(params):
    def remove_files(files):
        for file in files:
            try:
                os.remove(file)
            except OSError as e:
                error_print('Cannot delete ' + file, e2=e)

    def remove_dirs(dirs):
        for dir in dirs:
            try: 
                shutil.rmtree(dir)
            except OSError as e:
                error_print('Cannot delete ' + file, e2=e)

    def clean_splits_peers():
        if os.path.exists(split_peer_dir):
            files = [os.path.join(split_peer_dir,x) for x in os.listdir(split_peer_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep clean; remove split directory too
            shutil.rmtree(split_peer_dir)
        
    def clean_splits_model():
        if os.path.exists(split_model_dir):
            files = [os.path.join(split_model_dir,x) for x in os.listdir(split_model_dir) if x[0] != '.']
            remove_files(files)
           #Wasih (02-21-20) Deep clean; remove split directory too
            shutil.rmtree(split_model_dir)
 
    def clean_preprocess_peers():
        if os.path.exists(preprocess_peers_dir):
            files = [os.path.join(preprocess_peers_dir,x) for x in os.listdir(preprocess_peers_dir) if x[0] != '.']
            dirs = list(filter(os.path.isdir, files))
            files = list(filter(os.path.isfile, files))
            remove_files(files)
            remove_dirs(dirs)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(preprocess_peers_dir)

    def clean_preprocess_model():
        if os.path.exists(preprocess_model_dir):
            files = [os.path.join(preprocess_model_dir,x) for x in os.listdir(preprocess_model_dir) if x[0] != '.']
            dirs = list(filter(os.path.isdir, files))
            files = list(filter(os.path.isfile, files))
            remove_files(files)
            remove_dirs(dirs)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(preprocess_model_dir)

    def clean_pyramid():
        #Wasih (02-27-20) First check if scores.txt present, only then delete it
        if os.path.exists(os.path.join(pyramid_dir, 'scores.txt')) == True:
            remove_files( [os.path.join(pyramid_dir,'scores.txt')] )

    def clean_scoring_pyrs():
        if os.path.exists(os.path.join(scoring_dir, 'pyrs')):
            pyrs_dir = os.path.join(scoring_dir,'pyrs','pyramids')
            files = [os.path.join(pyrs_dir,x) for x in os.listdir(pyrs_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(os.path.join(scoring_dir, 'pyrs'))

    def clean_scoring_scu():
        if os.path.exists(os.path.join(scoring_dir, 'scu')):
            scu_dir = os.path.join(scoring_dir,'scu')
            files = [os.path.join(scu_dir,x) for x in os.listdir(scu_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(scu_dir)

    def clean_scoring_sizes():
        if os.path.exists(os.path.join(scoring_dir, 'sizes')):
            sizes_dir = os.path.join(scoring_dir,'sizes')
            files = [os.path.join(sizes_dir,x) for x in os.listdir(sizes_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(sizes_dir)

    def clean_scoring_temp():
        if os.path.exists(os.path.join(scoring_dir, 'temp')):
            temp_dir = os.path.join(scoring_dir,'temp')
            files = [os.path.join(temp_dir,x) for x in os.listdir(temp_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(temp_dir)

    def clean_ext():
        if os.path.exists(ext_dir):
            files = [os.path.join(ext_dir,x) for x in os.listdir(ext_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(ext_dir)

    def clean_log():
        if os.path.exists(log_dir):
            files = [os.path.join(log_dir,x) for x in os.listdir(log_dir) if x[0] != '.']
            remove_files(files)
            #Wasih (02-21-20) Deep Clean; remove folders too
            shutil.rmtree(log_dir)

    def clean_base():
        files = [os.path.join(base_dir,x) for x in os.listdir(base_dir) if (os.path.splitext(x)[1] == '.csv' and x[0] != '.')]
        remove_files(files)

    clean_splits_peers()
    clean_splits_model()
    clean_preprocess_peers()
    clean_preprocess_model()
    clean_pyramid()
    #Wasih (02-22-20) Remove results.csv
    output_file = config.get('Paths', 'OutputFile')
    if os.path.exists(output_file):
        os.remove(output_file)
    clean_scoring_pyrs()
    clean_scoring_scu()
    clean_scoring_sizes()
    clean_scoring_temp()
    clean_ext()
    clean_log()
    clean_base()
    
    #Wasih (02-21-20) Print colored text for user-friendliness
    text = colored('Everything Cleaned!', 'yellow')
    print (text)

def change_py_interp(params):
    global py_interp
    py_interp = params

def error_print(e1, e2=None):
    print('ERROR: ' + e1)
    if e2:
        print(e2)

if __name__ == "__main__":
    print(INSTRUCTIONS)
    config = configparser.ConfigParser()
    config.read('parameters.ini')
    base_dir = os.path.dirname(os.path.realpath(__file__))
    # TODO: user-changeable
    #Wasih (02-20-20) Make ConfigParser
    py_interp = [config.get('Paths', 'PythonInterp')]
    raw_peer_dir = config.get('Paths', 'RawPeerDir')
    raw_model_dir = config.get('Paths', 'RawModelDir')
    split_peer_dir = config.get('Paths', 'SplitPeerDir')
    split_model_dir = config.get('Paths', 'SplitModelDir')
    split_script = config.get('Paths', 'SplitScript')
    stanford_dir = config.get('Paths', 'StanfordDir')
    stanford_script = config.get('Paths', 'StanfordScript')
    abcd_dir = config.get('Paths', 'ABCDDir')
    seg_method = config.get('Segmentation', 'Method')
    preprocess_dir = config.get('Paths', 'PreprocessDir')
    preprocess_script = config.get('Paths', 'PreprocessScript')
    preprocess_peers_dir = config.get('Paths', 'PreprocessPeersDir')
    preprocess_model_dir = config.get('Paths', 'PreprocessModelDir')
    pyramid_dir = config.get('Paths', 'PyramidDir')
    pyramid_script = config.get('Paths', 'PyramidScript')
    scoring_dir = config.get('Paths', 'ScoringDir')
    scoring_script = config.get('Paths', 'ScoringScript')
    ext_dir = config.get('Paths', 'ExtDir')
    log_dir = config.get('Paths', 'LogDir')
    pyramid_name = config.get('Paths', 'OutputPyramidName')
    choice_dict = {
        '0': autorun,
        '1': splitsent,
        '2': stanford,
        '3': preprocess,
        '4': pyramid,
        '5': score,
        'c': clean,
        'i': change_py_interp,
        'q': quit,
    }    
    while True:
        try:
            #Wasih (02-27-20) If python 2 => use raw_input, else use input
            if PYTHON_VERSION == 2:
                user_in = raw_input(INPUT_STR)
            else:
                user_in = input(INPUT_STR)
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if (len(user_in) == 0):
            continue
        tokens = user_in.split()
        command = tokens[0]
        params = tokens[1:]
        try:
            choice = choice_dict[tokens[0]]
        except KeyError:
            error_print('Bad command')
            continue
        #Wasih (02-21-20) Add ext dir if not present (deleted in deep cleaning)
        if tokens[0] == 'q':
            break
        else:
            if not os.path.exists(ext_dir):
                os.makedirs(ext_dir)
            choice(params)

