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
<link rel="apple-touch-icon" sizes="57x57" href="/apple-icon-57x57.png">
<link rel="apple-touch-icon" sizes="60x60" href="/apple-icon-60x60.png">
<link rel="apple-touch-icon" sizes="72x72" href="/apple-icon-72x72.png">
<link rel="apple-touch-icon" sizes="76x76" href="/apple-icon-76x76.png">
<link rel="apple-touch-icon" sizes="114x114" href="/apple-icon-114x114.png">
<link rel="apple-touch-icon" sizes="120x120" href="/apple-icon-120x120.png">
<link rel="apple-touch-icon" sizes="144x144" href="/apple-icon-144x144.png">
<link rel="apple-touch-icon" sizes="152x152" href="/apple-icon-152x152.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-icon-180x180.png">
<link rel="icon" type="image/png" sizes="192x192"  href="/android-icon-192x192.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/manifest.json">
<meta name="msapplication-TileColor" content="#ffffff">
<meta name="msapplication-TileImage" content="/ms-icon-144x144.png">
<meta name="theme-color" content="#ffffff">
</head>
<body>
<div class=imagecontainer>
<img src="figs/president_%d.png">
</div>
<br \>
<img src="figs/senate_%d.png">
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-86893562-1', 'auto');
  ga('send', 'pageview');

</script>
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
