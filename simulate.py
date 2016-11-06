#!/usr/bin/env python
import numpy as np
from scipy.io import loadmat
from collections import defaultdict
from progressbar import ProgressBar, Bar, ETA

from electoral_votes import VOTES
assert(sum(VOTES.values()) == 538)

def simulate_once(states, model):
    votes = defaultdict(int)
    for s, m in zip(states, model):
        idx = np.random.choice(len(m), size=1, replace=False, p=m)[0]
        votes[idx] += VOTES[s]
    return np.array([votes[i] for i in range(len(m))])

def simulate(states, model, N=100000):
    np.random.seed(1)
    winners = defaultdict(int)
    progress = ProgressBar(widgets=['Simulating: ', Bar('='), ' ', ETA()])
    for i in progress(range(N)):
        votes = simulate_once(states, model)
        if np.max(votes) < 270:
            continue
        winners[np.argmax(votes)] += 1
    return np.array([winners[i] for i in range(model.shape[1])]) / float(N)

def main():
    mat = loadmat('model.mat')
    states = [str(s).strip() for s in mat['states']]
    candidates = [str(c).strip() for c in mat['candidates']]
    for mname, data in zip(mat['models'], mat['model']):
        print mname.strip()
        print simulate(states, data / 100.)

if __name__ == '__main__':
    main()
