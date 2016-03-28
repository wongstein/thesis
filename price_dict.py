# -*- coding: utf-8 -*-

from library import prices, database, time
import datetime
import sys
import json

#listing_id: {"daily_default": None, "weekend_increase":, "currency_id":, "end_date"}
most_recent_prices = {}
earliest_dates = {}

all_prices_calendar = {}
valid_listings = []

def get_data(custom_prices = True):
    global earliest_dates
    worldhomes_data = database.database("worldhomes")
    earliest_dates_list = worldhomes_data.get_data("SELECT `id`, `created_at` FROM `listings`")
    earliest_dates = {entry[0]: entry[1] for entry in earliest_dates_list}

    if custom_prices is True:
        query = 'SELECT `listing_id`,`date_start`, `date_end`, `rate` FROM `listing_custom_prices` WHERE date_end >= "2013-01-01" AND date_start < "2016-1-30" AND date_start > "2012-01-01" ORDER BY `date_start` ASC;'
    else:
        query = 'SELECT `id`,`rate` FROM `listings` WHERE master_id IS NULL;'
    final = worldhomes_data.get_data(query)

    worldhomes_data.destroy_connection()
    return final

'''
Converting to Euros
'''
def _convert_currency(value, currency_id):
    if currency_id == 1:
        return value
    elif currency_id == 2: #USD
        return (value * 0.896) #03/12
    elif currency_id == 3: #british pound
        return (value * 1.268)
    elif currency_id == 4: #russian rubble
        return (value * 0.0128)
    elif currency_id == 5:
        print "do we really have to convert currency = 5?"

'''
checks a date to see if a weekend price should be applied
returns true if the day is a weekend, false if it is not.
weekend prices applied to: friday night and saturday night.
'''
def _check_weekday(date):
    day = date.weekday()

    if day in [4,5]:
        return True
    else:
        return False

'''
Sometimes, the database puts "N" to signify none.  We will treat this as a 0
'''
def _check_int_string(value):
    try:
        return int(value)
    except Exception as e:
        return 0


def check_table_to_truncate(database_object, day, tables_truncated): #item is the specific date entry
    table_name = "price_" + day.strftime("%Y")

    if table_name not in tables_truncated:
        database_object.clear_table(table_name)
        tables_truncated.append(table_name) #I think this is inherited
        print "truncated table ", table_name

'''
Returning non-translated currencies.  Because more likely, we're evaluating within a cluster and within a cluster
the currency should be the same.
'''
def decode_rates(prices_string):
    prices_object = prices.custom_prices(prices_string)

    default_daily = _check_int_string(prices_object.get_dict_value("daily_default"))
    weekend_increase = _check_int_string(prices_object.get_dict_value("weekend_increase"))
    currency_id = _check_int_string(prices_object.get_dict_value("currency_id"))

    return {"default_daily": default_daily, "weekend_increase": weekend_increase, "currency_id": currency_id}

'''
logic: assume that the none dates have the last price advertised in the system
'''
def fill_nones(listing_id, start_from_date):
    global most_recent_prices, all_prices_calendar
    #find last priced day
    try:
        temp_price = most_recent_prices[listing_id]
    except KeyError: #this is the earliest date
        return None

    if start_from_date > datetime.date(2013, 1, 1):
        still_none = True
    else:
        return

    delta_time = 1
    while(still_none):
        check_day = start_from_date + datetime.timedelta(-1 * delta_time)

        #avoid keyError so do the check_day first
        if check_day >= datetime.date(2013, 1, 1) and all_prices_calendar[listing_id][check_day.strftime("%Y")][check_day.strftime("%Y-%m-%d")] is None and check_day >= earliest_dates[listing_id].date():
            if _check_weekday: #true when weekend
                all_prices_calendar[listing_id][check_day.strftime("%Y")][check_day.strftime("%Y-%m-%d")] = _convert_currency((temp_price["default_daily"] + temp_price["weekend_increase"]), temp_price["currency_id"])
            elif check_day >= earliest_dates[listing_id]:
                all_prices_calendar[listing_id][check_day.strftime("%Y")][check_day.strftime("%Y-%m-%d")] =  _convert_currency(temp_price["default_daily"], temp_price["currency_id"])

            #increment delta
            delta_time += 1

        else:
            still_none = False



def process_entry(entry):
    global all_prices_calendar, most_recent_prices
    #`listing_id`,`date_start`, `date_end`, `rate`
    #
    #default_daily, weekend_increase, currency_id
    listing_id = entry[0]
    if listing_id not in valid_listings:
        return
    temp_price = decode_rates(entry[3])
    if temp_price['default_daily'] == 0:
        return True

    for day in time._daterange(entry[1], entry[2]):
        if day >= datetime.date(2014, 1, 1) and day <= datetime.date(2016, 1, 29):
            if _check_weekday: #true when weekend
                all_prices_calendar[listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")] = _convert_currency((temp_price["default_daily"] + temp_price["weekend_increase"]), temp_price["currency_id"])
            else:
                all_prices_calendar[listing_id][day.strftime("%Y")][day.strftime("%Y-%m-%d")] =  _convert_currency(temp_price["default_daily"], temp_price["currency_id"])

    this_try = fill_nones(listing_id, entry[1])
    if this_try is None:
        #in the case that this is the first price and it doesn't cover up to the beginning of the trianing period
        most_recent_prices[listing_id] = temp_price
        fill_nones(listing_id, entry[1])


    most_recent_prices[listing_id] = temp_price



def main():
    global all_prices_calendar, valid_listings

    all_data = get_data()

    #make structure and only do it for listing_ids that have data
    thesis_data = database.database("Thesis")
    pot_listings = thesis_data.get_data("SELECT `listing_id` FROM listing_clusters_plain")
    valid_listings = [entry[0] for entry in pot_listings]
    thesis_data.destroy_connection()

    for listing_id in valid_listings:
        all_prices_calendar[listing_id] = time.default_date_structure()

    #fill structure:
    for item in all_data:
        process_entry(item)

    #get default_rate data:
    #just id, rate
    all_data = get_data(False)

    for entry in all_data:
        listing_id = entry[0]
        if listing_id not in all_prices_calendar.keys():
            #need to get like this:
            #listing_id`,`date_start`, `date_end`, `rate`
            all_prices_calendar[listing_id] = time.default_date_structure()

            to_process = [listing_id, datetime.date(2014, 1, 1), datetime.date(2016, 1, 29), entry[1]]

            is_none = process_entry(to_process)
            if is_none is True:
                del all_prices_calendar[listing_id]

    #fill the ends of the dates and really make sure there are no 0's or None
    for listing_id, default_date_dict in all_prices_calendar.iteritems():
        fill_nones(listing_id, datetime.date(2016, 1, 29))

    #save it
    with open("data/price_dict.json", 'w') as jsonFile:
        json.dump(all_prices_calendar, jsonFile)

    print "Finished!!!  "



if __name__ == '__main__':
    main()
