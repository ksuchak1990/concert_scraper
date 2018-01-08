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
    """worker to grab the info from SongKick.com, process it, and output it.
    This involves:
        - Getting html from SongKick.com,
        - Parsing html,
        - Looking up artists on wikipedia,
        - Getting artist genres from the wikipedia pages where available."""
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
        """Make a list of the pages to request."""
        baseURLCode = self.requestURL(self.baseURL)

        # Calculate number of pages
        numberOfConcerts = self.restrict(inputString=baseURLCode, 
                                        startStr='upcoming-concerts-count"><b>', 
                                        endStr='</b>')
        numberOfPages = ceil(int(numberOfConcerts) / self.RESULTS_PER_PAGE)
        print('Catalogue is made up of {0} concerts over {1} pages'.format(numberOfConcerts, 
                numberOfPages))

        # For each page, get source
        queryURLList = [self.queryURL.format(str(i)) for i in range(1, numberOfPages)]
        return queryURLList


    def downloadCatalogue(self, queryURLList):
        """Download the html for each of the urls."""
        sourceCodeList = list()
        for i, queryURL in enumerate(queryURLList):
            print('getting page {0}'.format(i))
            sourceCode = self.requestURL(queryURL)
            sourceCodeList.append(sourceCode)
            sleep(0.5)

        return sourceCodeList

    def parseCatalogue(self, sourceCodeList):
        """For each source page, identify individual events."""
        eventsList = list()
        for page in sourceCodeList:
            events = self.restrict(inputString=page, 
                startStr='<div class="component events-summary" id="event-listings">', 
                endStr='<div class="pagination">')
            eventsCodeList = events.split('<script type="application/ld+json">')[1:]
            eventsJSONList = [self.restrict(x, endStr='</script>') for x in eventsCodeList]
            eventsList.extend(eventsJSONList)

        return eventsList

    def parseEvents(self, eventsList):
        """Parse each event to get the relevant event metadata."""
        eventsMetadataDict = dict()
        for event in eventsList:
            eventMetadata = self.getEventMetadata(event)
            eventID = eventMetadata['EventID']

            # If EventID already in dict, merge new entry with old, else add new
            if eventID in eventsMetadataDict:
                oldEventMetadata = eventsMetadataDict[eventID].copy()
                eventsMetadataDict[eventID] = self.consolidateEvents(eventMetadata, 
                                                        oldEventMetadata)
            else:
                eventsMetadataDict[eventID] = eventMetadata
        # Construct list of dicts from dict of dicts
        eventsMetadataList = [v for k, v in eventsMetadataDict.items()]

        return eventsMetadataList

    def supplementMetadata(self, eventsList):
        """For each eventDict:
            - Check if artist is on wikipedia - if yes:
                - Get html for wikipedia page,
                - Check if page holds artist genres - if yes:
                    - Get artist genres,
                    - Attach genres to eventDict."""
        outputList = list()
        artistSet = {event['Artist'] for event in eventsList}
        genreDict = dict()

        # Get wikipedia genres relating to each artist
        # Use set so we don't look up same artist multiple times
        for artist in artistSet:
            genreDict[artist] = self.getWikipediaGenres(artist)

        # Add genres to events
        for event in eventsList:
            supplementedEvent = event.copy()
            supplementedEvent['Genres'] = genreDict[event['Artist']]
            outputList.append(supplementedEvent)
        return outputList

    # Auxiliary event parsing functions
    def getEventMetadata(self, eventJSON):
        eventDict = json.loads(eventJSON)[0]
        event = {'Artist': self.getArtist(eventDict),
                    'Date': self.getDate(eventDict),
                    'Venue': self.getVenue(eventDict),
                    'Coordinates': self.getCoordinates(eventDict)}
        event['Support'] = self.getSupport(eventDict, event['Artist'])
        event['EventID'] = self.makeEventID(event)
        return event

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

    def getCoordinates(self, eventDict):
        locationDict = eventDict['location']
        if 'geo' in locationDict:
            return locationDict['geo']
        else:
            return dict()

    def makeEventID(self, event):
        artist = self.cleanUpArtist(event['Artist'])
        date = self.normalise(event['Date'])
        venue = self.normalise(event['Venue'])
        return '___'.join([date, venue, artist])

    def cleanUpArtist(self, artistString):
        artist = artistString.lower()
        # Dealing with 'and' vs '&''
        artist = artist.replace('&', 'and')

        # Dealing with leading 'the' (this can cause confusion)
        artist = self.prefixStrip(artist, 'the ')

        # Normalising
        artist = self.normalise(artist)

        return artist

    def consolidateEvents(self, newEvent, oldEvent):
        # As it stands, this function only consolidates the support artists,
        # But the aim is to leave it open to consolidating other metadata in the future.

        # Provide base event metadata
        outputKeys = ['EventID', 'Artist', 'Date', 'Venue', 'Coordinates']
        outputEvent = self.dictKeyFilter(oldEvent, outputKeys)
        # outputEvent = {'EventID': oldEvent['EventID'],
        #                 'Artist': oldEvent['Artist'],
        #                 'Date': oldEvent['Date'],
        #                 'Venue': oldEvent['Venue'],
        #                 'Coordinates': oldEvent['Coordinates']}

        # Get keys to be added
        keys = {key for key in oldEvent if key not in outputEvent}

        # For each of the remaining keys, make a set of values in each of the events
        for key in keys:
            values =  set()
            for event in [newEvent, oldEvent]:
                if isinstance(event[key], collections.Iterable):
                    for v in event[key]:
                        values.add(v)
            outputEvent[key] = list(values)

        return outputEvent

    # Auxiliary supplementary metadata functions
    def getWikipediaGenres(self, artist):
        # Handling errors in searching for artists on wikipedia
        try:
            page =  wiki.page(artist, auto_suggest=False).html()
        except wiki.exceptions.PageError:
            page = ''
            print('Unable to find wikipedia page for {0}'.format(artist))
        except wiki.exceptions.DisambiguationError:
            page = ''
            # Consider implementing a way to let the user choose here
            print('Multiple entries found for {0}, none chosen'.format(artist))

        # Search for genres in wikipedia html if page found
        genres = self.getGenre(page, artist) if page else None

        return genres

    def getGenre(self, page, artist):
        # Only split out the genres if there are genres to find
        if '<th scope="row">Genres</th>' not in page:
            print('No genres available for {0}'.format(artist))
            return None
        else:
            print('Collecting genres for {0}'.format(artist))
            genreSection = self.restrict(inputString=page, 
                                        startStr='<th scope="row">Genres</th>', 
                                        endStr='<tr>')
            genreCodeList = genreSection.split('</a>')
            genres = [self.restrict(inputString=x.lower(), startStr='title="', endStr='">') 
                        for x in genreCodeList if 'itle=' in x]
            return genres
