# Imports
import csv
import os
from Worker import Worker

# Class
class WatchWorker(Worker):
    """Worker to maintain a watchlist of artists and genres,
    and alert the user when appropriate concerts arise."""
    def __init__(self):
        super().__init__()

        self.product = 'your_events'

        # Stages
        self.stageList = ['importData',
                            'getEventsByGenre']
        self.stageDict = {'importData': self.importData,
                            'getEventsByGenre': self.getEventsByGenre}

        # Paths
        self.eventPath = './output/concerts/supplementMetadata.json'
        self.inputPath = './input/{0}_list.txt'
        self.watchlistPaths = {'artists': self.inputPath.format('artist'),
                            'genres': self.inputPath.format('genre')}

        self.watchlists = self.readWatchlists()

    # Stage methods
    def importData(self):
        """Getting data that has been produced by the SongKickWorker.
        :returns: list of event metadata dictionaries"""
        eventList = self.pickUp(self.eventPath)
        return eventList

    def getEventsByGenre(self, eventList):
        genreDict = dict()
        eventDict = {event['EventID']: event for event in eventList}
        for genre in self.watchlists['genres']:
            eventSet = set()
            for event in eventList:                
                if isinstance(event['Genres'], list):
                    for eventGenre in event['Genres']:
                        if genre in eventGenre:
                            eventSet.add(event['EventID'])
            genreList = [event for key, event in eventDict.items() if key in eventSet]
            genreDict[genre] = genreList
        return genreDict

    # Auxiliary methods
    def readWatchlists(self):
        watchlists = dict()
        for k, v in self.watchlistPaths.items():
            watchlists[k] = self.read(v)
        return watchlists

    def read(self, path):
        if not os.path.exists(path):
            raise OSError('File path {0} does not exist - please sort it out.'.format(path))
        watchSet = set()
        with open(path) as infile:
            watchlistReader = csv.reader(infile)
            for row in watchlistReader:
                for item in row:
                    watchSet.add(item)
        return watchSet

