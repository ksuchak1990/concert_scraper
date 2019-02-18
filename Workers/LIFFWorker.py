from WebWorker import WebWorker

class LIFFWorker(WebWorker):

    def __init__(self):
        super().__init__()

        self.product = 'films'

        # Stages
        self.stageList = ['downloadHome', 'parseHome', 'makeEventURLs',
                            'downloadEvents', 'parseEvents']

        self.stageDict = {'downloadHome': self.downloadHome,
                        'parseHome': self.parseHome,
                        'makeEventURLs': self.makeEventURLs,
                        'downloadEvents': self.downloadEvents,
                        'parseEvents': self.parseEvents}
        
        # Info
        self.homeURL = 'https://www.leedsfilmcity.com/film-festivals/leeds-international-film-festival/liff-2018-programme/?Date=All+Dates&Strand=&Country=&Venue=&SortOrder=0&PageSize=10000&Page=1#festival-filter-form'
        self.queryURL = 'https://www.leedsfilmcity.com{0}'

    # stage functions
    def downloadHome(self):
        return self.requestURL(self.homeURL)

    def parseHome(self, pageCode):
        codeSection = self.restrict(inputString=pageCode, startStr='<section id="film-listing" class="event-listing">', endStr='</section>')
        eventSections = codeSection.split('<div class="span4 event-item">')[1:]
        eventList = [self.restrict(inputString=x, startStr='a href=\"', endStr='\">') for x in eventSections]
        return list(set(eventList))
    
    def makeEventURLs(self, events):
        endings = set(events)
        return [self.queryURL.format(event) for event in endings]
    
    def downloadEvents(self, urls):
        return [self.requestURL(inputString=url) for url in urls]
    
    def parseEvents(self, events):
        return [self.parseEvent(event) for event in events]
    
    # Auxiliary functions
    def parseEvent(self, event):
        metadataList = ['length', 'rating', 'countries'
                        'director', 'title', 'venue',
                        'date', 'time']
        metadata = dict()
        
        filmInfo = self.restrict(inputString=event, startStr='<section class="film-details">', endStr=' ')


    
