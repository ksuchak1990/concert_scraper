# Imports
from SongKickWorker import SongKickWorker
from math import ceil
from time import sleep


# class GoogleSheetsWorker(Worker):
#     def __init__(self):
#         super().__init__()

#         self.product = 'none'

#         # Stages
#         self.stageList = ['readData', 'processData', 'writeData']
#         self.stageDict = {'readData': self.readData,
#                             'processData': self.readData,
#                             'writeData': self.writeData}

#     def readData(self):
#         pass

#     def processData(self, data):
#         pass

#     def writeData(self, data):
#         pass

# Running
s = SongKickWorker()
s.work()

# g = GoogleSheetsWorker()
# g.work()