# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 23:07:39 2024

@author: jkern
"""

import pandas as pd

fromba = []
toba = []
connections = []
max_flows = []
min_flows = []

for j in [2019,2020,2021,2022,2023]:
    
    fn = 'exchange time series' + str(j) + '.csv'

    df = pd.read_csv(fn,header=0)    
    
    for i in range(len(df)):
        
        c = df.loc[i,'fromba'] + '_' + df.loc[i,'toba']
        
        if c in connections:
        
            pass
        
        else:
                
            connections.append(c)
            fromba.append(df.loc[i,'fromba'])
            toba.append(df.loc[i,'toba'])

import numpy as np

min_flows = np.ones((len(connections),1))*10000
max_flows = np.ones((len(connections),1))*-10000

for j in [2019,2020,2021,2022,2023]:
    
    fn = 'exchange time series' + str(j) + '.csv'

    df = pd.read_csv(fn,header=0)    
            
    for i in range(len(connections)):
        
        f = fromba[i]
        t = toba[i]
        
        sample = df.loc[(df['fromba']==f) & (df['toba']==t),'value']
        
        if len(sample) > 0:
            
            mx = max(sample)
            mn = min(sample)
            
            if j == 2019:
                
                min_flows[i] = mn
                max_flows[i] = mx
            
            else:
                
                if min_flows[i] > mn:
                    min_flows[i] = mn
                
                if max_flows[i] < mx:
                    max_flows[i] = mx

for i in range(len(max_flows)):
    max_flows[i] = max(0,max_flows[i])
    
df_out = pd.DataFrame()
df_out['fromba'] = fromba
df_out['toba'] = toba
df_out['max'] = max_flows
df_out.to_csv('BA_to_BA_max_flows.csv',index=None)

### max flows for EIC only

df_max_flows = pd.read_csv('BA_to_BA_max_flows.csv',header=0) 
df = pd.read_csv('BA_to_BA_transmission_matrix_TEST.csv',header=0)

connections = list(df['Exchange'])

idx = []

for i in range(len(df_max_flows)):
    c = df_max_flows.loc[i,'fromba'] + '_' + df_max_flows.loc[i,'toba']
    
    if c in connections:
        
        idx.append(i)
        
EIC_max_flows = df_max_flows.loc[idx,:]
EIC_max_flows.to_csv('EIC_BA_to_BA_max_flows.csv',index=None)
        