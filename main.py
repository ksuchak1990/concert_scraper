import requests
import json
from math import ceil
from time import sleep

baseURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds'
queryURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds?page={0}'
RESULTS_PER_PAGE = 50

# Web worker functions from training_courses project
# (probably rebuild this using those workers)
def requestURL(inputString):
    if not isinstance(inputString, str):
        raise TypeError('inputString must be a string')
    r = requests.get(url=inputString)
    if r.status_code != 200:
        # Don't think that this should be a StandardError
        # I'll need to find something more appropriate
        e = 'Page request unsuccessful: status code {0}'.format(r.status_code)
        raise RuntimeError(e)
    return(r.text)

# Text functions
def restrict(inputString, start=None, end=None):
    # Error cases:
    # Ensure that inputString is string
    if not isinstance(inputString, str):
        raise TypeError('inputString must be a string')

    # If start given then find start, else default to beginning
    c0 = inputString.index(start) + len(start) if start else 0

    # If end given then find end, else default to end
    c1 = inputString.index(end) if end else len(inputString)

    # Return text between start and end
    return(inputString[c0:c1])


# Get base page
baseURLCode = requestURL(baseURL)

# Calculate number of pages
numberOfConcerts = restrict(inputString=baseURLCode, start='upcoming-concerts-count"><b>', end='</b>')
numberOfPages = ceil(int(numberOfConcerts) / RESULTS_PER_PAGE)

# For each page, get source
sourceCodeList = list()
for i in range(1, numberOfPages+1):
    print('getting page {0}'.format(i))
    sourceCode = requestURL(queryURL.format(str(i)))
    sourceCodeList.append(sourceCode)
    sleep(0.5)

print('Listings contain {0} concerts over {1} pages'.format(numberOfConcerts, len(sourceCodeList)))

# For each source page, identify individual events
eventsList = list()
for page in sourceCodeList:
    events = restrict(inputString=page, start='<div class="component events-summary" id="event-listings">', end='<div class="pagination">')
    eventsCodeList = events.split('<script type="application/ld+json">')[1:]
    eventsJSONList = [restrict(x, end='</script>') for x in eventsCodeList]
    eventsList.extend(eventsJSONList)

# Parsing functions
def getArtist(eventDict):
    return eventDict['name']

def getSupport(eventDict, headliner):
    artists = eventDict['performer']
    support = [d['name'] for d in artists if d['name'] != headliner] if len(artists) > 1 else ''
    return support

def getDate(eventDict):
    dateTime = eventDict['startDate']
    date = restrict(dateTime, end='T') if 'T' in dateTime else dateTime
    return date

def getVenue(eventDict):
    return eventDict['location']['name']

def getEventMetadata(eventJSON):
    eventDict = json.loads(eventJSON)[0]
    event = {'Artist': getArtist(eventDict),
                'Date': getDate(eventDict),
                'Venue': getVenue(eventDict)}
    event['Support'] = getSupport(eventDict, event['Artist'])
    return event

# Parse events
eventsMetaDataList = list()
for event in eventsList:
    eventMetadata = getEventMetadata(event)
    eventsMetaDataList.append(eventMetadata)
