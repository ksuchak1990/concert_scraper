# Imports
import requests
from Worker import Worker

# Class
class WebWorker(Worker):
    """a worker augmented with handy functions for web stuff"""
    def __init__(self):
        super().__init__()

    ## Web functions
    def requestURL(self, inputString):
        if not isinstance(inputString, str):
            raise TypeError('inputString must be a string') 
        r = requests.get(url=inputString)
        if r.status_code != 200:
            raise Exception('Page request unsuccessful: status code {0}'.format(r.status_code))
        return(r.text)

    ## Text functions
    def restrict(self, inputString, startStr=None, endStr=None):
        if not isinstance(inputString, str):
            raise TypeError('inputString must be a string')

        startIndex = inputString.index(startStr) + len(startStr) if startStr else 0
        reducedStr = inputString[startIndex:]
        endIndex = reducedStr.index(endStr) if endStr else len(reducedStr)
        return(reducedStr[:endIndex])
