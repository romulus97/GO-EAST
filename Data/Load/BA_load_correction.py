# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 12:16:00 2021

@author: kakdemi
"""

import pandas as pd
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt

#importing BA load data
load_data = pd.read_csv('BA_load.csv',header=0)
del load_data['Unnamed: 0']
load_data = load_data.fillna(0)

#reindexing BA load data and getting the BA names
hours_2019 = pd.date_range(start='1-1-2019 00:00:00',end='12-31-2019 23:00:00', freq='H')
load_data.index = hours_2019
BAs = list(load_data.columns)

#searching for a valid demand value by looking at 1 day before and after. If not available, the algorithm continues to look for a valid value up to 30 days before or after
for BA in BAs:
    
    for time in hours_2019:
        
        load_val = load_data.loc[time,BA]
        
        if load_val <= 0:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,31):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = load_data.loc[day_before,BA]
                    if new_val > 0:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = load_data.loc[day_after,BA]
                        if new_val > 0:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            

#checking whether there are still zero demand values or invalid values
if 0 in load_data.values or load_data.isna().sum().sum() != 0:
    print('There are still missing values.')
else:
    print('Data is filled successfully.')
    
#filtering out anomalies (really high and low values) from the data, replacing them with values from a different day but at the same hour
for BA in BAs:
    
    for time in hours_2019:
        
        load_val = load_data.loc[time,BA]
        
        time_before = time - timedelta(days=7)
        time_after = time - timedelta(days=7)
        max_load_before = load_data.loc[time_before:time - timedelta(days=1),BA].max()
        max_load_after = load_data.loc[time:time + timedelta(days=1),BA].max()
        
        min_load_before = load_data.loc[time_before:time - timedelta(days=1),BA].min()
        min_load_after = load_data.loc[time:time + timedelta(days=1),BA].min()
        
        if load_val > 1.2*max_load_before or load_val > 1.2*max_load_after:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,6):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = load_data.loc[day_before,BA]
                    if new_val <= max_load_before or new_val <= max_load_after:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = load_data.loc[day_after,BA]
                        if new_val <= max_load_before or new_val <= max_load_after:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            
        elif load_val < 0.8*min_load_before or load_val < 0.8*min_load_after:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,6):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = load_data.loc[day_before,BA]
                    if new_val >= min_load_before or new_val >= min_load_after:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = load_data.loc[day_after,BA]
                        if new_val >= min_load_before or new_val >= min_load_after:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            
        else:
            pass
        
#exporting corrected data
load_data.to_csv('BA_load_corrected.csv')


