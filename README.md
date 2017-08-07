# PyrEval

This is the package for running PyrEval. 

## Introduction 
PyrEval is a tool to construct a content model of semantically coherent units discovered from a small sample of expert reference summaries of one or more source texts, and to apply the content model to automatically evaluate the content of new summaries. It automates a manual method that was developed over a decade ago [1], and found to be extremely reliable [2, 3]. The tool is aimed at two audiences. It can help educators evaluate students’ summaries for content; this is important because summarization is a commonly used vehicle to teach reading and writing skills, and to assess students’ knowledge of content [4, 5]. It can also be used in evaluation of automated summarizers [5]. 

## Installation Requirement 
1. Python 2.7 (or Anaconda2)
2. Perl
3. Stanford CoreNLP System[6], see download https://stanfordnlp.github.io/CoreNLP/index.html. 
4. Python Pacakges: nltk, glob, sklearn, bs4, numpy, scipy, networkx

## Raw texts
At the very beginning, you need to split your raw text into one sentence per line. There are three folders for you to place your raw texts. 
- Preprocess/wise_crowd_summaries: the folder for model(referenced) summaries
- Preprocess/peer_summaries: the folder for the summaries you want to score
- Preprocess/test_summaries: others 

## Components and Directories
This package contains two major components: Build the pyramid and Score the peer summaries by the pyramid.  

Here is an explanation of 4 folders under PyrEval. 
- Preprocess: For preprocessing your raw texts(step 0 and 1). They will be proprocessed by Stanford CoreNLP system and vectorizations. 
- Pyramid: For preprocessed model summaries(step 2). We build the pyramid from model summaries under wise_crowd. And output the pyramid for future use. 
- Scoring: For scoring peer summaries by the pyramid(step3).  
- Summaries: TBD


## HOW TO USE 
### Step 0: Download and Run Stanford CoreNLP to get the preprocess xml files 
Copy stanford.py to the Stanford CoreNLP folder, then run command: 
```
python stanford.py path_to_raw_text mode path_to_PyrEval
```
where mode: 1: peer summries; 2: wise_crowd_summaries, 3:test_summaries. 
E.g: 
```
python stanford.py Users\blah\raw_text 2 Users\blah\PyrEval 
```

### Step 1: Preprocess files for sentence vectorizations 
We are using vectorizations method by WTMF, created by Weiwei Guo. [7][8]

cd to Preprocess directory, then run preprocess.py:
```
python preprocess.py mode 
``` 
where mode: 1: peer summries; 2: wise_crowd_summaries, 3:test_summaries. 

### Step2: Build Pyramid
The script will take input from Preprocess/wise_crowd_summaries/*, and output the pyramid as .pyr file to Pyramid/scu/. 

Locate to the Pyramid folder and run the script: 
```
python pyramid.py 
```

### Step3: Score the summaries 


## Reference
[1] Nenkova, Ani and Rebecca J. Passonneau. Evaluating content selection in summarization: The Pyramid Method. Joint Annual Meeting of Human Language Technology and the North American chapter of the Association for Computational Linguistics (HLT/NAACL). Boston, MA. June, 2004.

[2] Nenkova, Ani, Rebecca J. Passonneau, and Kathleen McKeown. "The pyramid method: Incorporating human content selection variation in summarization evaluation." ACM Transactions on Speech and Language Processing (TSLP) 4.2 (2007): 4.

[3] Passonneau, Rebecca J. 2010. Formal and functional assessment of the pyramid method for summary content evaluation. Natural Language Engineering 16:107-131. Copyright Cambridge University Press.

[4] Passonneau, Rebecca J., et al. "Wise Crowd Content Assessment and Educational Rubrics." International Journal of Artificial Intelligence in Education (2016): 1-27.

[5] Yang, Qian, Rebecca J. Passonneau, and Gerard de Melo. "PEAK: Pyramid Evaluation via Automated Knowledge Extraction." AAAI. 2016.

[6] Manning, Christopher D., Mihai Surdeanu, John Bauer, Jenny Finkel, Steven J. Bethard, and David McClosky. 2014. The Stanford CoreNLP Natural Language Processing Toolkit In Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics: System Demonstrations, pp. 55-60.

[7] Weiwei Guo, Wei Liu and Mona Diab. "Fast Tweet Retrieval with Compact Binary Codes". In Proceedings of COLING, 2014, Dublin, Ireland.

[8] Weiwei Guo and Mona Diab. "Modeling Sentences in the Latent Space". In Proceedings of ACL, 2012, Jeju, Korea.
