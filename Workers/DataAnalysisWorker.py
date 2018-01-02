# Imports
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
from Worker import Worker

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
        self.figPath = './output/visualisations/{0}.png'

    def importData(self):
        """Getting data that has been produced by the SongKickWorker."""
        eventList = self.pickUp(self.eventPath)
        return eventList

    def makeFigures(self, eventList):
        """Producing figures to show trends in the concert data."""
        # Make dataframe
        df = pd.DataFrame(eventList)

        # Convert dateStr to datetime format
        for index, row in df.iterrows():
            row['Date'] = dt.date(pd.to_datetime(row['Date']))

        # Produce plots
        self.plotDates(df)
        venues = self.plotVenues(df)
        self.plotVenueGenres(df, venues)

        return 'See figures.'

    # Auxiliary plotting functions
    def plotDates(self, data, numberOfDays=60, threshold=6):
        """Plot showing how total number of concerts in Leeds varies by date."""
        # Transform data
        rawData = data.groupby('Date').count()
        restrictedData = rawData[:numberOfDays]

        # Create bar colours
        colours = list()
        count = 0
        for index, row in restrictedData.iterrows():
            colour = 'darkred' if row['EventID'] > threshold else 'navy'
            count += row['EventID']
            colours.append(colour)

        # Plot
        plt.rcParams["figure.figsize"] = [10, 10]
        restrictedData.EventID.plot.bar(color=colours)
        plt.title('Total number of concerts: {0}'.format(count))
        plt.xlabel('Date')
        plt.ylabel('Concerts')
        plt.tight_layout()
        plt.savefig(self.figPath.format('dates'))

    def plotVenues(self, data, numberOfVenues=10):
        """Plot showing how the number of concerts varies across 
        different venues in Leeds."""
        # Transform data
        m = data.Venue.value_counts()[:numberOfVenues]

        # Plot
        plt.rcParams["figure.figsize"] = [10, 10]
        m.plot.bar()
        plt.xlabel('Venues')
        plt.ylabel('Concerts')
        plt.tight_layout()
        plt.savefig(self.figPath.format('venues'))
        return list(m.index.values)

    def plotVenueGenres(self, data, venues, genreThreshold=2, venueThreshold=10):
        """Plot showing how the genres of concerts varies across different venues."""
        # Create a dict of form:
        #   {venue1: {genre1: count1, genre2: count2...}, venue2:...}
        # for the top venues found in self.plotVenues()

        venueDict = self.makeVenueGenresDict(data, venues)

        # Reduce further by filtering for when there's enough occurrence of a genre at that venue
        reducedVenueDict = self.makeReducedVenueDict(venueDict, venues, 
            genreThreshold, venueThreshold)

        # Plot
        plt.rcParams["figure.figsize"] = [10, 10]
        newData = pd.DataFrame(reducedVenueDict).transpose()

        colours = ['#8B0000', '#008B00', '#00008B', '#FFFF00', '#FFA500']
        newData.plot.bar(stacked=True, color=colours)

        # newData.plot.bar(stacked=True)
        plt.xticks(rotation=45)
        plt.xlabel('Venues')
        plt.ylabel('Occurrences')
        plt.tight_layout()
        plt.savefig(self.figPath.format('venueGenres'))

    # Auxiliary venue-genre functions
    def makeVenueGenresDict(self, data, venues):
        """Make a dict of venues, for each of which the value is a dict of the 
        counts of how many concerts at that venue fall under a particular genre.
        This is simplified by try to generalise sub-genres of metal, punk, rock
        and pop to their aforementioned umbrella genres."""
        genreList = ['metal', 'punk', 'rock', 'pop']
        venueDict = dict()
        # Filter down to the venues found when plotting the venues
        reducedData = data[data['Venue'].isin(venues)]
        for index, row in reducedData.iterrows():
            v = row['Venue']
            g = row['Genres']
            if v not in venueDict and v in venues:
                venueDict[v] = dict()
            if isinstance(g, list):
                for genre in g:
                    newGenre = 'other'
                    # Try to capture the genre in a generalisation
                    for generalisation in genreList:
                        if generalisation in genre:
                            newGenre = generalisation
                            break
                    # Clean up whatever we have
                    cleanGenre = self.cleanUpGenre(newGenre)

                    if cleanGenre not in venueDict[v]:
                        venueDict[v][cleanGenre] = 1
                    else:
                        venueDict[v][cleanGenre] += 1

        return venueDict

    def makeReducedVenueDict(self, venueDict, venues, genreThreshold, venueThreshold):
        """Filter the venueDict down to venues that meet the requisite threshold
        of concerts at that venue, and to genres that meet the requisite threshold
        of concerts that fall under that genre at the venue."""
        reducedVenueDict = dict()
        for venue in venues:
            tempDict = dict()
            total = 0
            for genre, count in venueDict[venue].items():
                if count > genreThreshold:
                    tempDict[genre] = count
                    total += count
            if total > venueThreshold:
                reducedVenueDict[venue] = tempDict

        return reducedVenueDict

    def cleanUpGenre(self, genreStr):
        replacementList = ['(', ')', 'music', 'amp;']

        genre = genreStr
        for replacement in replacementList:
            genre = genre.replace(replacement, '')
        return genre.strip()
