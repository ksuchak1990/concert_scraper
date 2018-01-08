# Imports
import csv
from Worker import Worker

# Class
class FileWriteWorker(Worker):
    """worker to get the data that SongKickWorker has produced, sort it, 
    and write it in a nice csv """
    def __init__(self):
        super().__init__()

        self.product = 'output_files'

        # Stages
        self.stageList = ['importData', 'organiseData', 'writeData']
        self.stageDict = {'importData': self.importData,
                            'organiseData': self.organiseData,
                            'writeData': self.writeData}

        # Paths
        self.eventPath = './output/concerts/supplementMetadata.json'
        self.outputPath = './output/output_files/data.csv'

        self.headers = ['Date', 'Venue', 'Artist', 'Genres', 'Support']

    def importData(self):
        """Getting data that has been produced by the SongKickWorker."""
        eventList = self.pickUp(self.eventPath)
        return eventList

    def organiseData(self, eventList):
        """Sorting the entries by the EventID, which acts as a proxy for
        sorting by date, then venue, then artist."""
        sortedList = sorted(eventList, key=lambda d: d['EventID'])

        # Filter down the event keys to those required
        outputList = list()
        for event in eventList:
            outputList.append(self.dictKeyFilter(event, self.headers))
        return outputList

    def writeData(self, sortedList):
        """Write list of dicts to csv output file."""
        with open(self.outputPath, 'w') as outfile:
            dataWriter = csv.DictWriter(outfile, fieldnames=self.headers)
            dataWriter.writeheader()
            dataWriter.writerows(sortedList)
