# Imports
import pandas as pd
from datetime import datetime as dt
from Worker import Worker
import matplotlib.pyplot as plt

# Class
class DataAnalysisWorker(Worker):
    def __init__(self):
        super().__init__()

        self.product = 'visualisations'

        # Stages
        self.stageList = ['importData', 'makeFigures']
        self.stageDict = {'importData': self.importData,
                            'makeFigures': self.makeFigures}

        # Paths
        self.eventPath = './output/concerts/supplementMetadata.json'

    def importData(self):
        eventList = self.pickUp(self.eventPath)
        return eventList

    def makeFigures(self, eventList):
        # Make dataframe
        df = pd.DataFrame(eventList)

        for index, row in df.iterrows():
            row['Date'] = dt.date(pd.to_datetime(row['Date']))

        # df['Date'] = pd.to_datetime(df['Date'])

        # Produce plots
        self.plotDates(df)
        self.plotVenues(df)

        return 'See figures.'

    def plotDates(self, data, numberOfDays=60):
        # Transform data
        rawData = data.groupby('Date').count()
        restrictedData = rawData[:numberOfDays]

        # Create bar colours
        colours = list()
        count = 0
        for index, row in restrictedData.iterrows():
            colour = 'darkred' if row['EventID'] > 6 else 'navy'
            count += row['EventID']
            colours.append(colour)

        # Plot
        restrictedData.EventID.plot.bar(color=colours)
        plt.suptitle('Number of concerts over the next {0} days'.format(numberOfDays))
        plt.title('Total number of concerts: {0}'.format(count))
        plt.tight_layout()
        plt.show()

    def plotVenues(self, data, numberOfVenues=10):
        # Transform data
        m = data.Venue.value_counts()[:numberOfVenues]

        # Plot
        m.plot.bar()
        plt.title('Number of concerts at each of the top {0} venues'.format(numberOfVenues))
        plt.tight_layout()
        plt.show()

