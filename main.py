# Imports
import sys
sys.path.append('./Workers')
from Workers import FileWriteWorker, DataAnalysisWorker, LIFFWorker

# # Running
# s = SongKickWorker()
# s.work(start='supplementMetadata', end='supplementMetadata')

l = LIFFWorker()
l.work(start='downloadHome', end='makeEventURLs')

# fW = FileWriteWorker()
# fW.work(start='importData', end='writeData')

# dAW = DataAnalysisWorker()
# dAW.work(start='importData', end='makeFigures')

# wW = WatchWorker()
# wW.work(start='importData', end='checkWatchlists')

# sW = ScopusWorker()
# sW.work(start='getRobsStats', end='getRobsStats')

# import requests
# import json

# resp = requests.get("http://api.elsevier.com/content/author?author_id=7004212771&view=metrics",
#                     headers={'Accept':'application/json',
#                              'X-ELS-APIKey': '7e059441b3fcd16c752c50b628747a01'})

# print(json.dumps(resp.json(),
#                  sort_keys=True,
#                  indent=4, separators=(',', ': ')))
