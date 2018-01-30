""" Python Implementation of test_ormf.m """
import scipy.io as sio
from scipy.sparse import coo_matrix, find
from numpy import loadtxt
import numpy as np

def getVectorization(DATA, MODEL):
    FILE = open(DATA, 'r')
    LINES = FILE.readlines()

    M_VARS = sio.whosmat(MODEL)
    SIZE = list(M_VARS[5][1])
    DIM = SIZE[0]
    N_WORDS = SIZE[1]
    MODEL = sio.loadmat(MODEL)
    P = MODEL['P']
    W_M = MODEL['w_m'].tolist()[0]
    LAM = MODEL['lambda'].tolist()[0]
    N_ITERS = MODEL['n_iters'].tolist()[0]

    if len(LINES) != 0:
        STUFF = loadtxt(DATA)
        ROWS = STUFF[:, 0].astype(int)
        HEIGHT = ROWS.max()
        COLS = STUFF[:, 1].astype(int)
        LENGTH = COLS.max()
        VALS = STUFF[:, 2]
        DATA = coo_matrix((VALS, (ROWS, COLS)), shape=(HEIGHT + 1, LENGTH + 1)).tocsc()
        N_DOCS = DATA.shape[1]
        V = np.zeros((DIM, N_DOCS))
    else:
        N_DOCS = 0
        V = np.zeros((DIM, 0))

    PPTW = P.dot(P.transpose())
    PPTW = PPTW*W_M[0]

    T = find(DATA)
    A = T[0].tolist()
    B = T[1].tolist()
    C = T[2].tolist()
    TEMP = []
    B = [(i - 1) for i in B]
    for i in B:
        if i not in TEMP:
            TEMP.append(i)
    #print 'TEMP',len(TEMP)
    NONZERO = [[] for i in range(len(TEMP))]
    for n, i in enumerate(B):
        NONZERO[i].append([A[n], C[n]])

    for p, lil_zero in enumerate(NONZERO):
        cols = []
        vals = []
        for j in lil_zero:
            cols.append(j[0])
            vals.append(j[1])
        cols = [(i - 1) for i in cols]
        pv = P[:, cols]
        vals = np.array(vals)
        pv_dot = np.matmul(pv, pv.transpose())*(1-W_M[0])
        lam_identity = np.identity(SIZE[0])*LAM
        num = PPTW + pv_dot + lam_identity
        den = (np.matmul(pv, vals))
        if (p == 1):
        	print num[10,:]
        	print den
        V[:,p] = np.linalg.lstsq(num, den)[0]
    print V

 
    ret = []
    for p, lil in enumerate(NONZERO):
        vect = []
        for k in range(DIM):
            vect.append(V[k,p])
        ret.append(vect)
    return ret
        
    
