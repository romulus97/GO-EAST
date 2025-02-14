# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 11:12:22 2021

@author: kakdemi
"""

import pandas as pd

# reading fuel region name data
fuel_region_data = pd.read_excel('FuelRegion_ElectricRegionDefinitions.xlsx',sheet_name='GPI_Fuel_Region',\
                                 header=0,usecols=['Fuel Region','Balancing Authority'])

# reading and defining BA names
BA_df = pd.read_csv('../BAs.csv', header=0)
BAs = ['AZPS', 'CISO', 'IPCO', 'NEVP', 'PACE', 'PACW', 'PGE', 'PSEI']
BAs_with_NG_data_name = list(BA_df.loc[BA_df['Abbreviation'].isin(BAs)]['Name'])
BAs_without_NG_data_name = list(set(list(BA_df['Name'])) - set(BAs_with_NG_data_name))

# getting all fuel regions under BAs except main region (minimum of all fuel regions)
for BA in BAs:
    
    all_regions = list(fuel_region_data.loc[fuel_region_data['Balancing Authority']==BA]['Fuel Region'])
    globals()['{}_regions'.format(BA)] = all_regions.copy()
    globals()['{}_regions'.format(BA)].remove('FR{}'.format(BA))
    
    
# reading in monthly data and aggregating them into one dataset
for month in range(1,13):
    
    fuel_data = pd.read_csv('Fuel_{}.csv'.format(month), header=0, usecols=['OPR_DT','FUEL_REGION_ID','PRC'])
    
    if month == 1:
        total_fuel_data = fuel_data
        
    else:
        total_fuel_data = total_fuel_data.append(fuel_data, ignore_index=True)

# creating a date range for the NG data 
time_range = pd.date_range(start='1/1/2019 00:00:00', end='12/31/2019 23:00:00', freq='H')

# calculating average fuel price for every BA and saving them
for BA in BAs:
    
    selected_regions = total_fuel_data.loc[total_fuel_data['FUEL_REGION_ID']\
                                           .isin(globals()['{}_regions'.format(BA)])].copy()
    trigger=0
    
    for region in globals()['{}_regions'.format(BA)]:
        
        specific_region = selected_regions.loc[selected_regions['FUEL_REGION_ID']==region].copy()
        
        if len(specific_region) == 8760:
            trigger+=1
            specific_region.index = time_range
            specific_region_daily_price = specific_region.resample('D').mean()
            
            if trigger==1:
                region_df = specific_region_daily_price.copy()
            
            elif trigger>1:
                region_df = pd.concat([region_df,specific_region_daily_price], axis=1)
            
        else:
            pass
           
    average_NG_price_BA = region_df.mean(axis=1).copy()
        
    if BAs.index(BA) == 0:
        final_NG_prices = average_NG_price_BA.copy()
    
    else:
        final_NG_prices = pd.concat([final_NG_prices,average_NG_price_BA], axis=1)
        
# changing the column names and saving the data as CSV  
final_NG_prices.columns = BAs_with_NG_data_name         
      
#reading BA coefficient matrix to estimate NG prices
BA_NG_coeff_matrix_df = pd.read_csv('BA_NG_Price_Coeff_Matrix.csv', header=0, index_col=0)

#estimating NG prices coefficients that are inversely proportional to distance between BAs
for BA_name in BAs_without_NG_data_name:
    
    final_NG_prices[BA_name] = final_NG_prices.loc[:,'ARIZONA PUBLIC SERVICE COMPANY']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'ARIZONA PUBLIC SERVICE COMPANY']+ \
        final_NG_prices.loc[:,'CALIFORNIA INDEPENDENT SYSTEM OPERATOR']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'CALIFORNIA INDEPENDENT SYSTEM OPERATOR']+ \
        final_NG_prices.loc[:,'IDAHO POWER COMPANY']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'IDAHO POWER COMPANY']+ \
        final_NG_prices.loc[:,'NEVADA POWER COMPANY']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'NEVADA POWER COMPANY']+ \
        final_NG_prices.loc[:,'PACIFICORP - EAST']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'PACIFICORP - EAST']+ \
        final_NG_prices.loc[:,'PACIFICORP - WEST']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'PACIFICORP - WEST']+ \
        final_NG_prices.loc[:,'PORTLAND GENERAL ELECTRIC COMPANY']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'PORTLAND GENERAL ELECTRIC COMPANY']+ \
        final_NG_prices.loc[:,'PUGET SOUND ENERGY']* \
        BA_NG_coeff_matrix_df.loc[BA_name,'PUGET SOUND ENERGY']
        


            
final_NG_prices.to_csv('Average_NG_prices_BAs.csv') 
    

    

    
