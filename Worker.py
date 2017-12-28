# Imports
import json
import os

# Class
class Worker():
    """class representing the generic worker, for which more specific workers inherit"""
    def __init__(self):
        self.product = 'generic'

        self.stageList = list()
        self.stageDict = dict()

        self.baseDir = 'output'

    def work(self, start, end):
        # Parameter checking
        first, last = self.stageChecks(firstStage=start, lastStage=end)

        # stageRange is inclusive of last stage
        stageRange = list(range(first, last+1))

        print('working on product: {0}'.format(self.product))
        print('stages: {0}'.format(stageRange))

        self.initialChecks()

        # for each stage, get data from previous stage, run method and write output
        for i, stage in enumerate(self.stageList):
            if i in stageRange:
                print('Starting {0}'.format(stage))
                if i != 0:
                    inputData = self.pickUp('{0}/{1}/{2}.json'.format(self.baseDir, self.product, self.stageList[i-1]))
                    outputData = self.stageDict[stage](inputData)
                else:
                    outputData = self.stageDict[stage]()
                self.putDown(outputData, '{0}/{1}/{2}.json'.format(self.baseDir, self.product, stage))
                print('Completed {0}'.format(stage))

    # ensure that relevant output directories exist
    def initialChecks(self):
        outputPath = './{0}/{1}'.format(self.baseDir, self.product) if self.product != 'generic' else self.baseDir
        if outputPath and not os.path.exists(outputPath):
            os.makedirs(outputPath)

    def stageChecks(self, firstStage, lastStage):
        # Type-checking - parameters should both be keys or ints
        if type(firstStage) != type(lastStage):
            raise TypeError('Stage types do not match.')

        # Continue under the assumption that parameters have matching types
        if isinstance(firstStage, str):
            first = self.stageList.index(firstStage)
            last = self.stageList.index(lastStage)
        elif isinstance(firstStage, int):
            first = firstStage
            last = lastStage
        else:
            raise TypeError('Stage types should be either int or self.stageDict keys.')

        if last < first:
            raise IndexError('Please pick an end stage that is not before the start stage.')

        return first, last

    # get data from previous stage
    def pickUp(self, path):
        with open(path) as infile:
            item = json.load(infile)
        return item

    # output data at end of stage
    def putDown(self, item, path):
        with open(path, 'w') as outfile:
            json.dump(item, outfile)

    # Write out csv data file
    def putDownCSV(self, item, path):
        print('Writing to {0}'.format(path))
        with open(path, 'w') as outfile:
            dataWriter = csv.DictWriter(outfile, fieldnames=item[0].keys())
            dataWriter.writeheader()
            dataWriter.writerows(item)

