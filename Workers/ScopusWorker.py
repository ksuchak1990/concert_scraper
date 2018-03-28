# Imports
import json
import requests
from Worker import Worker

# Class
class ScopusWorker(Worker):
    """a worker augmented with handy functions for web stuff"""
    def __init__(self):
        super().__init__()

        self.product = 'citations'

        # Stages
        self.stageList = ['getRobsStats']
        self.stageDict = {'getRobsStats': self.getRobsStats}

        # URLs
        self.baseURL = 'http://api.elsevier.com/content/author?author_id={}&view=metrics'

        # Headers
        self.headers = {'Accept': 'application/json',
                        'X-ELS-APIKey': '7e059441b3fcd16c752c50b628747a01'}

        # Author id
        self.robsID = '6602678643'

    def getRobsStats(self):
        r = requests.get(self.baseURL.format(self.robsID), headers=self.headers)
        output = r.json()
        print(output)
        return output
