# PyrEval

This is the package for running PyrEval. 

## Introduction 
PyrEval is a tool to construct a content model of semantically coherent units discovered from a small sample of expert reference summaries of one or more source texts, and to apply the content model to automatically evaluate the content of new summaries. It automates a manual method that was developed over a decade ago [1], and found to be extremely reliable [2, 3]. The tool is aimed at two audiences. It can help educators evaluate students’ summaries for content; this is important because summarization is a commonly used vehicle to teach reading and writing skills, and to assess students’ knowledge of content [4, 5]. It can also be used in evaluation of automated summarizers [5]. 

## Installation Requirement 
1. Python 2.7 (or Anaconda2)
2. Stanford CoreNLP System, see download https://stanfordnlp.github.io/CoreNLP/index.html
3. Pacakges: nltk, glob, sklearn, bs4, numpy, scipy

## HOW TO USE 
### Step 0: Download and Run CoreNLP to get the preprocess xml files 
Copy stanford.py to the Stanford CoreNLP folder, then run command: 
```
python stanford.py path_to_raw_text mode 
```
where mode: 1: peer summries; 2: wise_crowd_summaries, 3:test_summaries. 

 