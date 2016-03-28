#!/usr/bin/python
from library import database
#import clean_locations_better
#import fill_locations
#import features
#import listing_cluster


def make_listing_clusters():
    #for now
    #shape up features
    import features

    #make big and small features (stored in database)
    features.main() #really only need to make fancy features

    #cluster
    import listing_cluster
    listing_cluster.main()


def make_jsons():
    import set_up_reservation_dicts
    set_up_reservation_dicts.main()

def set_dicts_and_averages():
    '''
    import occupancy_to_dict #okay March 21
    #all inclusive
    occupancy_to_dict.main()


    #do averages
    import listing_cluster_averages

    listing_cluster_averages.main()

    #graph
    import find_season_clusters
    find_season_clusters.main(True)

    #other dicts
    import price_dict
    price_dict.main()
    '''

    import set_up_confirmed_advance
    set_up_confirmed_advance.main()


    import set_up_reservation_dicts
    set_up_reservation_dicts.main() #03/15 redo for 03/16


def alternative_k_cluster():
    import enquiries_averages_of_max
    enquiries_averages_of_max.main()

    import new_k_means
    new_k_means.main()

def machine_learning_experiments(): #03/15 ran fine
    import machine_prediction_interactive

    #date_only
    #machine_prediction_interactive.date_only_experiments()

    #listing_features
    machine_prediction_interactive.price_experiments()

def monte_carlo():

    #make reservation dict in the right format
    import monte_carlo_make_dicts
    monte_carlo_make_dicts.main()

    #do the prediction

def main():
    #make_listing_clusters() #good 03/21
    # alternative_k_cluster()
    #set_dicts_and_averages() #good 03/21

    machine_learning_experiments()







if __name__ == '__main__':
	main()