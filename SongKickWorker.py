# Imports
import collections
import genres
import json
import wikipedia as wiki
from math import ceil
from time import sleep
from WebWorker import WebWorker

#Class
class SongKickWorker(WebWorker):
    """worker to grab the info from SongKick, process it, and output it.
    This can involve looking up artists on wikipedia to get their genres,"""
    def __init__(self):
        super().__init__()

        self.product = 'concerts'

        # Stages
        self.stageList = ['makeCatalogue', 'downloadCatalogue', 
                            'parseCatalogue', 'parseEvents', 
                            'supplementMetadata']
        self.stageDict = {'makeCatalogue': self.makeCatalogue, 
                            'downloadCatalogue': self.downloadCatalogue,
                            'parseCatalogue': self.parseCatalogue,
                            'parseEvents': self.parseEvents,
                            'supplementMetadata': self.supplementMetadata}

        # Info
        self.baseURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds'
        self.queryURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds?page={0}'
        self.RESULTS_PER_PAGE = 50

    # Stage functions
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

    def parseEvents(self, eventsList):
        eventsMetadataDict = dict()
        for event in eventsList:
            eventMetadata = self.getEventMetadata(event)
            eventID = eventMetadata['EventID']
            # If EventID already in dict, merge new entry with old, else add new
            if eventID in eventsMetadataDict:
                oldEventMetadata = eventsMetadataDict[eventID].copy()
                eventsMetadataDict[eventID] = self.consolidateEvents(eventMetadata, oldEventMetadata)
            else:
                eventsMetadataDict[eventID] = eventMetadata
        # Construct list of dicts from dict of dicts
        eventsMetadataList = [v for k, v in eventsMetadataDict.items()]

        for event in eventsMetadataList:
            if not isinstance(event, dict):
                raise TypeError('event is of type {}'.format(type(event)))
        return eventsMetadataList

    def supplementMetadata(self, eventsList):
        outputList = list()
        for event in eventsList:
            supplementedEvent = self.addWikipediaGenres(event)
            outputList.append(supplementedEvent)
        return outputList

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

    def makeEventID(self, event):
        artist = self.cleanUpArtist(event['Artist'])
        date = self.normalise(event['Date'])
        venue = self.normalise(event['Venue'])
        return '___'.join([date, venue, artist])

    def cleanUpArtist(self, artistString):
        artist = artistString.lower()
        # Dealing with 'and' vs '&''
        artist = artist.replace('&', 'and')

        # Dealing with leading 'the'
        artist = self.prefixStrip(artist, 'the ')

        # Normalising
        artist = self.normalise(artist)

        if artist != artistString:
            print(artistString, artist)

        return artist

    def getEventMetadata(self, eventJSON):
        eventDict = json.loads(eventJSON)[0]
        event = {'Artist': self.getArtist(eventDict),
                    'Date': self.getDate(eventDict),
                    'Venue': self.getVenue(eventDict)}
        event['Support'] = self.getSupport(eventDict, event['Artist'])
        event['EventID'] = self.makeEventID(event)
        return event

    def consolidateEvents(self, newEvent, oldEvent):
        # As it stands, this function only consolidates the supports,
        # But the aim is to leave it open to consolidating other metadata in the future

        # provide base event metadata
        outputEvent = {'EventID': oldEvent['EventID'],
                        'Artist': oldEvent['Artist'],
                        'Date': oldEvent['Date'],
                        'Venue': oldEvent['Venue']}

        # get keys to be added
        keys = {key for key in oldEvent if key not in outputEvent}

        for key in keys:
            values =  set()
            for event in [newEvent, oldEvent]:
                if isinstance(event[key], collections.Iterable):
                    for v in event[key]:
                        values.add(v)
            outputEvent[key] = list(values)

        return outputEvent

    def addWikipediaGenres(self, event):
        print(event)
        d = event.copy()
        try:
            page =  wiki.page(d['Artist'], auto_suggest=False).html()
        except:
            page = ''
            print('unable to find wikipedia page for {0}'.format(d['Artist']))
        if len(page) != 0:
            d['Genres'] = self.getGenre(page, d['Artist'])
        return d

    def getGenre(self, page, artist):
        if '<th scope="row">Genres</th>' not in page:
            print('No genres available for {0}'.format(artist))
            return None
        else:
            print('running {0}'.format(artist))
            genreSection = self.restrict(inputString=page, startStr='<th scope="row">Genres</th>', endStr='<tr>')
            genreCodeList = genreSection.split('</a>')
            genres = [self.restrict(inputString=x.lower(), startStr='title="', endStr='">') for x in genreCodeList if 'itle=' in x]
            return genres

