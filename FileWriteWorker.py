# Imports
import csv
from Worker import Worker

# Class
class FileWriteWorker(Worker):
    """worker to get the data that SongKickWorker has produced, sort it, and write it in a nice csv """
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
        eventList = self.pickUp(self.eventPath)
        return eventList

    def organiseData(self, eventList):
        sortedList = sorted(eventList, key=lambda d: d['EventID'])
        outputList = list()
        for event in eventList:
            outputList.append(self.dictKeyFilter(event, self.headers))
        return outputList

    def writeData(self, sortedList):
        with open(self.outputPath, 'w') as outfile:
            dataWriter = csv.DictWriter(outfile, fieldnames=self.headers)
            dataWriter.writeheader()
            dataWriter.writerows(sortedList)

