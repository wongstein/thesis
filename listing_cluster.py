
import dbscan
from library import database
from sklearn.cluster import DBSCAN
from sklearn.mixture import DPGMM
import sys

'''
input the normal data, cleans out the really empty entries
returns a list of 2 lists, (data, identification)
'''
def _check_data(data, to_check):
	final = []
	identification = []
	for entry in data:
		row = []
		okay = True
		for x in to_check:
			if entry[x] == 0:
				okay = False
		if okay is True:
			final.append(entry[1:])
			identification.append(entry[0])
	return [final,identification]


'''
This is an internal function to test with DBSCAN for clustering.  Automatically
updates values
takes in the full data, and the labels and database connection
'''
def _DBSCAN(cluster_data, identification, db):
		#try the dbscn
	dbscan = DBSCAN().fit(cluster_data)
	core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
	core_samples_mask[dbscan.core_sample_indices_] = True
	labels = dbscan.labels_
	n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

	print('Estimated number of clusters with DBSCAN: %d' % n_clusters_)

	final = [] #listing_id, label, city, country
	for n in range(0,len(identification)):
		final.append([identification[n],labels[n]])
	print len(final)
	print final[:3]

	return final

'''
Internal function to run dirichlet
'''
def _Dirichlet(cluster_data, identification):
	print "In Dirichlet"
	for i in range(0,3):
		print "i is ", i
		dirichlet = DPGMM(n_components = len(cluster_data)).fit(cluster_data)
	#paremeters= dirichlet.get_params #returns parameters of the algorithm as a whole from the fit
		predict = dirichlet.predict(cluster_data)
		n_clusters_ = len(set(predict)) - (1 if -1 in predict else 0)
		print('Estimated number of clusters with Dirichlet: %d' % n_clusters_)

	final = []
	for x in range(0,len(identification)):
		final.append([identification[x],predict[x]])

	print "this is what final sort of looked like"
	print final[:3]

	return final


'''
For the test we are going to do the big just for barcelona
'''
def main():
	from library import database #don't know why all of the sudden this needs to be in the function
	data_thesis = database.database("Thesis")

	query_plain = "SELECT * FROM `features_plain_gobig`;"
	query_fancy = "SELECT * FROM `features_fancy`;"

	data_plain = data_thesis.get_data(query_plain)
	data_fancy = data_thesis.get_data(query_fancy)

	#sorting data
	go_plain = [[float(item) for item in entry[1:]] for entry in data_plain]
	go_plain_identification = [entry[0] for entry in data_plain]

	go_fancy = [[float(item) for item in entry[1:]] for entry in data_fancy]
	go_fancy_identification = [entry[0] for entry in data_fancy]

	print "Let's try to isolate clusters by location!"

	#_DBSCAN(cluster_data, identification, db)
	plain_final = _Dirichlet(go_plain, go_plain_identification)
	fancy_final = _Dirichlet(go_fancy, go_fancy_identification)

	'''
	go big: 11 clusters (full data)
	go small = 13 clusters (full data)
	data: listing_id, cluster
	'''

	#save data
	data_thesis.clear_table("listing_clusters_fancy")
	data_thesis.clear_table("listing_clusters_plain")

	for x in range(0, len(plain_final)):
		data_thesis.add_entry_to_table("listing_clusters_plain", plain_final[x])
		data_thesis.add_entry_to_table("listing_clusters_fancy", fancy_final[x])

	data_thesis.destroy_connection()


if __name__ == '__main__':
	main()