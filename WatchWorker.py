# Imports
from Worker import Worker

# Class
class WatchWorker(Worker):
    """Worker to maintain a watchlist of artists and genres,
    and alert the user when appropriate concerts arise."""
    def __init__(self):
        super().__init__()

        self.product = 'your_events'

        # Stages
        self.stageList = ['importData']
        self.stageDict = {'importData': self.importData}

        # Paths
        self.eventPath = './output/concerts/supplementMetadata.json'

    def importData(self):
        """Getting data that has been produced by the SongKickWorker.
        :returns: list of event metadata dictionaries"""
        eventList = self.pickUp(self.eventPath)
        return eventList
