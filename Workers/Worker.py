# Imports
import json
import os

# Class
class Worker():
    """Class representing the generic worker, from which more specific workers inherit"""
    def __init__(self):
        self.product = 'generic'

        self.stageList = list()
        self.stageDict = dict()

        self.baseDir = 'output'

    def work(self, start, end):
        """Main function that gets each worker to do whatever work you ask of it.
        :param start: start stage contained in the stageList, can be indexed by either int or str
        :param end: end stage contained in the stageList, can be indexed by either int or str
        :returns: None"""
        # Parameter checking
        first, last = self.stageChecks(firstStage=start, lastStage=end)

        # stageRange is inclusive of last stage
        stageRange = list(range(first, last+1))

        # Report what worker is working on, and which stages
        print('working on product: {0}'.format(self.product))
        print('stages: {0}'.format(stageRange))

        # Checking if required output directories exist
        self.initialChecks()

        # For each stage, get data from previous stage, run method and write output
        for i, stage in enumerate(self.stageList):
            if i in stageRange:
                print('Starting {0}'.format(stage))
                # There is nothing for stage 0 to pick up, because no stage precedes it
                if i != 0:
                    inputData = self.pickUp('{0}/{1}/{2}.json'.format(self.baseDir, 
                                            self.product, self.stageList[i-1]))
                    outputData = self.stageDict[stage](inputData)
                else:
                    outputData = self.stageDict[stage]()
                self.putDown(outputData, '{0}/{1}/{2}.json'.format(self.baseDir, 
                                self.product, stage))
                print('Completed {0}'.format(stage))

    def initialChecks(self):
        """Ensure that relevant output directories exist.
        :returns: None"""
        outputPath = './{0}/{1}'.format(self.baseDir, self.product) if self.product != 'generic' else self.baseDir
        if outputPath and not os.path.exists(outputPath):
            os.makedirs(outputPath)

    def stageChecks(self, firstStage, lastStage):
        """Get the indices of the start and end stages in stageList.
        :param firstStage: start stage contained in the stageList, can be indexed by either int or str
        :param lastStage: end stage contained in the stageList, can be indexed by either int or str
        :returns: indices of first and last stages in stageList"""
        # Type-checking - parameters should both be keys or ints
        if type(firstStage) != type(lastStage):
            raise TypeError('Stage types do not match.')

        # Continue under the assumption that parameters have matching types
        # Convert to indices if required
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

    def pickUp(self, path):
        """Read data from previous stage.
        :param path: path from which data is read, str
        :returns: data contain in file at provided path"""
        with open(path) as infile:
            item = json.load(infile)
        return item

    def putDown(self, item, path):
        """Write output data at end of stage.
        :param item: data to be written
        :param path: path to which data is written, str
        :returns: None"""
        with open(path, 'w') as outfile:
            json.dump(item, outfile)

    def dictKeyFilter(self, inputDict, keysToKeep):
        """Filter down a dict to only the keys that we want.
        :param inputDict: dictionary to be filtered down
        :param keysToKeep: keys desired in the returned dictionary
        :returns: filtered down dictionary"""
        return {k: v for k, v in inputDict.items() if k in keysToKeep}
