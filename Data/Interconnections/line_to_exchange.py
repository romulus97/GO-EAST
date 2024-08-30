# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 15:31:26 2024

@author: jkern
"""

import pandas as pd
import re
import numpy as np

line_to_bus = pd.read_csv('../../line_to_bus.csv',header=0)

nodes_to_BA = pd.read_csv('nodes_to_BA_state.csv',header=0)

lines = list(line_to_bus['line'])

BAs = pd.read_csv('../../BAs_tell.csv',header=0)
# BA_names_upper = []
# for i in BAs['Name']:
#     BA_names_upper.append(i.upper())

exchange_dict = {}
exchange_list = []

for i in lines:
    
    idx = lines.index(i)
    origin = line_to_bus.loc[idx,line_to_bus.loc[idx,:]==1].index[0]
    destination = line_to_bus.loc[idx,line_to_bus.loc[idx,:]==-1].index[0]
    
    origin_num = int(re.search("\d+", origin)[0])
    destination_num = int(re.search("\d+", destination)[0])
    
    origin_BA = nodes_to_BA.loc[nodes_to_BA['Number']==origin_num,'NAME'].values[0]
    destination_BA = nodes_to_BA.loc[nodes_to_BA['Number']==destination_num,'NAME'].values[0]
    
    if origin_BA == destination_BA:
        pass
    elif origin_BA not in list(BAs['Name']):
        pass
    elif destination_BA not in list(BAs['Name']):
        pass
    
    else:
        origin_abbr = BAs.loc[BAs['Name'] == origin_BA,'Abbreviation'].values[0]
        destination_abbr = BAs.loc[BAs['Name'] == destination_BA,'Abbreviation'].values[0]
        
        exchange = origin_abbr + '_' + destination_abbr
        
        if exchange in exchange_list:
            exchange_dict[exchange] += [i]
            
        else:
            exchange_list.append(exchange)
            exchange_dict[exchange] = [i]
        

z = np.zeros((len(exchange_list),len(lines)+1))
df = pd.DataFrame(z)
df.columns = ['Exchange'] + lines
df['Exchange'] = exchange_list

for e in exchange_list:
    
    e_index = exchange_list.index(e)
    L = exchange_dict[e]
    
    if len(L) < 1:
        pass
    else:
        
    
        for l in L:
            
            df.loc[e_index,l] = 1
        
df.to_csv('BA_to_BA_transmission_matrix_TEST.csv',index=None)
        


        