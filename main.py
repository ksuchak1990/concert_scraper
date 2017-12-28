# Imports
from SongKickWorker import SongKickWorker
from FileWriteWorker import FileWriteWorker

# Running
# s = SongKickWorker()
# s.work(start='makeCatalogue', end='supplementMetadata')

fw = FileWriteWorker()
fw.work(start='importData', end='writeData')
