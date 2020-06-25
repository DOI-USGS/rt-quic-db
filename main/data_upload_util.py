# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 13:58:56 2020

@author: NBOLLIG
"""
import csv
import io

"""
Parse file into a dictionary of the following format:
    rows[well_name] = [content, fluorescence_series]

where content is a string and fluorescence_series is an array parallel to array of times time_s_vals.

Returns:
    rows
    time_s_vals
"""
def parse_rt_quic_csv(file, decode="UTF8"):
    reading_fluor_data = False
    rows = {}
    
    stream = io.StringIO(file.stream.read().decode(decode), newline=None)
    csv_reader = csv.reader(stream)
    
    for row in csv_reader:
        well_name = None
        content = None
        fluorescence_series = None
        
        if (reading_fluor_data == True):
            well_name = row[0]
            content = row[1]
            fluorescence_series = row[2:]
            rows[well_name] = [content, fluorescence_series]
            
        if (reading_fluor_data == False) and row[1] == 'Time [sec]':
            time_s_vals = row[2:]
            reading_fluor_data = True
            
    return rows, time_s_vals
    