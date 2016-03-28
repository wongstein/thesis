from library import database, read_csv, clustering, graph, time
import json
import datetime


'''
data:

location_cluster: listing_cluster, day, day -> occupancy average. (just one D clustering)

by year: 2015, 2014


'''
cluster_averages = {}
date_dict = {}

def _get_city(location_cluster):
    thesis_database = database.database("Thesis")
    data_list = thesis_database.get_data("SELECT `city` FROM `listing_locations_DBSCAN_final` WHERE `listing_locations_DBSCAN_final`.`label_id` = %s GROUP BY `label_id`" % (int(location_cluster)) )
    thesis_database.destroy_connection()
    return data_list[0][0]

def _look_at_graph(results_store):
    global cluster_averages, date_dict
    #let's look at a graph real fast
    for year, location_results in results_store.iteritems():
        for location_cluster, k_cluster_number in location_results.iteritems():
            for k_cluster_number, k_cluster_data in k_cluster_number.iteritems():
                city = _get_city(location_cluster)
                try:
                    this_graph = graph.graph(("K_Means Clustered: %s, %s, %s" % (city, year, k_cluster_number)), "days as int", "average occupancy")
                except UnicodeDecodeError:
                    this_graph = graph.graph(("K_Means Clustered: %s, %s, %s" % ("location_cluster %s" % location_cluster, year, k_cluster_number)), "days as int", "average occupancy")
                for k_cluster, days_list in k_cluster_data.iteritems():
                    x = []
                    y = []
                    for day in days_list:
                        for listing_cluster in cluster_averages[year][location_cluster].keys():

                            try:
                                if cluster_averages[year][location_cluster][listing_cluster][day] is not None:
                                #need to include 0's into the clustering
                                    try:
                                        x.append(date_dict[year][day])
                                        y.append(cluster_averages[year][location_cluster][listing_cluster][day])
                                    except KeyError as e:
                                        #this day is not in the date_dict, and we don't care
                                        pass
                            except KeyError as e: #date is out of bounds
                                pass

                    this_graph.plot_scatter_plot(x, y)
                this_graph.show_plot()

def main(graph = False):
    #get data called
    global cluster_averages, date_dict


    cluster_averages_filepath = "data/cluster_averages_year.json"
    save_to = "data/k-means_season_clusters.json"

    with open(cluster_averages_filepath) as jsonFile:
        cluster_averages = json.load(jsonFile)

    #make date
    date_dict = {}
    for year in [2013, 2014, 2015, 2016]:
        date_dict[str(year)] = time.day_int_dict(datetime.date(year, 01, 01), datetime.date(year, 12, 31))

    #put do thes by year
    results_store = {}

    #year: {location_id: k_means_type: day: cluster_designation}
    json_dump = {}

    for year in cluster_averages.keys():
        results_store[year] = {}
        json_dump[year] = {}
        for location_cluster,  listing_cluster_data in cluster_averages[year].iteritems():
            data_entry = {}
            valid_day = {}
            #set up the data: day:[averages]
            for listing_cluster, date_data in listing_cluster_data.iteritems():
                for day, average in date_data.iteritems():
                    #make sure only valid data added
                    if day not in valid_day.keys() and average is not None:
                        valid_day[day] = True

                    #only add values that exist and associated with valid day
                    if average is None:
                        valid_day[day] = False
                        print "deleted a data_entry" #never enters but it should
                        try:
                            del data_entry[day]
                        except KeyError: #they haven't added this day yet and we'll keep it that way
                            pass

                    elif average is not None and valid_day[day] is True:
                        if day not in data_entry.keys():
                            data_entry[day] = []
                        data_entry[day].append(average)



            data = data_entry.values()
            identification = data_entry.keys()

            print "On location: ", location_cluster, ", year: ", year, " with ", len(identification), " samples"

            for number_clusters in [2,3]:
                if len(data) > number_clusters:
                    k_means = clustering.K_Means(data, identification, number_clusters)
                    k_means_clusters = clustering.list_dict_by_cluster(k_means)

                    if location_cluster not in results_store[year].keys():
                        results_store[year][location_cluster] = {}
                        json_dump[year][location_cluster] = {}


                    results_store[year][location_cluster][number_clusters] = k_means_clusters

                    json_dump[year][location_cluster][number_clusters] = {}

                    for cluster, date_list in k_means_clusters.iteritems():
                        for day in date_list:

                            json_dump[year][location_cluster][number_clusters][day] = cluster

    with open (save_to, "w") as jsonFile:
        json.dump(json_dump, jsonFile)


    if graph:
        _look_at_graph(results_store)


    print "finished!"

if __name__ == '__main__':
    main(False)














