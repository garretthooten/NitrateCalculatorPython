import datamap

class MapHandler:
    
    #   Initial user input
    #   Stores crop maps as [year] = DataMap
    crop_maps = dict()
    #   Stores constant maps as ["type"] = DataMap
    constant_maps = dict()

    #   Step 0: Create MapHandler and ingest relevant datamaps
    #   Input maps with directory paths, e.g. travel_time = "Input/travel_time2019.csv"
    #   Constructor should use each path to create a datamap object  
    def __init__(self, **kwargs):
        print("creating map handler")
        
        #   load constant maps, if given
        self.load_constant_map(**kwargs)
        #   load crop maps, if given
        if "crop_maps" in kwargs:
            self.load_crop_maps(kwargs.get("crop_maps"))
            

    #   Call at any time to load or reload constant maps
    def load_constant_map(self, **kwargs):
        args_to_get = ["travel_time", "recharge_in", "lookup_table"]
        for arg in args_to_get:
            if arg in kwargs:
                if arg == "travel_time":
                    self.constant_maps[arg] = datamap.DataMap(kwargs.get(arg), travel_time = True)
                elif arg == "lookup_table":
                    self.constant_maps[arg] = datamap.DataMap(kwargs.get(arg), lookup_table = True)
                else:
                    self.constant_maps[arg] = datamap.DataMap(kwargs.get(arg))
        
    #   Call at any time to load or reload crop maps
    def load_crop_maps(self, crop_directories):
        for directory in crop_directories:
                year = "".join(filter(str.isdigit, directory))
                year = int(year)
                self.crop_maps[year] = datamap.DataMap(directory)
                print("ncols for " + str(year) + " is " + str(self.crop_maps[year].ncols))

    #   Step 1: Find smallest map in the set based on total land covered
    #   get_land_covered returns the area of a given datamap.
    def get_land_covered(self, dm):
        return int(dm.cellsize) * int(dm.ncols) * int(dm.nrows)
    
    #   find_smallest_map searches through all constant and crop maps to find the smallest map and returns it.
    def find_smallest_map(self):
        print("Entering find_smallest_map")
        
        #   Start with smallest_map as travel_time, just to get started
        smallest_map = self.constant_maps["travel_time"]
        smallest_area = self.get_land_covered(smallest_map)

        for key, map in ({**self.constant_maps, **self.crop_maps}).values:
            if not key == "lookup_table":    
                if self.get_land_covered(map) < smallest_area:
                    smallest_area = self.get_land_covered(map)
                    smallest_map = map
        return smallest_map

    #   Step 2: Make all maps start at same coordinates
    def get_same_coords(self, smallest_map, maps_to_shrink):
        print("Entering get_same_coords")
        try:
            for map in maps_to_shrink:
                if not map == self.constant_maps["lookup_table"]:
                    if smallest_map.xllcorner > map.xllcorner and smallest_map.yllcorner > map.yllcorner:
                        units = map.cellsize / smallest_map.cellsize
                        new_map = []
                        starting_x = (smallest_map.xllcorner - map.xllcorner) / map.cellsize
                        starting_y = (smallest_map.yllcorner - map.yllcorner) / map.cellsize

                        for i in range(starting_x, map.nrows):
                            temp_row = []
                            for j in range(starting_y, map.ncols):
                                temp_row.append(map.get_value[i, j])
                            new_map.append(temp_row)
                        map = datamap.DataMap(new_map, smallest_map.xllcorner, smallest_map.yllcorner, map.cellsize, map.NODATA_VALUE, map.is_travel_time, map.is_lookup_table)
                    elif smallest_map.xllcorner == map.xllcorner and smallest_map.yllcorner == map.yllcorner:
                        print("Maps already at same coordinates, skipping")
        except Exception as exc:
            print("Error in get_same_coords:")
            print(type(exc))
            print(exc)

    #   Gets the average of a cell when the cellsize between two maps is different.
    def get_adj_cell(map1, map2, i, j):
        units = map2.cellsize / map1.cellsize
        return map2.stored_map[i / units][j / units]


    #   Step 3: Find smallest map of new adjusted set. In the python version the maps are adjusted in place...
    #   so you just call find_smallest_map again.

    #   Step 4: Calculate within smallest map
    #   This is the function the main program should call after loading all appropriate maps into the class.
    #   This function will go through all the steps created above, in addition to calculating the new map.
    #   Input the year which
    def calculate_new_map(self, year):

        #   Step 1: Find smallest map.
        smallest_map = self.find_smallest_map()
        print("Found smallest map")

        #   Step 2: Make all maps begin at the smallest coordinates.
        self.get_same_coords(smallest_map, self.constant_maps)
        self.get_same_coords(smallest_map, self.crop_maps)

        #   Step 3: Find the smallest map of the adjusted set.
        smallest_map = self.find_smallest_map()

        #   Step 4: Calculate within the smallest map.
        crop_value = None
        sum_of_MgN = 0
        sum_of_volume = 0
        return_map = []

        tt_units = self.constant_maps["travel_time"].cellsize / smallest_map.cellsize
        recharge_units = self.constant_maps["recharge_in"].cellsize / smallest_map.cellsize

        for i in range(len(smallest_map.stored_map)):
            inside_temp = []
            for j in range(len(smallest_map.stored_map[i])):
                temp = self.constant_maps["travel_time"].get_value(i,j)

                if not temp == self.constant_maps["travel_time"].NODATA_VALUE:
                    access = int(year) - int(temp)
                    crop_value = self.crop_maps[access].get_value(i,j)

                    if not crop_value in self.constant_maps["lookup_table"].stored_map:
                        crop_value = self.crop_maps[access].NODATA_VALUE
                    
                    current_recharge_cell = self.get_adj_cell(smallest_map, self.constant_maps["recharge_in"], i, j)

                    if ((not crop_value == self.crop_maps[access].NODATA_VALUE) and (self.constant_maps["lookup_table"].stored_map[crop_value].size == 3) and (not current_recharge_cell == self.constant_maps["recharge_in"].NODATA_VALUE)):
                        area = self.crop_maps[access].cellsize ** 2
                        m3_per_day = (current_recharge_cell * .0254 * area) / 365
                        concentration = float(self.constant_maps["lookup_table"][2])
                        volume = m3_per_day * 1000
                        mg_nitrate = volume * concentration
                        kgn_year = mg_nitrate * 365 * (10 ** -6)
                        sum_of_MgN += mg_nitrate
                        sum_of_volume += volume
                        inside_temp.append(kgn_year)

                    else:
                        inside_temp.append(smallest_map.NODATA_VALUE)

                else:
                    inside_temp.append(smallest_map.NODATA_VALUE)

            return_map.append(inside_temp)

        print("Exited calculation loop with nrows: " + str(len(return_map)) + " and ncols: " + str(len(return_map[0])))
        print("sum_of_MgN: " + str(sum_of_MgN) + "\nsum_of_volume: " + str(sum_of_volume))
