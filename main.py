import json
import os
import requests
from math import ceil
from time import sleep

# Classes
class Worker():
    """class representing the generic worker, for which more specific workers inherit"""
    def __init__(self):
        self.product = 'generic'

        self.stageList = list()
        self.stageDict = dict()

        self.baseDir = 'output'

    def work(self):
        self.initialChecks()

        print(self.stageList)

        for i, stage in enumerate(self.stageList):
            if i != 0:
                inputData = self.pickUp('{0}/{1}/{2}.json'.format(self.baseDir, self.product, self.stageList[i-1]))
                outputData = self.stageDict[stage](inputData)
                self.putDown(outputData, '{0}/{1}/{2}.json'.format(self.baseDir, self.product, stage))
            else:
                outputData = self.stageDict[stage]()
                self.putDown(outputData, '{0}/{1}/{2}.json'.format(self.baseDir, self.product, stage))

    # ensure that relevant output directories exist
    def initialChecks(self):
        outputPath = './{0}/{1}'.format(self.baseDir, self.product) if self.product != 'generic' else self.baseDir
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

    # get data from previous stage
    def pickUp(self, path):
        with open(path) as infile:
            item = json.load(infile)
        return item

    # output data at end of stage
    def putDown(self, item, path):
        with open(path, 'w') as outfile:
            json.dump(item, outfile)

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
            ## Don't think that this should be a StandardError, I'll need to find something more appropriate
            raise Exception('Page request unsuccessful: status code {0}'.format(r.status_code))
        return(r.text)

    ## Text functions
    def restrict(self, inputString, startStr=None, endStr=None):
        if not isinstance(inputString, str):
            raise TypeError('inputString must be a string')

        startIndex = inputString.index(startStr) + len(startStr) if startStr else 0
        endIndex = inputString.index(endStr) if endStr else len(inputString)
        return(inputString[startIndex:endIndex])

class SongKickWorker(WebWorker):
    """worker to grab the CDRC info, process it, and output it"""
    def __init__(self):
        super().__init__()

        self.product = 'concerts'

        # Stages
        self.stageList = ['makeCatalogue', 'downloadCatalogue', 'parseCatalogue', 'parseEvents']
        self.stageDict = {'makeCatalogue': self.makeCatalogue, 
                            'downloadCatalogue': self.downloadCatalogue,
                            'parseCatalogue': self.parseCatalogue,
                            'parseEvents': self.parseEvents}

        # Info
        self.baseURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds'
        self.queryURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds?page={0}'
        self.RESULTS_PER_PAGE = 50

    def makeCatalogue(self):
        baseURLCode = self.requestURL(self.baseURL)

        # Calculate number of pages
        numberOfConcerts = self.restrict(inputString=baseURLCode, startStr='upcoming-concerts-count"><b>', endStr='</b>')
        numberOfPages = ceil(int(numberOfConcerts) / self.RESULTS_PER_PAGE)

        # For each page, get source
        queryURLList = [self.queryURL.format(str(i)) for i in range(1, numberOfPages)]
        return queryURLList


    def downloadCatalogue(self, queryURLList):
        sourceCodeList = list()
        for i, queryURL in enumerate(queryURLList):
            print('getting page {0}'.format(i))
            sourceCode = self.requestURL(queryURL)
            sourceCodeList.append(sourceCode)
            sleep(0.5)

        # print('Listings contain {0} concerts over {1} pages'.format(numberOfConcerts, len(sourceCodeList)))

        return sourceCodeList

    def parseCatalogue(self, sourceCodeList):
        # For each source page, identify individual events
        eventsList = list()
        for page in sourceCodeList:
            events = self.restrict(inputString=page, startStr='<div class="component events-summary" id="event-listings">', endStr='<div class="pagination">')
            eventsCodeList = events.split('<script type="application/ld+json">')[1:]
            eventsJSONList = [self.restrict(x, endStr='</script>') for x in eventsCodeList]
            eventsList.extend(eventsJSONList)

        return eventsList

    # Auxilliary parsing functions
    def getArtist(self, eventDict):
        return eventDict['name']

    def getSupport(self, eventDict, headliner):
        artists = eventDict['performer']
        support = [d['name'] for d in artists if d['name'] != headliner] if len(artists) > 1 else ''
        return support

    def getDate(self, eventDict):
        dateTime = eventDict['startDate']
        date = self.restrict(dateTime, endStr='T') if 'T' in dateTime else dateTime
        return date

    def getVenue(self, eventDict):
        return eventDict['location']['name']

    def getEventMetadata(self, eventJSON):
        eventDict = json.loads(eventJSON)[0]
        event = {'Artist': self.getArtist(eventDict),
                    'Date': self.getDate(eventDict),
                    'Venue': self.getVenue(eventDict)}
        event['Support'] = self.getSupport(eventDict, event['Artist'])
        return event

    def parseEvents(self, eventsList):
        eventsMetaDataList = list()
        for event in eventsList:
            eventMetadata = self.getEventMetadata(event)
            eventsMetaDataList.append(eventMetadata)
        return eventsMetaDataList

s = SongKickWorker()
s.work()