# Imports
from SongKickWorker import SongKickWorker
from GoogleSheetsWorker import GoogleSheetsWorker

# Running
s = SongKickWorker()
s.work(start='makeCatalogue', end='supplementMetadata')

# g = GoogleSheetsWorker()
# g.work()