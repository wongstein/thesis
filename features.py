#import features_functions
from library import feature_helper, database
import sys
import json

'''
private function to get the right bed_weights
takes in the option, which can either be a string "big" or "small"

returns the bed_weights as a dictionary where they key is the bed_type,
the entry is the bed_weight

database_name: apartment type, or bed weight
retunrs dict with : type: {big:, small:}
'''
listing_weights = {}
bed_weights = {}
def fill_weights():
	global listing_weights, bed_weights
	from library import database

	thesis_data = database.database("Thesis")

	data_list = thesis_data.get_data("SELECT * FROM `types_of_listings`;")
	listing_weights = {entry[0]: {'small': entry[4], 'big': entry[3]} for entry in data_list}

	data_list = thesis_data.get_data("SELECT * FROM `bed_types`;")
	bed_weights = {entry[0]: {"small": entry[2], 'big': entry[1]} for entry in data_list}

	thesis_data.destroy_connection()



'''
This program goes through the entries in all_data_better and tries to give listings this structure
#listing_id, location_cluster, number of rooms, number of bathrooms, type, size, bed_weight
'''
def organize_data():
	thesis_data = database.database("Thesis")
	print "\nNow let's shape up our features"
	my_data = thesis_data.get_data("SELECT `all_data_better`.`listing_id`, property_title, property_type, size, description, room_description, bed_count, bathroom_boolean, bed_type, accomodates, label_id FROM `all_data_better`  INNER JOIN `dbscan_labels_full` on `dbscan_labels_full`.`listing_id` = `all_data_better`.`listing_id` INNER JOIN `listings_accomodation` ON `listings_accomodation`.`listing_id` = `all_data_better`.`listing_id` WHERE label_id IN(0, 1, 19)")
	print "I have data! "
	print my_data[1]
	thesis_data.destroy_connection()

	final = {entry[0]:{"property_title": entry[1], "property_type": entry[2], "description": entry[4], "size": entry[3], "rooms": [], "beds": {}, "bathroom_count": 0, "accomodates": entry[9],"location": entry[9]} for entry in my_data}

	for entry in my_data:
		#my_data: listing_id, property_title, property_type, size, description, room_description, bed_count, bathroom_boolean, bed_type, accomodates, label_id (location)

		if entry[5] is not None and entry[5] > ' ':
			final[entry[0]]["rooms"].append(entry[5])
		else:
			final[entry[0]]["rooms"].append("empty_content")

		#beds
		if entry[8] is not None and entry[8] > " ":
			if entry[8] not in final[entry[0]]["beds"].keys():
				final[entry[0]]["beds"][entry[8]] = 1
			else:
				final[entry[0]]["beds"][entry[8]] += 1
		else:
			if "empty_content" not in final[entry[0]]["beds"].keys():
				final[entry[0]]["beds"]["empty_content"] = 1
			else:
				final[entry[0]]["beds"]["empty_content"] += 1

			#bathroom
		if entry[7] is not None:
			final[entry[0]]["bathroom_count"] += entry[7]

	return final

def save_general_features(full_listing_data):
	thesis_data = database.database("Thesis")
	#listing_id INT, property_title TEXT, description TEXT, property_type INT, size INT, room_count INT, bathroom_count INT, beds TEXT

	#truncate
	thesis_data.clear_table("listing_plain_features")
	query = "INSERT INTO `listing_plain_features` VALUES(%s, \"%s\", '%s', %s,%s, %s, %s, \"%s\", %s)"
	for listing_id, listing_data in full_listing_data.iteritems():
		beds = str(listing_data["beds"])
		#print query % (listing_id, listing_data["property_title"], listing_data["description"], listing_data["property_type"], listing_data["size"], len(listing_data["rooms"]), listing_data["bathroom_count"], beds)
		if listing_data["property_title"]:
			title = listing_data["property_title"]
		else:
			title = "null"
		if listing_data["description"]:
			description = listing_data["description"]
		else:
			description = "null"
		if listing_data["property_type"]:
			property_type = listing_data["property_type"]
		else:
			property_type = "null"
		if listing_data["size"]:
			size = listing_data["size"]
		else:
			size = "null"
		if listing_data["rooms"]:
			room_count = len(listing_data["rooms"])
		else:
			room_count = "null"
		if listing_data["accomodates"]:
			accomodates = listing_data["accomodates"]
		else:
			accomodates = "null"

		thesis_data.execute(query % (listing_id, title, description, property_type, size, room_count, listing_data["bathroom_count"], beds, accomodates))
		print "saved entry for, ", listing_id

#return list
#input is dictionary: data_dict = {entry[0]: {"property_type": entry[1], "room_count": entry[2], "bathroom_count": entry[3], "beds": entry[4], 'accommodates': entry[5]}}
def calculate_features(feature_dict, which_features):
	global bed_weights, listing_weights
	final = []

	for listing_id, listing_data in feature_dict.iteritems():
		row = [listing_id]
		#average bedweight per person
		beds = eval(listing_data["beds"])
		tot_weight = 0
		for bed, count in beds.iteritems():
			identification = bed.lower().split()[0] #first word is enough
			tot_weight += bed_weights[identification]["big"]

		if which_features == "plain":
			#make spread even
			row += [(listing_data["room_count"] * 1.5), listing_data["bathroom_count"] * 3, listing_weights[listing_data["property_type"]]["big"], listing_data["accommodates"], tot_weight]
			final.append(row)

		else: #this is the fancy one
			#average number of rooms per person
			this_average = float(listing_data["room_count"])/listing_data["accommodates"]
			#row.append(this_average/1.5)
			row.append(this_average * 20)

			#bedw weight
			this_average = float(tot_weight)/listing_data["accommodates"]
			#row.append(this_average/6.5) #HERE
			row.append(this_average * 10)

			#type
			type_weight = listing_weights[listing_data["property_type"]]["big"]
			#row.append(float(type_weight)/ 8)
			row.append(float(type_weight) * 1.5)

			#accommodation of max
			#row.append(float(listing_data["accommodates"])/18)
			row.append(listing_data["accommodates"])

			#bathroom average
			bathroom_average = float(listing_data["bathroom_count"])/listing_data["accommodates"]
			#row.append(bathroom_average/0.5)
			row.append(bathroom_average * 10)

			final.append(row)

	return final


def save_calculated_features(feature_list, database_name):
	#do later
	#features_plain_gobig_new
	#features_plain_gosmall_new
	thesis_data = database.database("Thesis")
	thesis_data.clear_table(database_name)

	for entry in feature_list:
		insert_string = ''
		for item in entry:
			insert_string = insert_string + str(item) + ", "
		insert_string = insert_string[: len(insert_string) - 2] #pop off last coma
		#print insert_string
		query = "INSERT INTO `" + database_name + "` VALUES(" + insert_string + ");"

		thesis_data.execute(query)

	thesis_data.destroy_connection()


def main():
	#save listing_features into listing_plain_features
	#listing_id INT, property_title TEXT, description TEXT, property_type INT, size INT, room_count INT, bathroom_count INT, beds TEXT
	#get all data
	thesis_data = database.database("Thesis")
	query = "SELECT `listing_id`, `property_type`, `room_count`, `bathroom_count`, `beds`, `accomodates` FROM `listing_plain_features` WHERE `accomodates` IS NOT NULL;"
	data = thesis_data.get_data(query)

	#
	data_dict = {entry[0]: {"property_type": entry[1], "room_count": entry[2], "bathroom_count": entry[3], "beds": entry[4], 'accommodates': entry[5]} for entry in data}
	#set weights
	fill_weights()

	features_plain = calculate_features(data_dict, "plain")
	save_calculated_features(features_plain, "features_plain_gobig")

	features_fancy = calculate_features(data_dict, "fancy") #with dimensions all within 0-1
	save_calculated_features(features_fancy, "features_fancy")

if __name__ == '__main__':
	main()





