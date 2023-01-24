import csv
import numpy as np

class DataMap:
    directory = ""
    stored_map = None
    ncols = 0
    nrows = 0
    xllcorner = 0.0
    yllcorner = 0.0
    cellsize = 0
    NODATA_VALUE = 0

    successfully_created = False
    is_travel_time = False
    is_lookup_table = False

    def __init__(self, file_path, **kwargs):
        self.directory = file_path
        self.parse_csv(file_path)
        if "travel_time" in kwargs:
            self.is_travel_time = kwargs.get("travel_time")
            print("travel time set: " + str(self.is_travel_time))
        if "lookup_table" in kwargs:
            self.is_lookup_table = kwargs.get("lookup_table")
            print("lookup table set: " + str(self.is_lookup_table))
        if self.is_lookup_table and self.is_travel_time:
            print("ERROR: Invalid desingation of travel time and lookup table. Map invalid")
    
    def parse_csv(self, file_path):
        #   load file to stored_map
        with open(file_path, newline='') as file:
            self.stored_map = list(csv.reader(file))
        #   get parameters from stored_map into variables
        if not self.is_lookup_table:
            self.ncols = self.stored_map[0][1]
            self.nrows = self.stored_map[1][1]
            self.xllcorner = self.stored_map[2][1]
            self.yllcorner = self.stored_map[3][1]
            self.cellsize = self.stored_map[4][1]
            self.NODATA_VALUE = self.stored_map[5][1]
            #   Slice stored_map to get rid of extra parameter data
            self.stored_map = self.stored_map[6:]
        #print("ncols: " + ncols + "\nnrows: " + nrows + "\nxllcorner: " + xllcorner + "\nyllcorner: " + yllcorner + "\ncellsize: " + cellsize + "\nNODATA_VALUE: " + NODATA_VALUE)

        

    def __str__(self):
        if not self.is_lookup_table:
            return "ncols: " + str(self.ncols) + "\nnrows: " + str(self.nrows) + "\nxllcorner: " + str(self.xllcorner) + "\nyllcorner: " + str(self.yllcorner) + "\ncellsize: " + str(self.cellsize) + "\nNODATA_VALUE: " + str(self.NODATA_VALUE)
        else:
            return str(self.stored_map)