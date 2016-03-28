'''
the purpose of this private function is to provide a general template on which I can clean
query searches so that i have a in my final data, just one entry per value specified in
unique_column.  

Inputs: data_array (as a list of lists), and the column number that we want, assuming we are
are starting ocunt at 0
'''
def clean_me(excess_data, unique_column): 
	my_dict = {}
	data_final = []

	for row in excess_data:
		if row[unique_column] not in my_dict.keys():
			data_final.append(row)
			my_dict[row[unique_column]] = 0
	
	return data_final
