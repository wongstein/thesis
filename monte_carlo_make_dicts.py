from library import database, time
import json

#listing_id: year: day: reservation: created_at, status: ,checkin, checkout:,
full_reservation_data = {}

def get_data():
    worldhomes_data = database.database("worldhomes")

    query = "SELECT `listing_id`,`created_at`, `checkin`, `checkout`, `status`, `id`, CASE status WHEN 'CONFIRMED' OR 'BLOCKEDBYCONFIRMED' OR 'CANCELLATIONREQUESTED' OR 'UNAVAILABLE' OR 'DOUBLEBOOKING' THEN 'CONFIRMED' END AS status FROM `reservations` WHERE `additional_description` NOT LIKE 'test ' AND `checkin` >= '2014-01-01' AND `checkout` < '2016-01-30' AND `listing_id` IS NOT NULL AND DATEDIFF(`checkin`, `created_at`) <= 365 AND DATEDIFF(`checkout`, `checkin`) >= 0 ORDER BY `status`;"
    full_data = worldhomes_data.get_data(query)
    worldhomes_data.destroy_connection()

    return full_data
#full_reservation_data : listing_id: day: reservationID{stuff here}
def process_data(entry):
    global full_reservation_data

    #`listing_id`,`created_at`, `checkin`, `checkout`, `status`, `id`
    ##comes in as datetime objects
    this_day = entry[2]
    year = this_day.year

    full_reservation_data[entry[0]][str(year)][this_day.date().strftime("%Y-%m-%d")] = {entry[5]: { 'created_at': entry[1].date().strftime("%Y-%m-%d"), "checkin": entry[2].date().strftime("%Y-%m-%d"), "checkout": entry[3].date().strftime("%Y-%m-%d"), "status": entry[4]}}


def main():
    global full_reservation_data

    all_data = get_data()

    #get valid_listings and make reservation structure
    thesis_data = database.database("Thesis")
    valid_listings = thesis_data.get_data("SELECT `listing_id` FROM     listing_clusters_plain")
    full_reservation_data = {entry[0]: time.default_date_structure() for entry in valid_listings}

    for entry in all_data:
        if entry[0] in full_reservation_data.keys():
            process_data(entry)

    with open("data/monte_carlo_reservation_dict.json", 'w') as outFile:
        json.dump(full_reservation_data, outFile)

    thesis_data.destroy_connection()
    #s dict

if __name__ == '__main__':
    main()

