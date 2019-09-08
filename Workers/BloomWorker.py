# Class to get data from bloomberg
class BloomWorker():
    """
    A worker that gathers data from bloomberg regarding the parent companies of
    a collection of companies.
    """
    def __init__(self):
        super().__init__()

        self.product = 'companies'

        # Stages
        self.stageList = ['makeCompanyList', 'makeCompanyURLs', 
                            'downloadURLs', 'parsePages']
        self.stageDict = {'makeCompanyList': self.makeCompanyList,
                            'makeCompanyURLs': self.makeCompanyURLs,
                            'downloadURLs': self.downloadURLs,
                            'parsePages': self.parsePages}

        # Info
        self.baseURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds'
        self.queryURL = 'https://www.songkick.com/metro_areas/24495-uk-leeds?page={0}'
        self.RESULTS_PER_PAGE = 50

