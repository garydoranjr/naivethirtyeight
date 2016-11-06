#!/usr/bin/env python
import pylab as pl
import numpy as np
import yaml
from scipy.io import loadmat
from collections import defaultdict
from progressbar import ProgressBar, Bar, ETA
from matplotlib.backends.backend_pdf import PdfPages
import time

from simulate_president import main as presidential, RED, BLUE, DPI

def simulate(states, probs, N):
    np.random.seed(1)
    evotes = [1.0 for s in states]
    R = np.random.random_sample(size=(N, len(evotes)))
    E = np.dot((R < probs), evotes)
    return E

def get_called_states(called_file):
    if called_file is None: return {}
    with open(called_file, 'r') as f:
        d = yaml.load(f)
    d = dict((k, v) for k, v in d.items()
             if v in ('D', 'R'))
    return d

def adjust_probs(called, states, dprobs, rprobs):
    for i, s in enumerate(states):
        if s in called:
            if called[s] == 'D':
                dprobs[i] = 1.0
                rprobs[i] = 0.0
            else:
                dprobs[i] = 0.0
                rprobs[i] = 1.0
    return dprobs, rprobs

def main(model, outputfile, nsamples, plotthreshold, called):
    calls = get_called_states(called)
    mat = loadmat('senate_model.mat')
    states = [str(s).strip() for s in mat['states']]
    candidates = [str(c).strip() for c in mat['candidates']]
    models = [str(m).strip() for m in mat['models']]
    democrats = candidates.index('D')
    republicans = candidates.index('R')
    midx = models.index(model)
    data = mat['model'][midx]

    data /= 100.
    dprobs = data[:, democrats]
    rprobs = data[:, republicans]

    dprobs, rprobs = adjust_probs(calls, states, dprobs, rprobs)

    C = simulate(states, dprobs, nsamples) + 36
    T = simulate(states, rprobs, nsamples) + 30
    dprob = np.average(C > 50)
    rprob = np.average(T > 50)
    ttie = (np.average(C == 50) + np.average(T == 50)) / 2.0
    cprob, tprob = presidential(model, None, nsamples, None, 'called.yaml', True)
    dprob += ttie*cprob
    rprob += ttie*tprob

    fig = pl.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.set_title('Senate', fontsize=24)
    pdc, evc, _ = ax.hist(C, normed=True,
        histtype='step', color=BLUE, lw=2, bins=np.arange(0, 101))
    pdt, evt, _ = ax.hist(T, normed=True,
        histtype='step', color=RED, lw=2, bins=np.arange(0, 101))
    evc = evc[:-1]
    evt = evt[:-1]

    ymin, ymax = ax.get_ylim()
    ax.plot([50.5, 50.5], [ymin, ymax], 'k-', lw=3)

    # Determine nice plot bounds
    interesting = np.hstack([evc[pdc > plotthreshold],
                             evt[pdt > plotthreshold]])
    xmin = np.min(interesting) - 1
    xmax = np.max(interesting) + 1
    xmin = 45
    xmax = 56

    ax.text(xmin + 0.5, 0.9*ymax, 'Republicans %.1f%%' % (100*rprob), ha='left', va='top', fontsize=20, color=RED)
    ax.text(xmax - 0.5, 0.9*ymax, 'Democrats %.1f%%' % (100*dprob), ha='right', va='top', fontsize=20, color=BLUE)

    ticks = set(range(0, 101, 2))
    ticks.add(100)
    ticks = np.array(sorted(ticks))
    ax.set_xticks(ticks + 0.5)
    ax.set_xticklabels([str(int(t)) for t in ticks])
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_xlabel('Seats', fontsize=18)
    ax.set_ylabel('Probability Density', fontsize=18)

    if outputfile is not None:
        if outputfile == 'auto':
            outputfile = ('figs/senate_%d.png' % int(time.time()))
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
    parser.add_argument('-c', '--called', default='called_senate.yaml')

    args = parser.parse_args()
    main(**vars(args))
