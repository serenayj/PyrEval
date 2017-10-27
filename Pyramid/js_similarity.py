import numpy as np 
import scipy.stats 

def KLD(vec1,vec2):
	vec1 = np.array([vec1])
	vec1.reshape((-1,1))
	vec2 = np.array([vec2])
	vec2.reshape((-1,1))
	t1 = scipy.stats.norm(vec1.mean(), vec1.std())
	t2 = scipy.stats.norm(vec2.mean(), vec2.std())
	klab = scipy.stats.entropy(t1.pdf(vec1)[0], t2.pdf(vec2)[0])
	klba = scipy.stats.entropy(t2.pdf(vec2)[0], t1.pdf(vec1)[0]) 
	return klab, klba 

def JSD(kl1,kl2):
	return 0.5*kl1 + 0.5*kl2 

def cos(v1,v2):
	kl12,kl21 = KLD(v1,v2)
	# Since divergence is telling you how diverged are two ideas, the bigger number you get, the more divergence it indicates  
	sc = 1/JSD(kl12,kl21)
	return sc 

