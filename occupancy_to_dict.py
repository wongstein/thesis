from library import database
from library import read_csv
import json
import datetime
import sys

'''
Current definitional logic

purpose1: We want the prediction system to forecast for occupancy that comes from online platforms (rather than just from )

purpose2: We want to make prediction system that can guess overall occupancy, regardless if it comes from online or from owner themself
'''

listing_dict = {} #listing_id:{year:{day:occupancy}}
table = "confirmed_dateDict"
start = datetime.date(2013, 01, 01)
stop = datetime.date(2016, 1, 30)
clusters_listings = {} #cluster_id: {listing_cluster_id:[listing_ids]}
clusters_listings_with_data = [] #will hold pairings in dictionary format {}
final_record_dates = {}

def default_date_structure():
    final = {}
    years = ["2013", "2014", "2015", "2016"]

    for year in years:
        final[year] = {}

        for day in _daterange(datetime.date(int(year), 01, 01), datetime.date(int(year), 12, 31)):
            final[year][day.strftime("%Y-%m-%d")] = None

    return final


def _daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1): #weird bug, missing the last day, this is a hack
        yield start_date + datetime.timedelta(n)


def _get_occupancy_data(list_data, day):
    global listing_dict
    final = []
    year = datetime.datetime.strptime(day, "%Y-%m-%d").date().strftime("%Y")
    for listing_id in list_data:
        try:
            final.append(listing_dict[listing_id][year][day])
        except Exception as e:
            pass
            #print "this listing_id has no occupancy_data: ", listing_id

    return final

#list_data is a list of all the listing_id
def _get_average(list_data, day):
    #get occupancy data for this day
    list_data = _get_occupancy_data(list_data, day)
    total_count = 0
    total_value = 0
    if list_data:
        for entry in list_data:
            if entry:
                total_value += entry
                total_count += 1
    else:
        return None
    print "returning a real value"
    return float(total_value)/total_count

def _fill_cluster_listings():
    data_thesis = database.database("Thesis")
    global clusters_listings
    #get location clusters
    location_clusters = data_thesis.get_data("SELECT `listing_clusters_plain`.`listing_id`,`listing_locations_DBSCAN_final`.`label_id`, `listing_clusters_plain`.`cluster_id` FROM `listing_clusters_plain` INNER JOIN `listing_locations_DBSCAN_final` ON `listing_locations_DBSCAN_final`.`listing_id` = `listing_clusters_plain`.`listing_id` WHERE label_id != -1;") #trying go big for now

    #make structure for the pulled data
    #`listing_id`, `location_cluster`, `cluster`
    #
    #
    #structure for the final datastructure
    #location_cluster : { listing_cluster: { year: {day: percentage occupied}}}
    for entry in location_clusters:
        #if the location cluster
        if entry[1] not in clusters_listings.keys():
            clusters_listings[entry[1]] = {}
        #if the listing_cluster
        if entry[2] not in clusters_listings[entry[1]].keys():
            clusters_listings[entry[1]][entry[2]] = default_date_structure()

    data_thesis.destroy_connection()

'''
Make a super nested dictionary:

listing_id : {years} : {days} : 0/1
'''
def process_entry(this_entry, valid_listings):
    global listing_dict, final_record_dates
    #make valid_ids control to lower memory costs


    #listing_id, checkin, checkout
    if this_entry[0] in valid_listings:
        listing_id = this_entry[0]
    else:
        return

    if listing_id not in listing_dict.keys():
        listing_dict[listing_id] = default_date_structure()

    for day in _daterange(this_entry[1], this_entry[2]):
        listing_dict[listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")] = 1
        final_record_dates[listing_id] = day

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


def insert_zeros():
    global listing_dict

    active_listing = []
    #get earliest_dates (might as well):
    data_worldhomes = database.database("worldhomes")
    earliest_dates = data_worldhomes.get_data("SELECT `id`, `created_at` FROM `listings`")
    earliest_dates_dict = {entry[0]: entry[1] for entry in earliest_dates}

    end_dates_list = data_worldhomes.get_data("SELECT `id`, `updated_at`, `deleted_at`, `active` FROM `listings`;")
    #sort into a dictionary
    end_dates = {entry[0]: {'updated_at': entry[1], 'deleted_at': entry[2], 'active': entry[3]} for entry in end_dates_list}


    for listing in listing_dict.keys(): #for every listing
        #fetch entry date data
        for year, days in listing_dict[listing].iteritems():
            for day, occupancy in days.iteritems(): #within the year
                #see if there is an end date entry
                end_date = _get_end_date(int(listing), end_dates)
                if end_date:
                #if end is still after current day, then positive number
                    days_before_end = int(
                        (end_date.date() - datetime.datetime.strptime(day, "%Y-%m-%d").date()).days)
                else:
                    days_before_end = None


                days_after_earliest = int( (datetime.datetime.strptime(day, "%Y-%m-%d").date() - earliest_dates_dict[int(listing)].date()).days)

                #even if occupancy, before official created date we make none
                if days_after_earliest:
                    if days_after_earliest < 0:
                        listing_dict[listing][year][day] = None

                if days_after_earliest and days_before_end:
                    if days_after_earliest >= 0 and days_before_end > 0:
                        if occupancy is None:
                            #print "made something 0 with days_before_end"
                            listing_dict[listing][year][day] = 0
                    if days_before_end <=0:
                        listing_dict[listing][year][day] = None

                elif days_after_earliest and not days_before_end:
                    if days_after_earliest >= 0:
                    #if the day is after the earliest recorded date of activity
                        if occupancy is None:
                                #print "made something 0 without days_before end"
                            listing_dict[listing][year][day] = 0
                    #else:
                        #print "nothing is happening"


    print "finished inserting zeros, here's what something looks like"
    print listing_dict[listing_dict.keys()[10]]


    data_worldhomes.destroy_connection()

def reinsert_nones():
    #for all confirmed, blocked_by_confirmed, unavailable that have no subcription id, make those dates None

    #get all occupancies that don't come from a sync event
    query = "SELECT `listing_id`,`checkin`, `checkout` FROM `reservations` WHERE `additional_description` NOT LIKE 'test ' AND DATE(`checkin`) >= '2013-01-01' AND DATE(`checkout`) < '2016-01-30' AND `listing_id` IS NOT NULL AND `status` IN('CONFIRMED','BLOCKEDBYCONFIRMED','UNAVAILABLE', 'DOUBLEBOOKING', 'CANCELLATIONREQUESTED') AND ((`portal_uid` = '' OR `portal_uid` IS NULL) AND (`subscription_id` IS NULL OR `subscription_id` = 0) AND (`gateway_listor_id` IS NULL OR `gateway_listor_id` = 0))"

def fill_cluster_data():
    _fill_cluster_listings()
    global clusters_listings, clusters_listings_with_data

    print "Finished making getting the data structures ready.  Time to find averages"
    '''
    Now we begin to find the averages per day
    '''
    data_thesis = database.database("Thesis")
    #find average for each day (pain in ass)
    for location_cluster, listing_cluster in clusters_listings.iteritems():
        for listing_cluster_id, date_data in listing_cluster.iteritems():
            for year, days_data in date_data.iteritems(): #day is a string?
                for this_day in days_data.keys():
                #find the average
                    query = "SELECT `listing_clusters_plain`.`listing_id` FROM `listing_clusters_plain` INNER JOIN `listing_locations_DBSCAN_final` ON `listing_clusters_plain`.`listing_id` = `listing_locations_DBSCAN_final`.`listing_id` WHERE `label_id` = %s AND `cluster_id` = %s GROUP BY `listing_id`"
                    occupancy_set = data_thesis.get_data(query % (location_cluster, listing_cluster_id))

                #get average and put it in
                average = _get_average(occupancy_set, this_day)
                clusters_listings[location_cluster][listing_cluster_id][year][this_day] = average
                if average:
                    clusters_listings_with_data.append({location_cluster:listing_cluster})

    print "finished here's a sample"
    #print clusters_listings[1][len(clusters_listings[1].keys()) - 2]
    data_thesis.destroy_connection()


def main():
    query = "SELECT `listing_id`,`checkin`, `checkout`, `created_at`, `additional_description` FROM `reservations` WHERE (`additional_description` IS NULL OR (`additional_description` NOT LIKE 'test ' AND `additional_description` NOT LIKE ' test')) AND `checkin` >= '2013-01-01' AND `checkout` < '2016-1-29' AND `listing_id` IS NOT NULL AND `status` IN('CONFIRMED','BLOCKEDBYCONFIRMED','UNAVAILABLE', 'DOUBLEBOOKING', 'CANCELLATIONREQUESTED') AND DATEDIFF(`checkin`, `created_at`) <= 365 AND DATEDIFF(`checkin`, `created_at`) > 0;"

    woldhomes_data = database.database("worldhomes")
    my_data = woldhomes_data.get_data(query)

    thesis_data = database.database("Thesis")
    valid_listings = thesis_data.get_data("SELECT `listing_id` FROM listing_locations_DBSCAN_final WHERE label_id IN(0, 1, 19);")
    valid_listings = [entry[0] for entry in valid_listings]

    for entry in my_data:
        process_entry(entry, valid_listings)

    print "finished processing entries in my data, now need to insert 0's"

    insert_zeros()


    print "now let's find the average cluster data for each day"
    fill_cluster_data()

    global clusters_listings
    #
    print "at least putting things into a json"

    cluster_filepath = "data/cluster_averages.json"
    occupancy_filepath = "data/occupancy_dict.json"

    with open(cluster_filepath, 'w') as outfile:
        json.dump(clusters_listings, outfile)

    with open(occupancy_filepath, 'w') as outfile2:
        json.dump(listing_dict, outfile2)

    print "Finished saving the average cluster listings data.  Onto occupancy_dict"

    woldhomes_data.destroy_connection()


if __name__ == '__main__':

    #all inclusive
    main()

    #just confirmed_internet_bookings


    '''
    global listing_dict
    data_thesis = database.database("Thesis")
    data_thesis.clear_table("occupancy_dict")
    for listing_id, occupancy_data in listing_dict.iteritems():
        data_thesis.execute("INSERT INTO `occupancy_dict` (listing_id) VALUES (%s);" % listing_id)
        for year, year_data in occupancy_data.iteritems():
            data_thesis.execute("UPDATE `occupancy_dict` SET `%s` = '%s' WHERE `listing_id` = %s" % (year, json.dumps(year_data), listing_id))

    global listing_dict
    data_thesis = database.database("Thesis")
    for listing_id, date_dict in listing_dict.iteritems():
        data_thesis.cursor.execute("UPDATE `confirmed_dateDict` (`data_dict`) INSERT VALUES %s WHERE `listing_id` = %s;" % (json.dumps(data_dict), listing_id))
        data_thesis.db.commit()
    '''
