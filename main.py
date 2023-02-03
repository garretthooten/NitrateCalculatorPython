#import datamap
import maphandler
import time

my_crop_maps = ["Input/1994_crops.csv", "Input/2004_crops.csv", "Input/2009_crops.csv", "Input/2014_crops.csv", "Input/2015_crops.csv", "Input/2016_crops.csv","Input/2017_crops.csv", "Input/2018_crops.csv"]
mh = maphandler.MapHandler(travel_time = "Input/travel_time.csv", recharge_in = "Input/recharge_in.csv", lookup_table = "Input/Lookup_Table.csv", crop_maps = my_crop_maps)

start_time = time.perf_counter()
new_map = mh.calculate_new_map(2019)
stop_time = time.perf_counter()

print("calculate_new_map done in " + str(stop_time - start_time))

new_map.write_to_file("OUTPUT.csv")

print("Done!")


