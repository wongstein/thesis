
'''
Makes sure that an entry has the necessary information to be "valid"
Takes in a list as entry, which has all the fields that that data-point should have
Then checks the value specified by check, which should be an integer indicating
what place in the entry list to check (start from 0)

ex: entry = [0,1,NULL, NULL, 4,3]
	check = 2

	check_if_valid(entry,check) => False


'''
def check_if_valid(entry, check):
	try:
		if entry[check] == 'NULL':
			return False
		else:
			return True
	except IndexError:
		print entry

'''
Adds a listing to the unique list.
returns listing_rooms dictionary
'''
def save_a_room(entry, listing_rooms):
	if entry[0] not in listing_rooms.keys():
		listing_rooms[entry[0]] = 1
	return listing_rooms

'''
updates values for entry 
'''
def update_values(entry, weight_update, final_output):
	weight_sum += entry[3]
	save_a_room(entry)
	my_n += 1
