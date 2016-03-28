from library import read_csv, database
import json
import datetime
import sys

listing_dict = {} #listing_id:{year:{day:occupancy}}
start = datetime.date(2014, 01, 01)
stop = datetime.date(2016, 1, 30)
#all data in one dictionary for ease:
all_dict = {}
days_advance = {}
valid_ids = []
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
            print "this listing_id has no occupancy_data: ", listing_id

    return final

#list_data is a list of all the listing_id

def get_valid_ids():
    global valid_ids
    thesis_data = database.database("Thesis")
    pot_listings = thesis_data.get_data("SELECT `listing_id` FROM listing_clusters_plain")
    valid_ids = [entry[0] for entry in pot_listings]
    thesis_data.destroy_connection()


def get_data():

    query = "SELECT `listing_id`,`checkin`, `checkout`, `status`, `created_at`, `id` FROM `reservations` WHERE  (`additional_description` IS NULL OR (`additional_description` NOT LIKE 'test ' AND `additional_description` NOT LIKE ' test')) AND `checkin` >= '2013-01-01' AND `checkout` < '2016-01-30' AND `status` IN('ENQUIRY', 'CANCELLED') AND `listing_id` IS NOT NULL AND DATEDIFF(`checkin`, `created_at`) <= 365 AND DATEDIFF(`checkin`, `created_at`) >= 0 AND DATEDIFF(`checkout`, `checkin`) > 0 ORDER BY `status`;"

    database_worldhomes = database.database("worldhomes")
    database_worldhomes.cursor.execute(query)
    all_data = list(database_worldhomes.cursor.fetchall())

    database_worldhomes.destroy_connection()
    return all_data

'''
Make a super nested dictionary:

listing_id : {years} : {days} : 0/count

'''
def process_entry(this_entry):
    global all_dict, days_advance, valid_ids
    #listing_id, checkin, checkout, status, created_at, id
    if this_entry[3] not in all_dict.keys():
        all_dict[this_entry[3]] = {}

    listing_id = this_entry[0]
    if listing_id not in all_dict[this_entry[3]].keys() and listing_id in valid_ids:
        all_dict[this_entry[3]][listing_id] = default_date_structure()

    if listing_id not in valid_ids:
        return

    day_count = 1
    for day in _daterange(this_entry[1], this_entry[2]):

        #if this day is still empty, we need to make it into a
        if not all_dict[this_entry[3]][listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")]:
            all_dict[this_entry[3]][listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")] = {}

        #fill in calendar
        all_dict[this_entry[3]][listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")][this_entry[5]] = {'created_at': this_entry[4].strftime("%Y-%m-%d"), 'percent_of_occupation': float(day_count)/int( (this_entry[2].date() - this_entry[1].date()).days) }

        day_count += 1

def insert_zeros():
    global listing_dict

    #get earliest_dates (might as well):
    data_thesis = database.database("Thesis")
    earliest_dates = data_thesis.get_data("SELECT * FROM `earliest_date`")

    for entry in earliest_dates: #for every listing
        #fetch entry date data
        #all_dict: status, listing_id, year
        for status, all_data in all_dict.iteritems():
            #entry[0] = listing_id
            try:
                for year, days in all_data[entry[0]].iteritems():
                    for day, occupancy in days.iteritems(): #within the year
                        try:
                            if int( (datetime.datetime.strptime(day, "%Y-%m-%d").date() - entry[1]).days ) > 0:
                        #if the day is after the earliest recorded date of activity
                                if occupancy is None:
                                    listing_dict[entry[0]][year][day] = 0
                        except Exception as e:
                            pass
                            #sys.exit()
            except Exception as e: #most likely listing has no data for this year
                pass


    data_thesis.destroy_connection()


def save_data():
    global all_dict
    for status, all_listing_data in all_dict.iteritems():
        print "On status, ", status
        filename = "data/" + str(status) + ".json"
        with open(filename, 'w') as outfile:
            json.dump(all_listing_data, outfile)

def main():
    my_data = get_data()
    get_valid_ids()

    for entry in my_data:
        process_entry(entry)

    #print "finished processing entries in my data, now need to insert 0's"

    #insert_zeros()

    print "finished inserting zeros"
    #read_csv.print_dict_to_csv()
    #
    print "at least putting things into a json"

    #delete everything first
    save_data()

    print "finished"





if __name__ == '__main__':
    main()


