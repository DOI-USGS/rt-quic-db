# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 13:58:56 2020

@author: NBOLLIG
"""
import csv
import io
import warnings

import numpy as np

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
    wells_by_time_format = True
    rows = {}

    stream = io.StringIO(file.stream.read().decode(decode), newline=None)
    csv_reader = csv.reader(stream)

    for row in csv_reader:
        if len(row) == 0:
            continue

        well_name = None
        content = None
        fluorescence_series = None

        # Set up before reading fluorescence data
        if (reading_fluor_data == False) and row[0].startswith('Well'):
            names = row[2:]  # cache names if in time x wells format

        if (reading_fluor_data == False) and row[1].startswith('Time'):
            reading_fluor_data = True
            # Applies to format with wells x time
            if row[2] == '0':
                time_s_vals = row[2:]
                del names
            # Applies to format with time x wells
            else:
                wells_by_time_format = False
                time_s_vals = []
                contents = row[2:]
                table = []
            continue  # skip to next row

        # When reading fluorescence data
        if (reading_fluor_data == True):
            if wells_by_time_format == True:
                well_name = row[0]
                content = row[1]
                fluorescence_series = row[2:]
                rows[well_name] = [content, fluorescence_series]
            else:
                time_s_vals.append(row[1])
                table.append(row[2:])

    # Post-formatting for time x wells format
    if wells_by_time_format == False:
        table = np.array(table)

        for j in range(table.shape[1]):
            rows[names[j]] = [contents[j], list(table[:, j])]

    # Get implied dimensions from the formatting of well name
    print(rows.keys())
    implied_dims = compute_implied_dimensions(rows.keys())

    print(implied_dims)
    return rows, time_s_vals, implied_dims


def compute_implied_dimensions(well_names_list):
    """
    Input:
      well_names_list - a list of well names

    Returns:
      implied dimensions as a tuple [according to specifications below]

    Option 1: If row names follow the typical convention of 'A01', 'A02', ..., 'B01', ...,
    then we can infer a dimensions across the plate's row axis (number of alphabetic
    characters prefixed to each well name) and across the plates column axis (number of
    numeric values following the alphabetic character). The tuple length will then
    be 2 as (num of rows on plate, num of cols on plate).

    Option 2: The row names may not follow the typical convention. In that case, we cannot
    infer the 2-dimensional layout of plate. The tuple is of length 1 and
    represents the flattened dimension, like (num of rows on plate * num of cols on plate,).

    Returns a warning if well names follow Option 1 but some data is missing from the implied grid.
    """
    implied_grid = True  # boolean indicating if the well name list implies a grid by using alpha-numeric format
    last_row = ''
    last_col = 0

    row_labels = set()  # a set of alphabetic row labels
    col_labels = set()  # a set of numeric column labels

    # Check alphanumeric pattern (alpha + number) of well names to determine if plate grid is implied
    for well_name in well_names_list:
        alpha, num = well_name[:1], well_name[1:]
        if not alpha.isalpha() or not num.isnumeric():
            implied_grid = False
            break
        # Keep track of highest row label and highest column label
        if alpha.upper() > last_row:
            last_row = alpha
        if int(num) > last_col:
            last_col = int(num)

        # Put labels into a set
        row_labels.add(alpha.upper())
        col_labels.add(int(num))

    # Throw warning if there is an implied grid but some data is missing

    if implied_grid:
        if len(row_labels) * len(col_labels) != len(well_names_list):
            warnings.warn(
                "While parsing a .CSV file, a plate grid is implied by alphanumeric well names, but not all rows or columns are found.")
    # Compute implied dimensions
    if implied_grid:
        return (len(row_labels), len(col_labels))
    else:
        return (len(well_names_list),)


"""
Class for creating .csv that will be directly used to upload data into the Observation table.
"""


class UploadObsCSV:

    def __init__(self):
        self.rows = []
        header = ['fluorescence', 'time_s', 'x_coord', 'y_coord', 'wc_ID', 'index_in_well']
        self.rows.append(header)

    def add_observation(self, data, well_data, obs_data):
        fluorescence = obs_data['fluorescence']
        time_s = obs_data['time_s']
        x_coord = obs_data['x_coord']
        y_coord = obs_data['y_coord']
        wc_ID = well_data['wc_ID']
        index_in_well = obs_data['index_in_well']

        new_row = [fluorescence, time_s, x_coord, y_coord, wc_ID, index_in_well]
        self.rows.append(new_row)

    def write_csv(self, path='temp_observation_load.csv'):
        with open(path, 'w', newline='') as file:
            wr = csv.writer(file, quoting=csv.QUOTE_ALL)
            for row in self.rows:
                wr.writerow(row)
        return file


"""
Class for creating .csv that will be directly used to upload data into the Well_Condition table.
"""


class UploadWellConditionCSV:

    def __init__(self):
        self.rows = []
        header = ['wc_ID', 'salt_type', 'salt_conc', 'substrate_type', 'substrate_conc', 'sample_conc',
                  'surfact_type', 'surfact_conc', 'other_wc_attr', 'sample_ID', 'assay_ID', 'contents', 'well_name']
        self.rows.append(header)

    def add_record(self, data):
        wc_ID = data['wc_ID']
        salt_type = data['salt_type']
        salt_conc = data['salt_conc']
        substrate_type = data['substrate_type']
        substrate_conc = data['substrate_conc']
        sample_conc = data['sample_conc']
        surfact_type = data['surfact_type']
        surfact_conc = data['surfact_conc']
        other_wc_attr = data['other_wc_attr']
        sample_ID = data['sample_ID']
        assay_ID = data['assay_ID']
        contents = data['contents']
        well_name = data['well_name']

        new_row = [wc_ID, salt_type, salt_conc, substrate_type, substrate_conc, sample_conc,
                   surfact_type, surfact_conc, other_wc_attr, sample_ID, assay_ID, contents, well_name]
        self.rows.append(new_row)

    def write_csv(self, path='temp_wc_load.csv'):
        with open(path, 'w', newline='') as file:
            wr = csv.writer(file, quoting=csv.QUOTE_ALL)
            for row in self.rows:
                wr.writerow(row)
        return file
