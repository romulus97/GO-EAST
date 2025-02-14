# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import math
import numpy as np
import os
import xlrd
from shutil import copy
from pathlib import Path

########################################
# LOAD ALLOCATION FROM BALANCING AUTHORITY to NODES
########################################

base_dir = 'Data'

df_load = pd.read_csv(os.path.join(base_dir, 'Load/BA_load_corrected.csv'), header=0, index_col=0)
df_BAs = pd.read_csv(os.path.join(base_dir, 'Interconnections/BAs_full.csv'), header=0)
BAs = list(df_BAs['Name'])


df_full = pd.read_csv(os.path.join(base_dir, 'Interconnections/nodes_to_BA_state.csv'), header=0,index_col=0)
df_full = df_full.reset_index(drop=True)

full_available = list(df_full['Number'])

df_wind = pd.read_csv(os.path.join(base_dir, 'Gen/BA_wind.csv'), header=0,index_col=0)
df_solar = pd.read_csv(os.path.join(base_dir, 'Gen/BA_solar_corrected.csv'), header=0,index_col=0)
df_hydro = pd.read_csv(os.path.join(base_dir, 'Gen/BA_hydro_corrected.csv'), header=0,index_col=0)

BA_to_BA_transmission_data = pd.read_csv('Data/Interconnections/EIC_BA_to_BA_max_flows.csv',header=0)
all_BA_BA_connections = []
for i in range(len(BA_to_BA_transmission_data)):
    a = BA_to_BA_transmission_data.loc[i,'fromba']
    b = BA_to_BA_transmission_data.loc[i,'toba']
    c = a+'_'+b
    all_BA_BA_connections.append(c)
BA_to_BA_transmission_data['Exchange'] = all_BA_BA_connections

#NODE_NUMBER = [500,525,550,575,600,625,650,675,700]
NODE_NUMBER = [500]     # 2 pieces

# UC_TREATMENTS = ['_simple','_coal']
UC_TREATMENTS = ['_simple']

#trans_p = [25, 50 ,75 ,100, 200, 300, 400, 500]
trans_p = [25]

sections = [1]

for section in sections:
    
    for NN in NODE_NUMBER:
        
        for UC in UC_TREATMENTS:
            
            for T_p in trans_p:
                        
                path=str(Path.cwd()) + str(Path('/Exp' + str(NN) + UC + '_' + str(T_p) + '_' + str(section)))
                os.makedirs(path,exist_ok=True)
                
                T_p = T_p/100
                
                FN = 'reduced_network/Results_' + str(NN) + '.xlsx'
             
                # selected nodes
                df_selected = pd.read_excel(os.path.join(base_dir, FN), sheet_name = 'Bus', header=0)
                buses = list(df_selected['bus_i'])
                
                # pull selected nodes out of 
                selected_BAs = []
                for b in buses:
                    BA = df_full.loc[df_full['Number']==b,'NAME']
                    BA = BA.reset_index(drop=True)
                    selected_BAs.append(BA[0])
                
                df_selected['BA'] = selected_BAs
                    
                # calculate nodal weights within each BA
                
                BA_totals = []
                for b in BAs:
                    sample = list(df_selected.loc[df_selected['BA']==b,'Pd'])
                    corrected = [0 if x<0 else x for x in sample]
                    BA_totals.append(sum(corrected))
                
                BA_totals = np.column_stack((BAs,BA_totals))
                df_BA_totals = pd.DataFrame(BA_totals)
                df_BA_totals.columns = ['Name','Total']
                
                weights = []
                for i in range(0,len(df_selected)):
                    area = df_selected.loc[i,'BA']
                    if df_selected.loc[i,'Pd'] <0:
                        weights.append(0)
                    else:        
                        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                        W = (df_selected.loc[i,'Pd']/X)
                        weights.append(W)
                df_selected['BA Load Weight'] = weights
                
                idx = 0
                w= 0
                T = np.zeros((8760,len(buses)))
                
                for i in range(0,len(df_selected)):
                        
                    #load for original node
                    name = df_selected.loc[i,'BA']
                    
                    if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                        pass
                    else: 
                    
                        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                        weight = df_selected.loc[i,'BA Load Weight']
                        # T[:,i] = T[:,i] + np.reshape(df_load[abbr].values*weight,(8760,))
                        if max(df_load[abbr]) < 1:
                            T[:,i] = T[:,i] + np.reshape(df_load[abbr].values,(8760,))                    
                        else:                    
                            T[:,i] = T[:,i] + np.reshape(df_load[abbr].values*weight,(8760,)) 
                    
                for i in range(0,len(buses)):
                    buses[i] = 'bus_' + str(buses[i])
                
                df_C = pd.DataFrame(T)
                df_C.columns = buses
                df_C.to_csv('nodal_load.csv',index=None)   
                
                copy('nodal_load.csv',path)
                
                #############
                # GENERATORS
                           
                #get rid of NaNs
                a = df_wind.values
                m=np.where(np.isnan(a))
                r,c=np.shape(m)
                for i in range(0,c):
                    df_wind.iloc[m[0][i],m[1][i]] = 0
                a = df_solar.values
                m=np.where(np.isnan(a))
                r,c=np.shape(m)
                for i in range(0,c):
                    df_solar.iloc[m[0][i],m[1][i]] = 0    
                a = df_hydro.values
                m=np.where(np.isnan(a))
                r,c=np.shape(m)
                for i in range(0,c):
                    df_hydro.iloc[m[0][i],m[1][i]] = 0   
                
                # read reduction algorithm summary and parse nodal operations
                df_summary = pd.read_excel(os.path.join(base_dir, FN), sheet_name='Summary', header=6)
                # df_summary = df_summary.drop([len(df_summary)-1])
                nodes=0
                merged = {}
                N = []
                for i in range(0,len(df_summary)):
                    test = df_summary.iloc[i,0]
                    res = [int(i) for i in test.split() if i.isdigit()] 
                    if res[1] in N:
                        pass
                    else:
                        N.append(res[1])
                for n in N:
                    k = []
                    for i in range(0,len(df_summary)):
                        test = df_summary.iloc[i,0]
                        res = [int(i) for i in test.split() if i.isdigit()] 
                        if res[1] == n:
                            k.append(res[0])
                        else:
                            pass
                        
                    merged[n] = k
                
                ##################################
                # WIND ALLOCATION FROM BA TO NODE
                           
                df_gen = pd.read_csv(os.path.join(base_dir, 'Gen/Generators_EIA.csv'), header=0)
                MWMax = []
                fuel_type = []
                nums = list(df_gen['BusNum'])
                
                #add gen info to df
                for i in range(0,len(df_full)):
                    bus = df_full.loc[i,'Number']
                    if bus in nums:
                        MWMax.append(df_gen.loc[df_gen['BusNum']==bus,'MWMax'].values[0])
                        fuel_type.append(df_gen.loc[df_gen['BusNum']==bus,'FuelType'].values[0])
                    else:
                        MWMax.append(0)
                        fuel_type.append('none')
                
                df_full['MWMax'] = MWMax
                df_full['FuelType'] = fuel_type
                
                BA_totals = []
                
                for b in BAs:
                    sample = list(df_full.loc[(df_full['NAME']==b) & (df_full['FuelType'] == 'WND (Wind)'),'MWMax'])
                    # corrected = [0 if math.isnan(x) else x for x in sample]
                    BA_totals.append(sum(sample))
                
                BA_totals = np.column_stack((BAs,BA_totals))
                df_BA_totals = pd.DataFrame(BA_totals)
                df_BA_totals.columns = ['Name','Total']
                
                weights = []
                for i in range(0,len(df_full)):
                    area = df_full.loc[i,'NAME']
                    if str(area) in BAs:
                        if str(df_full.loc[i,'FuelType']) != 'WND (Wind)':
                            weights.append(0)
                        else:
                            X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                            W = df_full.loc[i,'MWMax']/X
                            weights.append(W)
                    else:
                        weights.append(0)
                        
                df_full['BA Wind Weight'] = weights
                
                sums = []
                for i in BAs:
                    s = sum(df_full.loc[df_full['NAME']==i,'BA Wind Weight'])
                    sums.append(s)
                
                # selected nodes
                # df_selected = pd.read_csv('reduced_buses.csv',header=0)
                buses = list(df_selected['bus_i'])
                
                idx = 0
                w= 0
                T = np.zeros((8760,len(buses)))
                
                BA_sums = np.zeros((len(BAs),1))
                BA_test = np.zeros((len(BAs),1))
                
                counter = 0
                
                for b in buses:
                    
                    #load for original node
                    sample = df_full.loc[df_full['Number'] == b]
                    sample = sample.reset_index(drop=True)
                    name = sample['NAME'][0]
                    
                    if str(name) in BAs:
                        
                        if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                            pass
                        else:
                            abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                            weight = sample['BA Wind Weight'].values[0]
                            T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight,(8760,))
                            w += weight
                            dx = BAs.index(name)
                            BA_sums[dx] = BA_sums[dx] + weight
                            BA_test[dx] += sum(df_wind[abbr].values*weight)
                            counter+=1
                        
                    else:
                        pass
                              
                    #add wind capacity from merged nodes
                    try:
                        m_nodes = merged[b]
                        counter+=len(m_nodes)
                        
                        for m in m_nodes:
                            
                            sample = df_full.loc[df_full['Number'] == m]
                            sample = sample.reset_index(drop=True)
                            name = sample['NAME'][0]
                            if str(name) in BAs:
                                
                                if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                                    pass
                                else:
                                    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                    weight = sample['BA Wind Weight']
                                    w += weight  
                                    dx = BAs.index(name)
                                    BA_sums[dx] = BA_sums[dx] + weight
                                    BA_test[dx] += sum(df_wind[abbr].values*weight.values[0])
                                    T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight.values[0],(8760,))
                            else:
                                pass
                
                    except KeyError:
                        # print (b)
                        pass
                    
                    idx +=1
                
                w_buses = []
                for i in range(0,len(buses)):
                    w_buses.append('bus_' + str(buses[i]))
                
                df_C = pd.DataFrame(T)
                df_C.columns = w_buses
                df_C.to_csv('nodal_wind.csv',index=None)   
                copy('nodal_wind.csv',path)
                
                
                ##################################
                # SOLAR ALLOCATION FROM BA TO NODE
                
                #### NOTE: TAMU DATASET DOES NOT INCLUDE ANY WIND IN: BANC, LADWP OR PSCO; EIA VALUES
                # FOR THESE BAs WERE MANUALLY ADDED TO CAISO AND WACM IN THE BA_wind.csv FILE.
                
                BA_totals = []
                
                for b in BAs:
                    sample = list(df_full.loc[(df_full['NAME']==b) & (df_full['FuelType'] == 'SUN (Solar)'),'MWMax'])
                    # corrected = [0 if math.isnan(x) else x for x in sample]
                    BA_totals.append(sum(sample))
                
                BA_totals = np.column_stack((BAs,BA_totals))
                df_BA_totals = pd.DataFrame(BA_totals)
                df_BA_totals.columns = ['Name','Total']
                
                weights = []
                for i in range(0,len(df_full)):
                    area = df_full.loc[i,'NAME']
                    if str(area) in BAs:
                        if str(df_full.loc[i,'FuelType']) != 'SUN (Solar)':
                            weights.append(0)
                        else:
                            X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                            W = df_full.loc[i,'MWMax']/X
                            weights.append(W)
                    else:  
                        weights.append(0)
                        
                df_full['BA Solar Weight'] = weights
                
                sums = []
                for i in BAs:
                    s = sum(df_full.loc[df_full['NAME']==i,'BA Solar Weight'])
                    sums.append(s)
                
                # selected nodes
                # df_selected = pd.read_csv('reduced_buses.csv',header=0)
                buses = list(df_selected['bus_i'])
                
                idx = 0
                w= 0
                T = np.zeros((8760,len(buses)))
                
                BA_sums = np.zeros((len(BAs),1))
                BA_test = np.zeros((len(BAs),1))
                
                for b in buses:
                    
                    #load for original node
                    sample = df_full.loc[df_full['Number'] == b]
                    sample = sample.reset_index(drop=True)
                    name = sample['NAME'][0]
                
                    
                    if str(name) in BAs:
                        
                        if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                            pass
                        else:
                
                            abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                            weight = sample['BA Solar Weight'].values[0]
                            T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight,(8760,))
                            w += weight
                            dx = BAs.index(name)
                            BA_sums[dx] = BA_sums[dx] + weight
                            BA_test[dx] += sum(df_solar[abbr].values*weight)
                        
                    else:
                        pass
                              
                    #add solar capacity from merged nodes
                    try:
                        m_nodes = merged[b]
                        
                        for m in m_nodes:
                            #load for original node
                            sample = df_full.loc[df_full['Number'] == m]
                            sample = sample.reset_index(drop=True)
                            name = sample['NAME'][0]
                            if str(name) in BAs:
                                if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                                    pass
                                else:
                                    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                    weight = sample['BA Solar Weight']
                                    w += weight  
                                    dx = BAs.index(name)
                                    BA_sums[dx] = BA_sums[dx] + weight
                                    BA_test[dx] += sum(df_solar[abbr].values*weight.values[0])
                                    T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight.values[0],(8760,))
                            else:
                                pass
                
                    except KeyError:
                        # print (b)
                        pass
                    
                    idx +=1
                    
                
                s_buses = []
                for i in range(0,len(buses)):
                    s_buses.append('bus_' + str(buses[i]))
                
                df_C = pd.DataFrame(T)
                df_C.columns = s_buses
                df_C.to_csv('nodal_solar.csv',index=None)  
                copy('nodal_solar.csv',path)
    
                ##################################
                # HYDRO ALLOCATION FROM BA TO NODE
                
                BA_totals = []
                
                for b in BAs:
                    sample = list(df_full.loc[(df_full['NAME']==b) & (df_full['FuelType'] == 'WAT (Water)'),'MWMax'])
                    # corrected = [0 if math.isnan(x) else x for x in sample]
                    BA_totals.append(sum(sample))
                
                BA_totals = np.column_stack((BAs,BA_totals))
                df_BA_totals = pd.DataFrame(BA_totals)
                df_BA_totals.columns = ['Name','Total']
                
                weights = []
                for i in range(0,len(df_full)):
                    area = df_full.loc[i,'NAME']
                    if str(area) in BAs:
                        if str(df_full.loc[i,'FuelType']) != 'WAT (Water)':
                            weights.append(0)
                        else:    
                            X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                            W = df_full.loc[i,'MWMax']/X
                            weights.append(W)
                    else:
                        weights.append(0)
                            
                df_full['BA Hydro Weight'] = weights
                
                sums = []
                for i in BAs:
                    s = sum(df_full.loc[df_full['NAME']==i,'BA Hydro Weight'])
                    sums.append(s)
                
                # selected nodes
                # df_selected = pd.read_csv('reduced_buses.csv',header=0)
                buses = list(df_selected['bus_i'])
                
                idx = 0
                w= 0
                T = np.zeros((8760,len(buses)))
                
                BA_sums = np.zeros((len(BAs),1))
                
                for b in buses:
                    
                    #load for original node
                    sample = df_full.loc[df_full['Number'] == b]
                    sample = sample.reset_index(drop=True)
                    name = sample['NAME'][0]
                
                    
                    if str(name) in BAs:
                        if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                            pass
                        else:
                            abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                            weight = sample['BA Hydro Weight'].values[0]
                            T[:,idx] = T[:,idx] + np.reshape(df_hydro[abbr].values*weight,(8760,))
                            w += weight
                            dx = BAs.index(name)
                            BA_sums[dx] = BA_sums[dx] + weight
                        
                    else:
                        pass
                              
                    #add hydro capacity from merged nodes
                    try:
                        m_nodes = merged[b]
                        
                        for m in m_nodes:
                            #load for original node
                            sample = df_full.loc[df_full['Number'] == m]
                            sample = sample.reset_index(drop=True)
                            name = sample['NAME'][0]
                            if str(name) in BAs:
                                if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                                    pass
                                else:
                                    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                    weight = sample['BA Hydro Weight']
                                    w += weight  
                                    dx = BAs.index(name)
                                    BA_sums[dx] = BA_sums[dx] + weight
                                    T[:,idx] = T[:,idx] + np.reshape(df_hydro[abbr].values*weight.values[0],(8760,))
                            else:
                                pass
                
                    except KeyError:
                        # print (b)
                        pass
                    
                    idx +=1
                    
                
                h_buses = []
                for i in range(0,len(buses)):
                    h_buses.append('bus_' + str(buses[i]))
                
                df_C = pd.DataFrame(T)
                df_C.columns = h_buses
                df_C.to_csv('nodal_hydro.csv',index=None)  
                copy('nodal_hydro.csv',path)
                
                
                ##############################
                # THERMAL GENERATION
                
                import re
                
                df_gens = pd.read_csv(os.path.join(base_dir, 'Gen/Generators_EIA.csv'), header=0)
                df_gens = df_gens.replace('', np.nan, regex=True)
                df_gens_heat_rate = pd.read_csv(os.path.join(base_dir, 'Gen/Heat_rates_EIA.csv'), header=0)
                old_bus_num =[]
                new_bus_num = []
                NB = []
                
                old_bus_num_hr =[]
                new_bus_num_hr = []
                NB_hr = []
                
                for n in N:
                    k = merged[n]
                    for s in k:
                        old_bus_num.append(s)
                        new_bus_num.append(n)
                
                for i in range(0,len(df_gens)):
                    OB = df_gens.loc[i,'BusNum']
                    if OB in old_bus_num:
                        idx = old_bus_num.index(OB)
                        NB.append(new_bus_num[idx])
                    else:
                        NB.append(OB)
                
                df_gens['NewBusNum'] = NB
                
                for i in range(0,len(df_gens_heat_rate)):
                    OB = df_gens_heat_rate.loc[i,'BusNum']
                    if OB in old_bus_num:
                        idx = old_bus_num.index(OB)
                        NB_hr.append(new_bus_num[idx])
                    else:
                        NB_hr.append(OB)
                
                df_gens_heat_rate['NewBusNum'] = NB_hr
        
                names = list(df_gens['BusName'])
                fts = list(df_gens['FuelType'])
                names_hr = list(df_gens_heat_rate['BusName'])
                fts_hr = list(df_gens_heat_rate['BusName'])
                bus_area = list(df_gens['BusAreaName'])
                bus_area_hr = list(df_gens_heat_rate['AreaName'])
                
                # remove numbers and spaces
                for n in names:
                    i = names.index(n)
                    corrected = re.sub(r'[^A-Z]',r'',n)
                    f = fts[i]
                    bn = bus_area[i]
                    bn = bn.replace(" ", "_")
                    if f == 'NUC (Nuclear)':
                        f = 'Nuc'
                    elif f == 'NG (Natural Gas)':
                        f = 'NG'
                    elif f == 'BIT (Bituminous Coal)':
                        f = 'C'
                    elif f == 'SUN (Solar)':
                        f = 'S'
                    elif f == 'WAT (Water)':
                        f = 'H'
                    elif f == 'WND (Wind)':
                        f = 'W'
                    elif f == 'DFO (Distillate Fuel Oil)':
                        f = 'O'
                        
                    corrected = corrected + '_' + f + '_' + bn
                    names[i] = corrected
                    
                for n in names_hr:
                    i = names_hr.index(n)
                    corrected = re.sub(r'[^A-Z]',r'',n)
                    f = fts_hr[i]
                    bn = bus_area_hr[i]
                    bn = bn.replace(" ", "_")
                    
                    if f == 'NUC (Nuclear)':
                        f = 'Nuc'
                    elif f == 'NG (Natural Gas)':
                        f = 'NG'
                    elif f == 'BIT (Bituminous Coal)':
                        f = 'C'
                    elif f == 'SUN (Solar)':
                        f = 'S'
                    elif f == 'WAT (Water)':
                        f = 'H'
                    elif f == 'WND (Wind)':
                        f = 'W'
                    elif f == 'DFO (Distillate Fuel Oil)':
                        f = 'O'
                        
                    corrected = corrected + '_' + f + '_' + bn
                    names_hr[i] = corrected
                
                df_gens['PlantNames'] = names
                df_gens_heat_rate['PlantNames'] = names_hr            
                NB = df_gens['NewBusNum'].unique()
                plants = []
                caps = []
                mw_min = []
                count = 2
                nbs = []
                heat_rate = []
                f = []
                thermal = ['NG (Natural Gas)','NUC (Nuclear)','BIT (Bituminous Coal)','DFO (Distillate Fuel Oil)']
                
                for n in NB:
                    sample = df_gens.loc[df_gens['NewBusNum'] == n]
                    sample_hr = df_gens_heat_rate.loc[df_gens_heat_rate['NewBusNum'] == n]
                    sublist = sample['PlantNames'].unique()
                    for s in sublist:
                        fuel = list(sample.loc[sample['PlantNames']==s,'FuelType'])
                        if fuel[0] in thermal:
                            c = sum(sample.loc[sample['PlantNames']==s,'MWMax'].values)
                            hr = np.nanmean(sample.loc[sample['PlantNames']==s,'Heat Rate MBTU/MWh'].values)
                            if hr == np.nan or hr == 0 or hr == 'nan' or hr == '':
                                # print(n)
                                hr = np.nanmean(df_gens.loc[df_gens['FuelType']==fuel[0],'Heat Rate MBTU/MWh'].values)
                            else:
                                pass
                            mn = sum(sample.loc[sample['PlantNames']==s,'MWMin'].values)
                            mw_min.append(mn)
                            caps.append(c)
                            nbs.append(n)
                            heat_rate.append(hr)
                            f.append(fuel[0])
                            if s in plants:
                                new = s + '_' + str(count)
                                plants.append(new)
                                count+=1
                            else:
                                plants.append(s)
                
                C=np.column_stack((plants,nbs))
                C=np.column_stack((C,f))
                C=np.column_stack((C,caps))
                C=np.column_stack((C,mw_min))
                C=np.column_stack((C,heat_rate))
                
                df_C = pd.DataFrame(C)
                df_C.columns = ['Name','Bus','Fuel','Max_Cap','Min_Cap','Heat_Rate']
                df_C.to_csv('thermal_gens.csv',index=None)
                copy('thermal_gens.csv',path)
                    
                
                # ##############################
                # # HYDROPOWER
                
                # #EIA plants
                # df_hydro = pd.read_csv('EIA_302_WECC_hydro_plants.csv',header=0)
                # df_hydro_ts = pd.read_csv('p_mean_max_min_MW_WECC_302plants_weekly_2019.csv',header=0)
                # new_hydro_nodes = []
                
                # for i in range(0,len(df_hydro)):
                    
                #     name = df_hydro.loc[i,'plant']
                #     new_name = re.sub(r'[^A-Z]',r'',name)
                #     bus = df_hydro.loc[i,'bus']
                    
                #     if bus in old_bus_num:
                #         idx = old_bus_num.index(bus)
                #         new_hydro_nodes.append(new_bus_num[idx])
                #         pass
                #     elif bus in buses:
                #         new_hydro_nodes.append(bus)
                #     else:
                #         print(name + ' Not found')
                
                # # add mean/min/max by node
                # H_min = np.zeros((52,len(buses)))
                # H_max = np.zeros((52,len(buses)))
                # H_mu = np.zeros((52,len(buses)))
                
                # for i in range(0,len(df_hydro)):
                #     b = new_hydro_nodes[i]
                #     idx = buses.index(b)
                #     plant = df_hydro.loc[i,'plant']
                    
                #     ts = df_hydro_ts[df_hydro_ts['plant']==plant]
                    
                #     H_min[:,idx] += ts['min']
                #     H_max[:,idx] += ts['max']
                #     H_mu[:,idx] += ts['mean']
                    
                
                # # create daily time series by node
                # H_min_hourly = np.zeros((365,len(buses)))
                # H_max_hourly = np.zeros((365,len(buses)))
                # H_mu_hourly = np.zeros((365,len(buses)))
                
                # for i in range(0,len(H_min)):
                #     for j in range(0,len(buses)):
                #         H_min_hourly[i*7:i*7+7,j] = H_min[i,j]
                #         H_max_hourly[i*7:i*7+7,j] = H_max[i,j]
                #         H_mu_hourly[i*7:i*7+7,j] = H_mu[i,j]*24
                        
                # H_min_hourly[364,:] = H_min_hourly[363,:]
                # H_max_hourly[364,:] = H_max_hourly[363,:]
                # H_mu_hourly[364,:] = H_mu_hourly[363,:] 
                
                # h_buses = []
                # for i in range(0,len(buses)):
                #     h_buses.append('bus_' + str(buses[i]))
                
                # H_min_df = pd.DataFrame(H_min_hourly)
                # H_min_df.columns = h_buses
                # H_max_df = pd.DataFrame(H_max_hourly)
                # H_max_df.columns = h_buses
                # H_mu_df = pd.DataFrame(H_mu_hourly) 
                # H_mu_df.columns = h_buses       
                
                # H_min_df.to_csv('Hydro_min.csv',index=None)
                # H_max_df.to_csv('Hydro_max.csv',index=None)
                # H_mu_df.to_csv('Hydro_total.csv',index=None)
                
                # copy('Hydro_min.csv',path)
                # copy('Hydro_max.csv',path)
                # copy('Hydro_total.csv',path)
                
                    
                
                #########################################
                # Generator file setup
                
                df_G = pd.read_csv('thermal_gens.csv',header=0)
                
                names = []
                typs = []
                nodes = []
                maxcaps = []
                mincaps = []
                heat_rates = []
                var_oms = []
                no_loads = []
                st_costs = []
                ramps = []
                minups = []
                mindns = []
                
                must_nodes = []
                must_caps = []
                
                for i in range(0,len(df_G)):
                    
                    name = df_G.loc[i,'Name']
                    t = df_G.loc[i,'Fuel']
                    if t == 'NG (Natural Gas)':
                        typ = 'ngcc'
                    elif t == 'BIT (Bituminous Coal)':
                        typ = 'coal'
                    elif t == 'DFO (Distillate Fuel Oil)':
                        typ = 'oil'
                    else:
                        typ = 'nuclear'
                    node = 'bus_' + str(df_G.loc[i,'Bus'])
                    maxcap = df_G.loc[i,'Max_Cap']
                    mincap = df_G.loc[i,'Min_Cap']
                    hr_2 = df_G.loc[i,'Heat_Rate']
                    
                    if typ == 'ngcc':
                        var_om = 3
                        minup = 4
                        mindn = 4
                        ramp = maxcap
                    elif typ == 'oil':
                        var_om = 8
                        minup = 1
                        mindn = 1
                        ramp = maxcap
                    else:
                        var_om = 4
                        minup = 12
                        mindn = 12
                        ramp = 0.33*maxcap
                    
                    st_cost = 70*maxcap
                    no_load = 3*maxcap
                    
                    if typ != 'nuclear':
                        
                        names.append(name)
                        typs.append(typ)
                        nodes.append(node)
                        maxcaps.append(maxcap)
                        mincaps.append(mincap)
                        var_oms.append(var_om)
                        no_loads.append(no_load)
                        st_costs.append(st_cost)
                        ramps.append(ramp)
                        minups.append(minup)
                        mindns.append(mindn)
                        heat_rates.append(hr_2)
                        
                    else:
                        
                        must_nodes.append(node)
                        must_caps.append(maxcap)
                    
                
                # wind
                
                df_W = pd.read_csv('nodal_wind.csv',header=0)
                buses = list(df_W.columns)
                for n in buses:
                    
                    if sum(df_W[n]) > 0:
                        name = n + '_WIND'
                        maxcap = 100000
                        names.append(name)
                        typs.append('wind')
                        nodes.append(n)
                        maxcaps.append(maxcap)
                        mincaps.append(0)
                        var_oms.append(0)
                        no_loads.append(0)
                        st_costs.append(0)
                        ramps.append(0)
                        minups.append(0)
                        mindns.append(0) 
                        heat_rates.append(0)
                
                # solar
                
                df_S = pd.read_csv('nodal_solar.csv',header=0)
                buses = list(df_S.columns)
                for n in buses:
                    if sum(df_S[n]) > 0:
                        name = n + '_SOLAR'
                        maxcap = 100000
                        names.append(name)
                        typs.append('solar')
                        nodes.append(n)
                        maxcaps.append(maxcap)
                        mincaps.append(0)
                        var_oms.append(0)
                        no_loads.append(0)
                        st_costs.append(0)
                        ramps.append(0)
                        minups.append(0)
                        mindns.append(0)   
                        heat_rates.append(0)
                
                # hydro
                
                df_H = pd.read_csv('nodal_hydro.csv',header=0)
                buses = list(df_H.columns)
                for n in buses:
                    if sum(df_H[n]) > 0:
                        name = n + '_HYDRO'
                        maxcap = max(df_H[n])
                        names.append(name)
                        typs.append('hydro')
                        nodes.append(n)
                        maxcaps.append(maxcap)
                        mincaps.append(0)
                        var_oms.append(1)
                        no_loads.append(1)
                        st_costs.append(1)
                        ramps.append(maxcap)
                        minups.append(0)
                        mindns.append(0)   
                        heat_rates.append(0)
                
                df_genparams = pd.DataFrame()
                df_genparams['name'] = names
                df_genparams['typ'] = typs
                df_genparams['node'] = nodes
                df_genparams['maxcap'] = maxcaps
                df_genparams['heat_rate'] = heat_rates
                df_genparams['mincap'] = mincaps
                df_genparams['var_om'] = var_oms
                df_genparams['no_load'] = no_loads
                df_genparams['st_cost'] = st_costs
                df_genparams['ramp'] = ramps
                df_genparams['minup'] = minups
                df_genparams['mindn'] = mindns
                
                df_genparams.to_csv('data_genparams_full.csv',index=None)
                copy('data_genparams_full.csv',path)
                
                df_must = pd.DataFrame()
                for i in range(0,len(must_nodes)):
                    n = must_nodes[i]
                    df_must[n] = [must_caps[i]]
                df_must.to_csv('must_run.csv',index=None)
                copy('must_run.csv',path)
                
                ######       
                
                
                ######
                # create gen-to-bus matrix
                
                df = pd.read_csv('data_genparams_full.csv',header=0)
                gens = list(df.loc[:,'name'])
                df_nodes = pd.read_excel(os.path.join(base_dir, FN), sheet_name = 'Bus', header=0)
                all_nodes = list(df_nodes['bus_i'])
                for i in range(0,len(all_nodes)):
                    all_nodes[i] = 'bus_' + str(all_nodes[i])
                
                A = np.zeros((len(gens),len(all_nodes)))
                
                df_A = pd.DataFrame(A)
                df_A.columns = all_nodes
                df_A['name'] = gens
                df_A.set_index('name',inplace=True)
                
                for i in range(0,len(gens)):
                    node = df.loc[i,'node']
                    g = gens[i]
                    df_A.loc[g,node] = 1
                
                df_A.to_csv('gen_mat_full.csv')
                copy('gen_mat_full.csv',path)
                
                
                
                # If uncommented, this section aggregates oil generators on nodal basis
                df = pd.read_csv('data_genparams_full.csv',header=0)
                
                df_oil = df.loc[df['typ'] == 'oil']
                df_oil = df_oil.reset_index(drop=True)
                
                gens = list(df.loc[:,'name'])
                gens_oil = list(df_oil.loc[:,'name'])
                gens_cap = list(df.loc[:,'maxcap'])
                gens_hr = list(df.loc[:,'heat_rate'])
                gens_min = list(df.loc[:,'mincap'])
                gens_var_om = list(df.loc[:,'var_om'])
                gens_no_load = list(df.loc[:,'no_load'])
                gens_st_cost = list(df.loc[:,'st_cost'])
                gens_ramp = list(df.loc[:,'ramp'])
                
                
                # Read nodes
                FN = 'reduced_network/Results_' + str(NN) + '.xlsx'
                df_nodes = pd.read_excel(os.path.join(base_dir, FN), sheet_name = 'Bus', header=0)
                all_nodes = list(df_nodes['bus_i'])
                
                # Read generator-node matrix
                df_gen_mat = pd.read_csv('gen_mat_full.csv',header=0)
                
                ######
                # create gen-to-bus matrix for oil
                
                for i in range(0,len(all_nodes)):
                    all_nodes[i] = 'bus_' + str(all_nodes[i])
                
                df_nodes['bus_i'] = all_nodes
                            
                A = np.zeros((len(gens),len(all_nodes)))
                            
                df_A = pd.DataFrame(A)
                df_A.columns = all_nodes
                df_A['name'] = gens
                df_A.set_index('name',inplace=True)
                            
                for i in range(0,len(gens_oil)):
                    node = df_oil.loc[i,'node']
                    g = gens_oil[i]
                    df_A.loc[g,node] = 1
                
                ######
                
                # Calculate oil parameters for each node
                tot_cap = np.zeros(len(all_nodes))
                oil_cap = np.zeros(len(all_nodes))
                oil_max = np.zeros(len(all_nodes))
                oil_hr = np.zeros(len(all_nodes))
                oil_min = np.zeros(len(all_nodes))
                oil_var_om = np.zeros(len(all_nodes))
                oil_no_load = np.zeros(len(all_nodes))
                oil_st_cost = np.zeros(len(all_nodes))
                oil_ramp = np.zeros(len(all_nodes))
                
                for i in range(0,len(all_nodes)):
                    tot_cap[i] = sum(gens_cap*df_gen_mat.iloc[:,i+1])
                    oil_cap[i] = sum(gens_cap*df_A.iloc[:,i])
                    oil_max[i] = sum(gens_cap*df_A.iloc[:,i])
                    oil_hr[i] = sum(gens_hr*(gens_cap*df_A.iloc[:,i])/sum(gens_cap*df_A.iloc[:,i]))
                    oil_min[i] = sum(gens_min*(gens_cap*df_A.iloc[:,i])/sum(gens_cap*df_A.iloc[:,i]))
                    oil_var_om[i] = sum(gens_var_om*(gens_cap*df_A.iloc[:,i])/sum(gens_cap*df_A.iloc[:,i]))
                    oil_no_load[i] = sum(gens_no_load*(gens_cap*df_A.iloc[:,i])/sum(gens_cap*df_A.iloc[:,i]))
                    oil_st_cost[i] = sum(gens_st_cost*(gens_cap*df_A.iloc[:,i])/sum(gens_cap*df_A.iloc[:,i]))
                    oil_ramp[i] = sum(gens_ramp*df_A.iloc[:,i])
                
                # Write oil parameters into the nodes dataframe
                df_oil = pd.DataFrame()
                df_oil.loc[:,'node'] = list(df_nodes.loc[:,'bus_i'])
                df_oil.loc[:,'maxcap'] = oil_max
                df_oil.loc[:,'heat_rate'] = oil_hr
                df_oil.loc[:,'mincap'] = oil_min
                df_oil.loc[:,'var_om'] = oil_var_om
                df_oil.loc[:,'no_load'] = oil_no_load
                df_oil.loc[:,'st_cost'] = oil_st_cost
                df_oil.loc[:,'ramp'] = oil_ramp
                df_oil = df_oil.dropna().reset_index(drop=True)
                
                df_oil.loc[:,'minup'] = 1
                df_oil.loc[:,'mindn'] = 1
                df_oil.loc[:,'typ'] = 'oil'
                
                oil_name = []
                for i in range(0,len(df_oil.index)):
                    oil_name.append(df_oil.loc[i,'node'] + '_oil')
                df_oil.loc[:,'name'] = oil_name
                
                df_oil = df_oil[["name", "typ", "node", "maxcap", "heat_rate", "mincap", "var_om", "no_load", "st_cost", "ramp", "minup", "mindn"]]
                
                # Substitute aggregated oil gens into the data_genparams.csv file
                # Removing the old set of oil generators
                df = df.loc[df['typ'] != 'oil']
                df = pd.concat([df, df_oil], ignore_index=True)
                df.to_csv('data_genparams.csv',index=None)
                copy('data_genparams.csv',path)
                
                
                ##### Recreate Generator to Bus matrix
                
                df = pd.read_csv('data_genparams.csv',header=0)
                gens = list(df.loc[:,'name'])
                
                df_nodes = pd.read_excel(os.path.join(base_dir, FN), sheet_name = 'Bus', header=0)
                all_nodes = list(df_nodes['bus_i'])
                for i in range(0,len(all_nodes)):
                    all_nodes[i] = 'bus_' + str(all_nodes[i])
                
                A = np.zeros((len(gens),len(all_nodes)))
                
                df_A = pd.DataFrame(A)
                df_A.columns = all_nodes
                df_A['name'] = gens
                df_A.set_index('name',inplace=True)
                
                for i in range(0,len(gens)):
                    node = df.loc[i,'node']
                    g = gens[i]
                    df_A.loc[g,node] = 1
                
                df_A.to_csv('gen_mat.csv')
                copy('gen_mat.csv',path)
                
    
                
                #####################################
                # TRANSMISSION
                
                df = pd.read_excel(os.path.join(base_dir, FN), sheet_name = 'Branch',header=0)
                
                # eliminate repeats
                lines = []
                repeats = []
                index = []
                for i in range(0,len(df)):
                    
                    t=tuple((df.loc[i,'fbus'],df.loc[i,'tbus']))
                    
                    if t in lines:
                        df = df.drop([i])
                        repeats.append(t)
                        r = lines.index(t)
                        i = index[r]
                        df.loc[i,'rateA'] += df.loc[i,'rateA']
                    else:
                        lines.append(t)
                        index.append(i)
                
                df = df.reset_index(drop=True)
                    
                sources = df.loc[:,'fbus']
                sinks = df.loc[:,'tbus']
                combined = np.append(sources, sinks)
                df_combined = pd.DataFrame(combined,columns=['node'])
                unique_nodes = df_combined['node'].unique()
                unique_nodes.sort()
                
                A = np.zeros((len(df),len(unique_nodes)))
                
                df_line_to_bus = pd.DataFrame(A)
                df_line_to_bus.columns = unique_nodes
                
                negative = []
                positive = []
                lines = []
                ref_node = 0
                reactance = []
                limit = []
                
                for i in range(0,len(df)):
                    s = df.loc[i,'fbus']
                    k = df.loc[i,'tbus']
                    line = str(s) + '_' + str(k)
                    if s == df.loc[0,'fbus']: 
                        lines.append(line)
                        positive.append(s)
                        negative.append(k)
                        df_line_to_bus.loc[ref_node,s] = 1
                        df_line_to_bus.loc[ref_node,k] = -1
                        reactance.append(df.loc[i,'x'])
                        MW = (1/df.loc[i,'x'])*100*(1+T_p)
                        limit.append(MW)
                        ref_node += 1
                    elif k == df.loc[0,'fbus']:      
                        lines.append(line)
                        positive.append(k)
                        negative.append(s)
                        df_line_to_bus.loc[ref_node,k] = 1
                        df_line_to_bus.loc[ref_node,s] = -1
                        reactance.append(df.loc[i,'x'])
                        MW = (1/df.loc[i,'x'])*100*(1+T_p)
                        limit.append(MW)
                        ref_node += 1
                        
                for i in range(0,len(df)):
                    s = df.loc[i,'fbus']
                    k = df.loc[i,'tbus']
                    line = str(s) + '_' + str(k)
                    if s != df.loc[0,'fbus']:
                        if k != df.loc[0,'fbus']:
                            lines.append(line)
                            
                            if s in positive and k in negative:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                            
                            elif k in positive and s in negative:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1
                                
                            elif s in positive and k in positive:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                            
                            elif s in negative and k in negative:   
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                                
                            elif s in positive:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                                negative.append(k)
                            elif s in negative:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1   
                                positive.append(k)
                            elif k in positive:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1  
                                negative.append(s)
                            elif k in negative:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1 
                                positive.append(s)
                            else:
                                positive.append(s)
                                negative.append(k)
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                
                            reactance.append(df.loc[i,'x'])
                            MW = (1/df.loc[i,'x'])*100*(1+T_p)
                            limit.append(MW)
                            ref_node += 1
                
                unique_nodes = list(unique_nodes)
                for i in range(0,len(unique_nodes)):
                    unique_nodes[i] = 'bus_' + str(unique_nodes[i])
                df_line_to_bus.columns = unique_nodes
                
                for i in range(0,len(lines)):
                    lines[i] = 'line_' + lines[i]
                    
                df_line_to_bus['line'] = lines
                df_line_to_bus.set_index('line',inplace=True)
                df_line_to_bus.to_csv('line_to_bus.csv')
                copy('line_to_bus.csv',path)
                
                
                df_line_params = pd.DataFrame()
                df_line_params['line'] = lines
                df_line_params['reactance'] = reactance
                df_line_params['limit'] = limit 
                df_line_params.to_csv('line_params.csv',index=None)
                copy('line_params.csv',path)
                
                
                #Creating BA to BA transmission matrix for individual lines
                exchange_columns = ['Exchange'] + lines
                BA_to_BA_exchange_matrix = pd.DataFrame(np.zeros((len(all_BA_BA_connections),len(exchange_columns))),columns=exchange_columns,index=all_BA_BA_connections)
                BA_to_BA_exchange_matrix.loc[:,'Exchange'] = all_BA_BA_connections
                
                for i in all_BA_BA_connections:
                    
                    weight_count = 0
                    line_count = 0
                    
                    splitted_str = i.split('_')
                    first_BA = splitted_str[0]
                    second_BA = splitted_str[1]
                    
                    for j in lines:
                                            
                        splitted_line = j.split('_')
                        BA_first_line = df_selected.loc[df_selected['bus_i']==int(splitted_line[1])]['BA'].values[0]
                        first_BA_abb = df_BAs.loc[df_BAs['Name']==BA_first_line]['Abbreviation'].values[0]
                        
                        a_bus = df_line_to_bus.loc[j,'bus_' + splitted_line[1]]
                        
                        BA_second_line = df_selected.loc[df_selected['bus_i']==int(splitted_line[2])]['BA'].values[0]
                        second_BA_abb = df_BAs.loc[df_BAs['Name']==BA_second_line]['Abbreviation'].values[0]
                        
                        b_bus = df_line_to_bus.loc[j,'bus_' + splitted_line[2]]
                        
                        # print(a_bus + b_bus)
                        
                        #if flow on that line means flow from first BA to second BA, write 1, if vice versa write -1
                        if first_BA_abb == first_BA and second_BA_abb == second_BA:
                            line_count += 1
                            BA_to_BA_exchange_matrix.loc[i,j] = int(a_bus)
                        elif first_BA_abb == second_BA and second_BA_abb == first_BA:
                            BA_to_BA_exchange_matrix.loc[i,j] = int(b_bus)
                            line_count += 1
                        else:
                            pass
                        
                        weight_count += int(BA_to_BA_exchange_matrix.loc[i,j])
                        
                
                BA_to_BA_exchange_matrix.to_csv('BA_to_BA_transmission_matrix.csv', index=False)
                copy('BA_to_BA_transmission_matrix.csv',path)
                copy('EIC_BA_to_BA_max_flows.csv',path)
                
                #####################################
                # FUEL PRICES
                
                df_genparams = pd.read_csv('data_genparams.csv',header=0)
                
                # Natural gas prices
                NG_price = pd.read_csv(os.path.join(base_dir, 'NG_price/Average_NG_prices_BAs.csv'), header=0)
                buses = list(df_selected['bus_i'])
                for bus in buses:
                    
                    selected_node_BA = df_full.loc[df_full['Number']==bus,'NAME'].values[0]
                    specific_node_NG_price = NG_price.loc[:,selected_node_BA].copy()
                    
                    if buses.index(bus) == 0:
                        NG_prices_all = specific_node_NG_price.copy()
                    else:
                        NG_prices_all = pd.concat([NG_prices_all,specific_node_NG_price], axis=1)
                
                Fuel_buses = []
                for i in range(0,len(buses)):
                    Fuel_buses.append('bus_' + str(buses[i]))
                
                NG_prices_all.columns = Fuel_buses
                
                # Coal prices
                Coal_price = pd.read_csv(os.path.join(base_dir, 'Coal_price/coal_prices_state.csv'), header=0)
        
                for bus in buses:
                    
                    selected_node_state = df_full.loc[df_full['Number']==bus,'STATE'].values[0]
                    
                    if selected_node_state == 'NB':
                        selected_node_state = 'ME'
                    elif selected_node_state == 'CO':
                        selected_node_state = 'KS'
                    elif selected_node_state == 'OR':
                        selected_node_state = 'AR'
                    elif selected_node_state == 'TX':
                        selected_node_state = 'OK'
                    elif selected_node_state == 'NM':
                        selected_node_state = 'OK'
                    elif selected_node_state == 'MT':
                        selected_node_state = 'SD'
                        
                    specific_node_coal_price = Coal_price.loc[:,selected_node_state].copy()
                    
                    if buses.index(bus) == 0:
                        Coal_prices_all = specific_node_coal_price.copy()
                    else:
                        Coal_prices_all = pd.concat([Coal_prices_all,specific_node_coal_price], axis=1)
                
                Coal_prices_all.columns = Fuel_buses
                
                Oil_prices = np.reshape(np.ones((365,1))*20,(365,))
                Oil_prices_all = pd.DataFrame()
                Oil_prices_all['all'] = Oil_prices
                
                # getting generator based fuel prices
                
                thermal_gens_info = df_genparams.loc[(df_genparams['typ']=='ngcc') | (df_genparams['typ']=='coal') | (df_genparams['typ']=='oil')].copy()
                thermal_gens_names = [*thermal_gens_info['name']]
                
                for ind, row in thermal_gens_info.iterrows():
                    
                    if row['typ'] == 'ngcc':
                        gen_fuel_price = NG_prices_all.loc[:, row['node']].copy() 
                    elif row['typ'] == 'coal':
                        gen_fuel_price = Coal_prices_all.loc[:, row['node']].copy() 
                    elif row['typ'] == 'oil':
                        gen_fuel_price = Oil_prices_all.loc[:,'all'].copy()
                    else:
                        pass
                    
                    if thermal_gens_names.index(row['name']) == 0:
                        Fuel_prices_all = gen_fuel_price.copy()
                    else:
                        Fuel_prices_all = pd.concat([Fuel_prices_all,gen_fuel_price], axis=1)
                        
                Fuel_prices_all.columns = thermal_gens_names
                
                Fuel_prices_all.to_csv('Fuel_prices.csv',index=None)
                copy('Fuel_prices.csv',path)       
    
                #copy other files
                w = 'wrapper' + UC + '_' + str(section) + '.py'
                milp = 'EIC_MILP' + UC + '.py'
                lp = 'EIC_LP' + UC + '.py'
                
                copy(w,path)
                copy('EICDataSetup.py',path)
                
                if UC == '_simple':
                    copy('EIC' + UC + '.py',path)
                else:          
                    copy(milp,path)
                    copy(lp,path)
                
                #Generator outages 
                copy('east_19_lostcap.csv',path)
                #importing a function created in another script to generate a dictionary from the data_genparams file
                from dict_creator import dict_funct
                df_loss_dict=dict_funct(df_genparams)
                #save the dictionary as a .npy file
                np.save('df_dict2.npy', df_loss_dict)
                copy('df_dict2.npy',path)
                    
                

