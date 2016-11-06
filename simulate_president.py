#!/usr/bin/env python
import pylab as pl
import numpy as np
import yaml
from scipy.io import loadmat
from collections import defaultdict
from progressbar import ProgressBar, Bar, ETA
from matplotlib.backends.backend_pdf import PdfPages
import time

from electoral_votes import VOTES
assert(sum(VOTES.values()) == 538)

DPI = 400
RED = (1.0, 0.36470588, 0.25)
BLUE = (0.09019608, 0.61960784, 0.87843137)

def simulate(states, cprobs, N):
    np.random.seed(1)
    evotes = [VOTES[s] for s in states]
    R = np.random.random_sample(size=(N, len(evotes)))
    E = np.dot((R < cprobs), evotes)
    return E

def get_called_states(called_file):
    if called_file is None: return {}
    with open(called_file, 'r') as f:
        d = yaml.load(f)
    d = dict((k, v) for k, v in d.items()
             if v in ('Clinton', 'Trump'))
    return d

def adjust_probs(called, states, cprobs, tprobs):
    for i, s in enumerate(states):
        if s in called:
            if called[s] == 'Clinton':
                cprobs[i] = 1.0
                tprobs[i] = 0.0
            else:
                cprobs[i] = 0.0
                tprobs[i] = 1.0
    return cprobs, tprobs

def main(model, outputfile, nsamples, plotthreshold, called, justreturnprobs=False):
    calls = get_called_states(called)
    mat = loadmat('model.mat')
    states = [str(s).strip() for s in mat['states']]
    candidates = [str(c).strip() for c in mat['candidates']]
    models = [str(m).strip() for m in mat['models']]
    clinton = candidates.index('Clinton')
    trump = candidates.index('Trump')
    midx = models.index(model)
    data = mat['model'][midx]

    data /= 100.
    cprobs = data[:, clinton]
    tprobs = data[:, trump]

    cprobs, tprobs = adjust_probs(calls, states, cprobs, tprobs)

    C = simulate(states, cprobs, nsamples)
    T = simulate(states, tprobs, nsamples)
    cprob = np.average(C >= 270)
    tprob = np.average(T >= 270)
    ptie = 1 - (cprob + tprob)
    cprob += 0.5*ptie
    tprob += 0.5*ptie
    if justreturnprobs: return cprob, tprob

    fig = pl.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.set_title('Presidency', fontsize=24)
    pdc, evc, _ = ax.hist(C, normed=True,
        histtype='step', color=BLUE, lw=2, bins=np.arange(0, 539))
    pdt, evt, _ = ax.hist(T, normed=True,
        histtype='step', color=RED, lw=2, bins=np.arange(0, 539))
    evc = evc[:-1]
    evt = evt[:-1]

    ymin, ymax = ax.get_ylim()
    ax.plot([270.5, 270.5], [ymin, ymax], 'k-', lw=3)

    # Determine nice plot bounds
    interesting = np.hstack([evc[pdc > plotthreshold],
                             evt[pdt > plotthreshold]])
    xmin = np.min(interesting) - 10
    xmax = np.max(interesting) + 10
    xmin = 160
    xmax = 380

    ax.text(xmin + 5, 0.9*ymax, 'Trump %.1f%%' % (100*tprob), ha='left', va='top', fontsize=20, color=RED)
    ax.text(xmax - 5, 0.9*ymax, 'Clinton %.1f%%' % (100*cprob), ha='right', va='top', fontsize=20, color=BLUE)

    ticks = set(range(170, 538, 20))
    ticks = np.array(sorted(ticks))
    ax.set_xticks(ticks + 0.5)
    ax.set_xticklabels([str(int(t)) for t in ticks])
    ax.set_xlim(xmin, xmax)

    ax.set_xlabel('Electoral Votes', fontsize=18)
    ax.set_ylabel('Probability Density', fontsize=18)

    if outputfile is not None:
        if outputfile == 'auto':
            outputfile = ('figs/president_%d.png' % int(time.time()))
        if outputfile.endswith('pdf'):
            pdf = PdfPages(outputfile)
            pdf.savefig(fig, bbox_inches='tight')
            pdf.close()
        else:
            fig.savefig(outputfile, dpi=DPI)
    else:
        pl.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument('-m', '--model',
                        choices=['now', 'plus', 'polls'], default='plus')
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('-n', '--nsamples', default=1000000, type=int)
    parser.add_argument('-t', '--plotthreshold', default=1e-4, type=float)
    parser.add_argument('-c', '--called', default='called.yaml')

    args = parser.parse_args()
    main(**vars(args))
