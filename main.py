"""
Main python script to run concert scraper.
"""

# Imports
import sys
sys.path.append('./Workers')
from Workers import FileWriteWorker, DataAnalysisWorker, LIFFWorker, SongKickWorker

# Running
s = SongKickWorker()
s.work(start='makeCatalogue', end='supplementMetadata')

# l = LIFFWorker()
# l.work(start='parseEvents', end='parseEvents')

fW = FileWriteWorker()
fW.work(start='importData', end='writeData')

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
