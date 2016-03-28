# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:54:36 2016

@author: AmeeWongstein
"""
import sys

class custom_prices():
    price_dict = {}

    def __init__(self, sample):
        self.make_dict(sample)

    def make_split(self, whole_first, char):

        if isinstance(whole_first, list):
            final = []
            for item in whole_first:
                final.append(item.split(char))
            return final
        elif isinstance(whole_first, str):
            return whole_first.split(char)



    def make_dict(self, sample):
        first_split = sample.split("{")
        second_split = self.make_split(first_split, '\"')
        good_stuff = self.make_split(second_split[2],';')
        #print good_stuff

        for x in range(2,len(good_stuff)-1):
            if len(good_stuff[x]) == 1: #this is a title name
                #print "here is potential_value"
                #print good_stuff[x+1][1], " ", type(good_stuff[x+1][1])
                try:
                    potential_value = self.make_split(good_stuff[x+1][1], ':')
                except Exception as e:
                    print e
                    print good_stuff[x+1]
                    sys.exit()

                #print potential_value
                if len(potential_value) == 1:
                    self.price_dict[good_stuff[x][0]] = potential_value[0]
                else:
                    self.price_dict[good_stuff[x][0]] = potential_value[1]
            #else:
             #   print good_stuff[x]

    def get_item(self, item_name):
        return price_dict[item_name]

    def get_dict_keys(self):
        return self.price_dict.keys()

    def get_dict_value(self, key_name):
        try:
            return self.price_dict[key_name]
        except Exception as e:
            print "This key doesn't exist in the price dict, ", key_name



'''if __name__ == '__main__':
    sample = 'C:18:"Vreasy\Models\Rate":398:{a:14:{s:7:"version";d:0.10000000000000001;s:16:"security_deposit";N;s:11:"currency_id";i:1;s:13:"daily_default";d:130;s:14:"weekly_default";d:0;s:15:"monthly_default";d:0;s:16:"weekend_increase";N;s:12:"minimum_stay";i:1;s:12:"maximum_stay";i:30;s:16:"extra_person_fee";i:0;s:31:"extra_person_fee_trigger_amount";i:1;s:17:"late_checkout_fee";N;s:16:"late_checkin_fee";N;s:17:"early_checkin_fee";N;}}'

    new_price = custom_prices(sample)
    print new_price.get_dict_keys()
'''
