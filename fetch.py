#!/usr/bin/env python
import numpy as np
from scipy.io import savemat
import re
import json
from HTMLParser import HTMLParser
import requests
from collections import defaultdict

URL = 'http://projects.fivethirtyeight.com/2016-election-forecast/'
RE = r'race\.(\w+)\s*=\s*([^;]*);'

class FiveThirtyEightHTMLParser(HTMLParser):

    def __init__(self):
        self.scripts = []
        self.state = None
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.state = 'script'

    def handle_endtag(self, tag):
        if self.state == 'script':
            self.state = None

    def handle_data(self, data):
        if self.state == 'script':
            self.scripts.append(data)

def get_data():
    response = requests.get(URL)
    parser = FiveThirtyEightHTMLParser()
    parser.feed(response.text)
    race = {}
    for script in parser.scripts:
        matches = re.findall(RE, script)
        for k, v in matches:
            race[k] = json.loads(v)

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    states = set()
    candidates = set()
    models = set()

    for i in race['summary']:
        state = i['state']
        if state == 'US': continue
        states.add(state)
        for ldict in i['latest'].values():
            candidate = ldict['candidate']
            candidates.add(candidate)
            for model, mdict in ldict['models'].items():
                models.add(model)
                data[model][state][candidate] = mdict['winprob']

    states, candidates, models = map(sorted, (states, candidates, models))

    data = np.array(
        [
            [
                [data[model][state][cand] for cand in candidates]
                for state in states
            ]
            for model in models
        ]
    )
    savemat('model.mat', {'model': data, 'states': states, 'candidates': candidates, 'models': models})

def main():
    get_data()

if __name__ == '__main__':
    main()
