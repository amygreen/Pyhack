from PythonHackathon.PythonHackathon_Mos.GroupStatistics import *

class TestGroupStatistics():

	def test_invalid_run_inp1(self):
		self.GroupStatistics = GroupStatistics(data_folder='.')
		try:
			result = GroupStatistics.run(mean='@', std=True)
		except TypeError:
			print('Input mean value must be True or False')
			return True
		else:
			return False

	def test_invalid_run_inp2(self):
		self.GroupStatistics = GroupStatistics(data_folder='.')
		try:
			result = GroupStatistics.run(mean=True, std='@')
		except TypeError:
			print('Input std value must be True or False')
			return True
		else:
			return False

	def test_invalid_GroupStatistics_inp(self):
		try:
			result = GroupStatistics(data_folder='')
			result = GroupStatistics(data_folder=123)
			result = GroupStatistics(data_folder='#$%')
		except TypeError:
			print('Input data_folder must be a valid path')
			return True
		else:
			return False
