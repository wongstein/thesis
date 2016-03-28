import os
import csv
import numpy as np
from decimal import *
import re
'''
This function reads a csv file and outputs a list of lists to represent the array
of data it has read.  It takes in the name of the file and assumes the file
is in the "data" folder.  It also takes in a list of column number (columns
	start from 0) that the user wants
to include from csv.  Or else it defaults to all.  This is meant to be a public
function.
'''
def csv_to_array(FileName, columns=None):
	#get in data directory
	os.chdir("/Users/ameewongstein/Thesis/data")
	#print "this is the working directory ", os.getcwd()
	filename = FileName

	if columns is None:
		#print "you have entered no columns, so we default to all"
		columns = []
		f = open(filename, 'r')
		first_line = f.readline()
		total = parse_string(first_line)
		for n in range (0, len(total)):
			columns.append(n)
		f.close()

	data_list = []
	with open(filename, 'r') as f:
		for line in f.readlines():
			column_count = 0
			row = []
			first_line = parse_string(line)

			#make sure we only get the things in columns
			for n in first_line:
				if column_count in columns:
					row.append(n)
					column_count += 1
				else:
					column_count += 1
			if not row: #to delete empty rows
				continue
			data_list.append(row)

	return data_list

'''
This is a public function meant to print a list of lists into a csv file
'''
def print_to_csv(filename, list_array):
	os.chdir("/Users/ameewongstein/data")
	delete_contents(filename)
	with open(filename, 'a') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		for i in range(0, len(list_array)):
			spamwriter.writerow(list_array[i])

'''
This is a private function that takes a list and outputs a csv appropriate sentence.
'''
def list_to_string(list):
	string = ''
	for item in list:
		string.append(item)
		string.append(", ")
	string.append('\n')
	return string


'''
this is a private function to parse the string better.
'''
def parse_string(string): #defaults to null unless otherwise specified
	string = string.replace('\n', '')
	split_string = string.split('"')
	second_split = []
	for item in split_string:
		if item != ',': #then this item contains a valuable string
			try:
				numbers = item.split(',')
				for n in numbers:
					if len(n) > 0 and n!='\n':
						try:
							second_split.append(float(n))
						except ValueError: #then it's just a string value
							second_split.append(n)
			except ValueError: #for long word descriptions
				item = item.replace(',', '')
				second_split.append(item)
				continue
			except IndexError:
				continue

	return second_split

'''
This is a private function that takes in the first line of a csv (the column names) as a string and
determines if there is a title column included.  Returns the column number of title, and false if
there is no title
'''
def have_title(column_names):
	column_names.replace('"', '')
	columns = column_names.split(',')
	for n in range(0, len(columns)):
		if n == 'title':
			return n
	return False


'''
This function deletes all contents in a file that is entered as a string in the parameter
'''
def delete_contents(filename):
	f = open(filename, 'r+')
	f.truncate()

def print_dict_to_csv(filename, dict_entry):
	os.chdir("/Users/ameewongstein/Thesis/data")
	delete_contents(filename)
	with open(filename, 'a') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		for key,value in dict_entry.iteritems():
			spamwriter.writerow(list_array[i])








