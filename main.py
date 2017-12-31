# Imports
from SongKickWorker import SongKickWorker
from FileWriteWorker import FileWriteWorker
from DataAnalysisWorker import DataAnalysisWorker

# Running
# s = SongKickWorker()
# s.work(start='makeCatalogue', end='supplementMetadata')

# fW = FileWriteWorker()
# fW.work(start='importData', end='writeData')

dAW = DataAnalysisWorker()
dAW.work(start='importData', end='makeFigures')