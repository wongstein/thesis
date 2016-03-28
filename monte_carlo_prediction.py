from monte_carlo import MonteCarlo
from library import common_database_functions, time
import datetime
import json

'''
Every seperate k-means clustered season shall be it's own training set

training_dict needs to be in this format:
training_dict: first checkin_date of the season: all consecutive days in this season cluster

the days in the a day_start key must be consecutive.  IF there is a new season day inbetween, then it should be made into a new check-in key!
'''
training_dict_all = {}
def make_training_dict_structure():
    #listing_id: k_cluster_checkin: day: reservation data
    global training_dict_all

    #location: k_means_type: day: classification
    with open("data/k-means_season_clusters.json") as jsonFile:
        all_k_means_data = json.load(jsonFile)

    #goal: to group the trianin data so that each cluster is a consecutive span of days
    for location in [0, 1, 19]:
        training_dict_all[location] = {}

        #should be a year, convert to datetime objects, then sort
        original_days = [datetime.datetime.strptime(entry, "%Y-%m-%d") for entry in all_k_means_data['2014'][str(location)]['3'].keys()]
        sorted_days = sorted(original_days)

        #setup loop
        last_key = sorted_days[0]
        training_dict_all[location][last_key] = {}

        #output: training_dict_all: first_day: day: {}
        for x, day in enumerate(sorted_days):
            if all_k_means_data['2014'][str(location)]['3'][day.strftime("%Y-%m-%d")] == all_k_means_data['2014'][str(location)]['3'][last_key.strftime("%Y-%m-%d")]: #if the keys are the same
                training_dict_all[location][last_key][day] = {} #will hold all reservations later
            else:
                last_key = day #update
                training_dict_all[location][last_key] = {day:{}}

def fill_training_dict_with_reservations():
    global training_dict_all
    with open("data/monte_carlo_reservation_dict.json") as jsonFile:
        all_reservations = json.load(jsonFile)

    #all_reservations: location_id:year: day:reservations
    for location_id in [0, 1, 19]:
        listing_ids = common_database_functions.get_listings_for_location(location_id)
        valid_ids = [this_id for this_id in listing_ids if str(this_id) in all_reservations.keys()]
        for listing in valid_ids:
            for checkin, k_data in training_dict_all[location_id].iteritems():
                for day, dictionary in k_data.iteritems():
                    if all_reservations[str(listing)][str(day.year)][str(day.date())]:

                        for reservation, reservation_data in all_reservations[str(listing)][str(day.year)][str(day.date())].iteritems():
                            dictionary[reservation] = reservation_data

def single_listing_prediction(start_date, end_date):
    #reservations come as dict with int: duration_int
    for day in time._daterange(start_date, end_date
    myMonte = monte_carlo.ModifiedMonteCarlo(training_dict_all, 2)



def main():
    global training_dict_all
    make_training_dict_structure()
    fill_training_dict_with_reservations()

    #make monte_carlo object


    print "hello"

if __name__ == '__main__':
    main()
