from library import database, time
import json
import datetime
import sys

'''
Current definitional logic

purpose1: We want the prediction system to forecast for occupancy that comes from online platforms (rather than just from )

purpose2: We want to make prediction system that can guess overall occupancy, regardless if it comes from online or from owner themself
'''

listing_dict = {} #listing_id:{year:{day:occupancy}}
start = datetime.date(2013, 01, 01)
stop = datetime.date(2016, 1, 30)
clusters_data = {} #ENQUIRY/cancellation: cluster_id: {listing_cluster_id:[listing_ids]}

#ENQUIRY/cancellation/cluster_averages: default date structure
records = {}
records_averages = {"ENQUIRY" : {}, "CANCELLED": {}} #ENQUIRY/cancellation/year: location_id/cluster_id/ day: average_cancel/occupancy
records_averages_full_year = {"ENQUIRY" : {}, "CANCELLED": {}}
records_total_counts = {"ENQUIRY" : {}, "CANCELLED": {}} #ENQUIRY/cancellation: location_id/cluster_id: day: [all values in cluster_id]

#location_id: listing_cluster_id: year: day:

def load_data():
    global records

    for filename in ["ENQUIRY", "CANCELLED", "cluster_averages", "occupancy_dict"]:
        with open ("data/" + filename + ".json") as jsonFile:
            records[filename] = json.load(jsonFile)


def structure_records_total_counts():
    data_thesis = database.database("Thesis")

    global records_total_counts, max_num
    #get location clusters
    location_clusters = data_thesis.get_data("SELECT `features_plain_gobig`.`listing_id`, `location_cluster`, `cluster` FROM `features_plain_gobig` INNER JOIN `listing_clusters_big_all` ON `features_plain_gobig`.`listing_id` = `listing_clusters_big_all`.`listing_id` WHERE location_cluster != -1") #trying go big for now

    #make structure for the pulled data
    #`listing_id`, `location_cluster`, `cluster`
    #
    #
    #structure for the final datastructure
    #location_cluster : { listing_cluster: { year: {day: percentage occupied}}}

    for year in ["2013", "2014", "2015", "2016"]:
            records_averages_full_year["ENQUIRY"][year] = {}
            records_averages_full_year["CANCELLED"][year] = {}

    for entry in location_clusters:
        #if the location cluster
        if entry[1] not in records_total_counts["ENQUIRY"]:
            for filename in ["ENQUIRY", "CANCELLED"]:
                records_total_counts[filename][entry[1]] = {}
                records_averages[filename][entry[1]] = {}
                for year in ["2013", "2014", "2015", "2016"]:
                    records_averages_full_year[filename][year][entry[1]] = {}
                    #if the listing_cluster
        if entry[2] not in records_total_counts["ENQUIRY"][entry[1]].keys():
            for filename in ["ENQUIRY", "CANCELLED"]:
                records_total_counts[filename][entry[1]][entry[2]] = time.default_date_structure()
                records_averages[filename][entry[1]][entry[2]] = time.default_date_structure()
                for year in ["2013", "2014", "2015", "2016"]:
                    records_averages_full_year[filename][year][entry[1]][entry[2]] = {}

    data_thesis.destroy_connection()

'''
put lisitng_id as int
'''
def _get_end_date(listing_id, end_dates):
    global final_record_dates

    try:
        active = end_dates[listing_id]["active"]
        if active == 1:
            #make pick deleted_at
            if end_dates[listing_id]["deleted_at"]:
                end_date1 = end_dates[listing_id]["deleted_at"]
                end_date2 = final_record_dates[listing_id]

                #sometimes there are occupancy data outside of deleted dates
                return max(end_date1, end_date2)
            else:
                #or else it's still an active listing
                return None
        else:
            #this listing shouldn't be active
            if end_dates[listing_id]["deleted_at"]:
                end_date1 = end_dates[listing_id]["deleted_at"]
                end_date2 = final_record_dates[listing_id]

                return max(end_date1, end_date2)
            else:
                end_date1 = end_dates[listing_id]["updated_at"]
                end_date2 = final_record_dates[listing_id]

                return max(end_date1, end_date2)
    except KeyError:
        return None


''''
Logic: we are going to treat a whole lisitng like a hotel.  Thus, the enquiry counts are cumulative and will be averaged later against a year high.
'''
def fill_records_total_counts_data():
    structure_records_total_counts()
    global records, records_total_counts, max_num

    print "Finished making getting the data structures ready"
    '''
    Now we begin to find the averages per day
    '''
    data_thesis = database.database("Thesis")
    #find average for each day (pain in ass)
    for filename in ["ENQUIRY", "CANCELLED"]:
        print "on: ", filename
    #for filename in ["ENQUIRY"]:
        for location_cluster, listing_cluster in records_total_counts[filename].iteritems():
            print "On location, ", location_cluster
        #for location_cluster in [1]:
            #print "On location: ", location_cluster
            for listing_cluster_id, date_data in records_total_counts[filename][location_cluster].iteritems():
            #for x in range(1,5):
                for year, days_data in date_data.iteritems(): #day is a string?
                #print "On lisitng_cluster, ", x

                #listing_cluster_id = x
                #for year in ["2013"]:
                    for this_day, day_list in days_data.iteritems():
                        days_data[this_day] = []
                #find the average
                        query = "SELECT `features_plain_gobig`.`listing_id` FROM `features_plain_gobig` INNER JOIN `listing_clusters_big_all` ON `features_plain_gobig`.`listing_id` = `listing_clusters_big_all`.`listing_id` WHERE `location_cluster` = %s AND `cluster` = %s GROUP BY `listing_id`"
                        listing_id_set = data_thesis.get_data(query % (location_cluster, listing_cluster_id))

                        #type check
                        if isinstance(listing_id_set[0], tuple) or isinstance(listing_id_set[0], list):
                            listing_id_set = [entry[0] for entry in listing_id_set]

                        #process
                        for listing_id in listing_id_set:
                            try:
                                days_data[this_day].append(len( records[filename][str(listing_id)][year][this_day].keys()) )
                                #print "adding entry for cluster", x, ": ", this_day, ": ", days_data[this_day]

                            except Exception:
                                #there's nothing on this day in the database

                                #check to see if active date
                                try:
                                    date_activity = records["occupancy_dict"][str(listing_id)][year][this_day]
                                    if date_activity == 0:
                                        days_data[this_day].append(0)
                                except KeyError: #there is no occupancy data, let's delete this entire listing
                                    pass

                    #do average calculations here in the year section
                    print "doing averages for year, ", year
                    to_add = fill_records_averages(days_data)

                    records_averages[filename][location_cluster][listing_cluster_id][year] = fill_records_averages(days_data)
                    if to_add is False:
                        del records_averages_full_year[filename][year][location_cluster][listing_cluster_id]
                    else:
                        "Huzzah some records for year, ", year, "location, ", location_cluster
                        records_averages_full_year[filename][year][location_cluster][listing_cluster_id][year] = to_add

    data_thesis.destroy_connection()

def fill_records_averages(year_data_dict):
    final = {}
    year_counts = [sum(entry) for entry in year_data_dict.values()]
    year_max = max(year_counts)
    valid_year = True
    for day, day_list in year_data_dict.iteritems():
        if day_list: #if it exists
            final[day] = _get_averages(day_list, year_max)
        else:
            valid_year = False
    if valid_year:
        return final
    else:
        return False


def _get_averages(day_data, year_max):
    final = {"percentage_of_max": None, "average_enquiries": None}

    all_valid = []
    for entry in day_data:
        if entry is not None:
            all_valid.append(entry)

    if all_valid and year_max > 0:
        final["percentage_of_max"] = float( sum(all_valid) )/year_max
        final["average_enquiries"] = float( sum(all_valid) )/len(all_valid)
    elif all_valid and sum(all_valid) == 0:
        final["percentage_of_max"] = 0
        final["average_enquiries"] = float( sum(all_valid) )/len(all_valid)

    return final



def main():
    load_data()
    #fill_records_total_counts()

    print "let's find the total number of CANCELLED and ENQUIRY per cluster per day"

    fill_records_total_counts_data()

    #print "now averages"
    #fill_records_averages()


    print "saving"
    for filename in ["ENQUIRY", "CANCELLED"]:
        with open("data/" + filename + "_averages_by_listing_cluster.json", 'w') as outFile:
            json.dump(records_averages[filename], outFile)
        with open("data/" + filename + "_averages_by_listing_cluster_year.json", 'w') as outFile:
            json.dump(records_averages_full_year[filename], outFile)

    print "finished!"

if __name__ == '__main__':

    #all inclusive
    main()

    #just confirmed_internet_bookings