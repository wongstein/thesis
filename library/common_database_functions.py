import database

'''
if the input is a list, the output is a dictionary where the the key is the location id and the value is a list of all listing_ids assocated

if not, then just a list is outputed
'''
def get_listings_for_location(location_id):
    #return listings that have at least one year of occupancy data
    #And restricted to barcelona

    if isinstance(location_id, list):
        final = {}
        for this_location in location_id:
            final[this_location] = get_listings_for_single_location(this_location)

        return final
    else:
        return get_listings_for_single_location(location_id)

def get_listings_for_single_location(location_id):
    testing_listings = []
    thesis_data = database.database("Thesis")

    query = "SELECT `listing_locations_DBSCAN_final`.`listing_id` FROM `listing_locations_DBSCAN_final` WHERE `label_id` = %s;"

    initial_data = thesis_data.get_data(query % location_id)

    thesis_data.destroy_connection()
    return [entry[0] for entry in initial_data]
