# Imports

# Class
class DataAnalysisWorker(Worker):
	def __init__(self):
		super().__init__()

        self.product = 'visualisations'

        # Stages
        self.stageList = []
        self.stageDict = {}

