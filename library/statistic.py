#import pandas
import statistics
import scipy

'''
Internal function to determine the mode of a data set
'''
def _mode(data_dict):
	most = 0
	most_key = 0
	for key,value in data_dict.iteritems():
		if value > most:
			most = value
			most_key = key

	return most_key


'''
Does basic stats when given a list of values to analyse
returns a dictionary with these basic states
'''
def basic_stats(total_data):
	mean = statistics.mean(total_data)
	median = statistics.median(total_data)
	mode = statistics.mode(total_data)
	standard_dev = statistics.stdev(total_data)

	return [mean, median, mode, standard_dev]

if __name__ == '__main__':
	basic_stats([1,2,3,4,5])

