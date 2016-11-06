#!/usr/bin/env python
import os
from glob import glob

TEMPLATE = r"""
<html>
<head>
<title>Na&iuml;veThirtyEight</title>
<style>
  .imagecontainer {
    position: relative;
    left: 0;
    right: 0;
    margin: 0;
  }
  img {
    max-width: 100%%;
    max-height: 100%%;
    display: block;
  }
</style>
</head>
<body>
<div class=imagecontainer>
<img src="figs/president_%d.png">
</div>
<br \>
<img src="figs/senate_%d.png">
</body>
</html>
"""

def latest(flist):
    return max([int(os.path.basename(f).split('_')[-1].split('.')[0])
                for f in flist])

def main():
    pfiles = glob(os.path.join('figs', 'president*.png'))
    sfiles = glob(os.path.join('figs', 'senate*.png'))
    platest = latest(pfiles)
    slatest = latest(sfiles)
    with open('index.html', 'w+') as f:
        f.write(TEMPLATE % (platest, slatest))

if __name__ == '__main__':
    main()
