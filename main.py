# Imports
import sys
sys.path.append('./Workers')
from Workers import SongKickWorker, FileWriteWorker, DataAnalysisWorker

# Running
s = SongKickWorker()
s.work(start='makeCatalogue', end='supplementMetadata')

fW = FileWriteWorker()
fW.work(start='importData', end='writeData')

dAW = DataAnalysisWorker()
dAW.work(start='importData', end='makeFigures')
