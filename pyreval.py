
import os
import sys
import shutil
from subprocess import call

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

c: Clean directories
i: Change python interpreter

To quit, type nothing and press return.
"""

def autorun(params):
    splitsent(params)
    stanford(params)
    preprocess(params)
    pyramid(params)
    score(params)

def splitsent(params):
    call(py_interp + [split_script, raw_peer_dir, split_peer_dir])
    call(py_interp + [split_script, raw_model_dir, split_model_dir])

def stanford(params):
    os.chdir(stanford_dir)
    call(py_interp + [stanford_script, split_peer_dir, '1', base_dir])
    call(py_interp + [stanford_script, split_model_dir, '2', base_dir])
    os.chdir(base_dir)

def preprocess(params):
    os.chdir(preprocess_dir)
    call(py_interp + [preprocess_script, '1', ' '.join(py_interp)])
    call(py_interp + [preprocess_script, '2', ' '.join(py_interp)])
    os.chdir(base_dir)

def pyramid(params):
    os.chdir(pyramid_dir)
    call(py_interp + [pyramid_script])
    os.chdir(base_dir)

def score(params):
    os.chdir(scoring_dir)
    call_s = py_interp + [scoring_script] + params
    call(call_s)
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
        files = [os.path.join(split_peer_dir,x) for x in os.listdir(split_peer_dir) if x[0] != '.']
        remove_files(files)

    def clean_splits_model():
        files = [os.path.join(split_model_dir,x) for x in os.listdir(split_model_dir) if x[0] != '.']
        remove_files(files)

    def clean_preprocess_peers():
        files = [os.path.join(preprocess_peers_dir,x) for x in os.listdir(preprocess_peers_dir) if x[0] != '.']
        dirs = list(filter(os.path.isdir, files))
        files = list(filter(os.path.isfile, files))
        remove_files(files)
        remove_dirs(dirs)

    def clean_preprocess_model():
        files = [os.path.join(preprocess_model_dir,x) for x in os.listdir(preprocess_model_dir) if x[0] != '.']
        dirs = list(filter(os.path.isdir, files))
        files = list(filter(os.path.isfile, files))
        remove_files(files)
        remove_dirs(dirs)

    def clean_pyramid():
        remove_files( [os.path.join(pyramid_dir,'scores.txt')] )

    def clean_scoring_pyrs():
        pyrs_dir = os.path.join(scoring_dir,'pyrs','pyramids')
        files = [os.path.join(pyrs_dir,x) for x in os.listdir(pyrs_dir) if x[0] != '.']
        remove_files(files)

    def clean_scoring_scu():
        scu_dir = os.path.join(scoring_dir,'scu')
        files = [os.path.join(scu_dir,x) for x in os.listdir(scu_dir) if x[0] != '.']
        remove_files(files)

    def clean_scoring_sizes():
        sizes_dir = os.path.join(scoring_dir,'sizes')
        files = [os.path.join(sizes_dir,x) for x in os.listdir(sizes_dir) if x[0] != '.']
        remove_files(files)

    def clean_scoring_temp():
        temp_dir = os.path.join(scoring_dir,'temp')
        files = [os.path.join(temp_dir,x) for x in os.listdir(temp_dir) if x[0] != '.']
        remove_files(files)

    def clean_ext():
        files = [os.path.join(ext_dir,x) for x in os.listdir(ext_dir) if x[0] != '.']
        remove_files(files)

    def clean_base():
        files = [os.path.join(base_dir,x) for x in os.listdir(base_dir) if (os.path.splitext(x)[1] == '.csv' and x[0] != '.')]
        remove_files(files)

    clean_splits_peers()
    clean_splits_model()
    clean_preprocess_peers()
    clean_preprocess_model()
    clean_pyramid()
    clean_scoring_pyrs()
    clean_scoring_scu()
    clean_scoring_sizes()
    clean_scoring_temp()
    clean_ext()
    clean_base()

def change_py_interp(params):
    global py_interp
    py_interp = params

def error_print(e1, e2=None):
    print('ERROR: ' + e1)
    if e2:
        print(e2)

print(INSTRUCTIONS)

base_dir = os.path.dirname(os.path.realpath(__file__))
# TODO: user-changeable
py_interp = ['python']
raw_peer_dir = os.path.join(base_dir,'Raw','peers')
raw_model_dir = os.path.join(base_dir,'Raw','model')
split_peer_dir = os.path.join(raw_peer_dir,'split')
split_model_dir = os.path.join(raw_model_dir,'split')
split_script = os.path.join(base_dir,'split-sent.py')
stanford_dir = os.path.join(base_dir,'Stanford')
stanford_script = os.path.join(stanford_dir, 'stanford.py')
preprocess_dir = os.path.join(base_dir,'Preprocess')
preprocess_script = os.path.join(preprocess_dir, 'preprocess.py')
preprocess_peers_dir = os.path.join(preprocess_dir,'peer_summaries')
preprocess_model_dir = os.path.join(preprocess_dir,'wise_crowd_summaries')
pyramid_dir = os.path.join(base_dir,'Pyramid')
pyramid_script = os.path.join(pyramid_dir, 'pyramid.py')
scoring_dir = os.path.join(base_dir,'Scoring')
scoring_script = os.path.join(scoring_dir, 'scoring.py')
ext_dir = os.path.join(base_dir, 'ext')

choice_dict = {
      '0': autorun,
      '1': splitsent,
      '2': stanford,
      '3': preprocess,
      '4': pyramid,
      '5': score,
      'c': clean,
      'i': change_py_interp,
}

while True:
    try:
        user_in = raw_input(INPUT_STR)
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
    tokens = user_in.split()
    command = tokens[0]
    params = tokens[1:]
    try:
        choice = choice_dict[tokens[0]]
    except KeyError:
        error_print('Bad command')
        continue
    choice(params)

