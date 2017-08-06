# PyrEval

This is the package for running PyrEval. 

## Introduction 
PyrEval is a tool to construct a content model of semantically coherent units discovered from a small sample of expert reference summaries of one or more source texts, and to apply the content model to automatically evaluate the content of new summaries. It automates a manual method that was developed over a decade ago [1], and found to be extremely reliable [2, 3]. The tool is aimed at two audiences. It can help educators evaluate students’ summaries for content; this is important because summarization is a commonly used vehicle to teach reading and writing skills, and to assess students’ knowledge of content [4, 5]. It can also be used in evaluation of automated summarizers [5]. 

## Installation Requirement 
1. Python 2.7 (or Anaconda2)
2. Stanford CoreNLP System, see download https://stanfordnlp.github.io/CoreNLP/index.html[6]
3. Pacakges: nltk, glob, sklearn, bs4, numpy, scipy

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


## Reference
[1] Nenkova, Ani and Rebecca J. Passonneau. Evaluating content selection in summarization: The Pyramid Method. Joint Annual Meeting of Human Language Technology and the North American chapter of the Association for Computational Linguistics (HLT/NAACL). Boston, MA. June, 2004.
[2] Nenkova, Ani, Rebecca J. Passonneau, and Kathleen McKeown. "The pyramid method: Incorporating human content selection variation in summarization evaluation." ACM Transactions on Speech and Language Processing (TSLP) 4.2 (2007): 4.
[3] Passonneau, Rebecca J. 2010. Formal and functional assessment of the pyramid method for summary content evaluation. Natural Language Engineering 16:107-131. Copyright Cambridge University Press.
[4] Passonneau, Rebecca J., et al. "Wise Crowd Content Assessment and Educational Rubrics." International Journal of Artificial Intelligence in Education (2016): 1-27.
[5] Yang, Qian, Rebecca J. Passonneau, and Gerard de Melo. "PEAK: Pyramid Evaluation via Automated Knowledge Extraction." AAAI. 2016.
[6] Manning, Christopher D., Mihai Surdeanu, John Bauer, Jenny Finkel, Steven J. Bethard, and David McClosky. 2014. The Stanford CoreNLP Natural Language Processing Toolkit In Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics: System Demonstrations, pp. 55-60.
