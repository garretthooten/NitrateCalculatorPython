#import datamap
import maphandler

my_crop_maps = ["Input/1994_crops.csv", "Input/2004_crops.csv", "Input/2009_crops.csv", "Input/2014_crops.csv", "Input/2015_crops.csv", "Input/2016_crops.csv","Input/2017_crops.csv", "Input/2018_crops.csv"]
mh = maphandler.MapHandler(travel_time = "Input/travel_time.csv", recharge_in = "Input/recharge_in.csv", lookup_table = "Input/Lookup_Table.csv", crop_maps = my_crop_maps)

mh.calculate_new_map(2019)
