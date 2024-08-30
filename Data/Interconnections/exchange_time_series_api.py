# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 21:18:42 2024

@author: jkern
"""

import pandas as pd
import datetime

def generate_dates():
    dates = []
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                date = datetime.date(2019, month, day)
                formatted_date = date.strftime('%m-%d')
                dates.append(formatted_date)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31)
                pass
    return dates

date_list = generate_dates()

for y in range(2020,2024):
    
    dfs = []  # Initialize an empty list
    
    for i in range(365):
        
        d = date_list[i]
                
        F = str(y) + "-" + d + "T00"
        S = str(y) + "-" + d + "T23"
        
        #url = "https://api.eia.gov/v2/electricity/rto/interchange-data/data/?frequency=hourly&data[0]=value&facets[fromba][]=AEC&facets[fromba][]=AECI&facets[fromba][]=AVA&facets[fromba][]=AVRN&facets[fromba][]=AZPS&facets[fromba][]=BANC&facets[fromba][]=BPAT&facets[fromba][]=CAL&facets[fromba][]=CAR&facets[fromba][]=CAR&facets[fromba][]=CENT&facets[fromba][]=CENT&facets[fromba][]=CHPD&facets[fromba][]=CISO&facets[fromba][]=CPLE&facets[fromba][]=CPLW&facets[fromba][]=DEAA&facets[fromba][]=DOPD&facets[fromba][]=DUK&facets[fromba][]=EEI&facets[fromba][]=EPE&facets[fromba][]=ERCO&facets[fromba][]=FLA&facets[fromba][]=FMPP&facets[fromba][]=FPC&facets[fromba][]=FPL&facets[fromba][]=GCPD&facets[fromba][]=GRID&facets[fromba][]=GRIF&facets[fromba][]=GVL&facets[fromba][]=GWA&facets[fromba][]=HGMA&facets[fromba][]=HST&facets[fromba][]=IID&facets[fromba][]=IPCO&facets[fromba][]=ISNE&facets[fromba][]=JEA&facets[fromba][]=LDWP&facets[fromba][]=LGEE&facets[fromba][]=MIDA&facets[fromba][]=MIDA&facets[fromba][]=MIDW&facets[fromba][]=MIDW&facets[fromba][]=MISO&facets[fromba][]=NE&facets[fromba][]=NE&facets[fromba][]=NEVP&facets[fromba][]=NSB&facets[fromba][]=NW&facets[fromba][]=NWMT&facets[fromba][]=NY&facets[fromba][]=NY&facets[fromba][]=NYIS&facets[fromba][]=PACE&facets[fromba][]=PACW&facets[fromba][]=PGE&facets[fromba][]=PJM&facets[fromba][]=PNM&facets[fromba][]=PSCO&facets[fromba][]=PSEI&facets[fromba][]=SC&facets[fromba][]=SCEG&facets[fromba][]=SCL&facets[fromba][]=SE&facets[fromba][]=SE&facets[fromba][]=SEC&facets[fromba][]=SEPA&facets[fromba][]=SOCO&facets[fromba][]=SPA&facets[fromba][]=SRP&facets[fromba][]=SW&facets[fromba][]=SWPP&facets[fromba][]=TAL&facets[fromba][]=TEC&facets[fromba][]=TEN&facets[fromba][]=TEPC&facets[fromba][]=TEX&facets[fromba][]=TIDC&facets[fromba][]=TPWR&facets[fromba][]=TVA&facets[fromba][]=US48&facets[fromba][]=WACM&facets[fromba][]=WALC&facets[fromba][]=WAUW&facets[fromba][]=WWA&facets[fromba][]=YAD&facets[toba][]=AEC&facets[toba][]=AECI&facets[toba][]=AESO&facets[toba][]=AVA&facets[toba][]=AVRN&facets[toba][]=AZPS&facets[toba][]=BANC&facets[toba][]=BCHA&facets[toba][]=BPAT&facets[toba][]=CAL&facets[toba][]=CAN&facets[toba][]=CAR&facets[toba][]=CEN&facets[toba][]=CENT&facets[toba][]=CHPD&facets[toba][]=CISO&facets[toba][]=CPLE&facets[toba][]=CPLW&facets[toba][]=DEAA&facets[toba][]=DOPD&facets[toba][]=DUK&facets[toba][]=EEI&facets[toba][]=EPE&facets[toba][]=ERCO&facets[toba][]=FLA&facets[toba][]=FMPP&facets[toba][]=FPC&facets[toba][]=FPL&facets[toba][]=GCPD&facets[toba][]=GRID&facets[toba][]=GRIF&facets[toba][]=GVL&facets[toba][]=GWA&facets[toba][]=HGMA&facets[toba][]=HQT&facets[toba][]=HST&facets[toba][]=IESO&facets[toba][]=IID&facets[toba][]=IPCO&facets[toba][]=ISNE&facets[toba][]=JEA&facets[toba][]=LDWP&facets[toba][]=LGEE&facets[toba][]=MEX&facets[toba][]=MHEB&facets[toba][]=MIDA&facets[toba][]=MIDW&facets[toba][]=MISO&facets[toba][]=NBSO&facets[toba][]=NE&facets[toba][]=NEVP&facets[toba][]=NSB&facets[toba][]=NW&facets[toba][]=NWMT&facets[toba][]=NY&facets[toba][]=NYIS&facets[toba][]=PACE&facets[toba][]=PACW&facets[toba][]=PGE&facets[toba][]=PJM&facets[toba][]=PNM&facets[toba][]=PSCO&facets[toba][]=PSEI&facets[toba][]=SC&facets[toba][]=SCEG&facets[toba][]=SCL&facets[toba][]=SE&facets[toba][]=SEC&facets[toba][]=SEPA&facets[toba][]=SOCO&facets[toba][]=SPA&facets[toba][]=SPC&facets[toba][]=SRP&facets[toba][]=SW&facets[toba][]=SWPP&facets[toba][]=TAL&facets[toba][]=TEC&facets[toba][]=TEN&facets[toba][]=TEPC&facets[toba][]=TEX&facets[toba][]=TIDC&facets[toba][]=TPWR&facets[toba][]=TVA&facets[toba][]=WACM&facets[toba][]=WALC&facets[toba][]=WAUW&facets[toba][]=WWA&facets[toba][]=YAD&start=2019-01-01T00&end=2019-12-31T00&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=c03df3a8ab4129408b54ef3c46c15c2c"
       
        
        url = "https://api.eia.gov/v2/electricity/rto/interchange-data/data/?frequency=hourly&data[0]=value&facets[fromba][]=AEC&facets[fromba][]=AECI&facets[fromba][]=AVA&facets[fromba][]=AVRN&facets[fromba][]=AZPS&facets[fromba][]=BANC&facets[fromba][]=BPAT&facets[fromba][]=CAL&facets[fromba][]=CAR&facets[fromba][]=CAR&facets[fromba][]=CENT&facets[fromba][]=CENT&facets[fromba][]=CHPD&facets[fromba][]=CISO&facets[fromba][]=CPLE&facets[fromba][]=CPLW&facets[fromba][]=DEAA&facets[fromba][]=DOPD&facets[fromba][]=DUK&facets[fromba][]=EEI&facets[fromba][]=EPE&facets[fromba][]=ERCO&facets[fromba][]=FLA&facets[fromba][]=FMPP&facets[fromba][]=FPC&facets[fromba][]=FPL&facets[fromba][]=GCPD&facets[fromba][]=GRID&facets[fromba][]=GRIF&facets[fromba][]=GVL&facets[fromba][]=GWA&facets[fromba][]=HGMA&facets[fromba][]=HST&facets[fromba][]=IID&facets[fromba][]=IPCO&facets[fromba][]=ISNE&facets[fromba][]=JEA&facets[fromba][]=LDWP&facets[fromba][]=LGEE&facets[fromba][]=MIDA&facets[fromba][]=MIDA&facets[fromba][]=MIDW&facets[fromba][]=MIDW&facets[fromba][]=MISO&facets[fromba][]=NE&facets[fromba][]=NE&facets[fromba][]=NEVP&facets[fromba][]=NSB&facets[fromba][]=NW&facets[fromba][]=NWMT&facets[fromba][]=NY&facets[fromba][]=NY&facets[fromba][]=NYIS&facets[fromba][]=PACE&facets[fromba][]=PACW&facets[fromba][]=PGE&facets[fromba][]=PJM&facets[fromba][]=PNM&facets[fromba][]=PSCO&facets[fromba][]=PSEI&facets[fromba][]=SC&facets[fromba][]=SCEG&facets[fromba][]=SCL&facets[fromba][]=SE&facets[fromba][]=SE&facets[fromba][]=SEC&facets[fromba][]=SEPA&facets[fromba][]=SOCO&facets[fromba][]=SPA&facets[fromba][]=SRP&facets[fromba][]=SW&facets[fromba][]=SWPP&facets[fromba][]=TAL&facets[fromba][]=TEC&facets[fromba][]=TEN&facets[fromba][]=TEPC&facets[fromba][]=TEX&facets[fromba][]=TIDC&facets[fromba][]=TPWR&facets[fromba][]=TVA&facets[fromba][]=US48&facets[fromba][]=WACM&facets[fromba][]=WALC&facets[fromba][]=WAUW&facets[fromba][]=WWA&facets[fromba][]=YAD&facets[toba][]=AEC&facets[toba][]=AECI&facets[toba][]=AESO&facets[toba][]=AVA&facets[toba][]=AVRN&facets[toba][]=AZPS&facets[toba][]=BANC&facets[toba][]=BCHA&facets[toba][]=BPAT&facets[toba][]=CAL&facets[toba][]=CAN&facets[toba][]=CAR&facets[toba][]=CEN&facets[toba][]=CENT&facets[toba][]=CHPD&facets[toba][]=CISO&facets[toba][]=CPLE&facets[toba][]=CPLW&facets[toba][]=DEAA&facets[toba][]=DOPD&facets[toba][]=DUK&facets[toba][]=EEI&facets[toba][]=EPE&facets[toba][]=ERCO&facets[toba][]=FLA&facets[toba][]=FMPP&facets[toba][]=FPC&facets[toba][]=FPL&facets[toba][]=GCPD&facets[toba][]=GRID&facets[toba][]=GRIF&facets[toba][]=GVL&facets[toba][]=GWA&facets[toba][]=HGMA&facets[toba][]=HQT&facets[toba][]=HST&facets[toba][]=IESO&facets[toba][]=IID&facets[toba][]=IPCO&facets[toba][]=ISNE&facets[toba][]=JEA&facets[toba][]=LDWP&facets[toba][]=LGEE&facets[toba][]=MEX&facets[toba][]=MHEB&facets[toba][]=MIDA&facets[toba][]=MIDW&facets[toba][]=MISO&facets[toba][]=NBSO&facets[toba][]=NE&facets[toba][]=NEVP&facets[toba][]=NSB&facets[toba][]=NW&facets[toba][]=NWMT&facets[toba][]=NY&facets[toba][]=NYIS&facets[toba][]=PACE&facets[toba][]=PACW&facets[toba][]=PGE&facets[toba][]=PJM&facets[toba][]=PNM&facets[toba][]=PSCO&facets[toba][]=PSEI&facets[toba][]=SC&facets[toba][]=SCEG&facets[toba][]=SCL&facets[toba][]=SE&facets[toba][]=SEC&facets[toba][]=SEPA&facets[toba][]=SOCO&facets[toba][]=SPA&facets[toba][]=SPC&facets[toba][]=SRP&facets[toba][]=SW&facets[toba][]=SWPP&facets[toba][]=TAL&facets[toba][]=TEC&facets[toba][]=TEN&facets[toba][]=TEPC&facets[toba][]=TEX&facets[toba][]=TIDC&facets[toba][]=TPWR&facets[toba][]=TVA&facets[toba][]=WACM&facets[toba][]=WALC&facets[toba][]=WAUW&facets[toba][]=WWA&facets[toba][]=YAD&start=" + F + "&end=" + S + "&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key=c03df3a8ab4129408b54ef3c46c15c2c"
    
        df = pd.read_json(url)
        
        #empty lists
        times=[]
        values = []
        fromba=[]
        toba=[]
        
        for i in range(0,len(df.loc['data','response'])):
            
          t = df.loc['data','response'][i]['period']
          v = df.loc['data','response'][i]['value']
          f = df.loc['data','response'][i]['fromba']
          to = df.loc['data','response'][i]['toba']
          
          times.append(t)
          values.append(v)
          fromba.append(f)
          toba.append(to)
    
        out_df = pd.DataFrame()
        out_df['hour'] = times
        out_df['value'] = values  
        out_df['fromba'] = fromba
        out_df['toba'] = toba
        
        dfs.append(out_df)  # Append each dataframe to the list
    
    final_df = pd.concat(dfs)  # Concatenate all dataframes
    
    final_df = final_df.sort_values(by=['hour'])
    final_df = final_df.reset_index(drop=True)
    
    filename = 'exchange time series' + str(y) + '.csv'
    final_df.to_csv(filename, index=None)
    

# NOW FIND MAXIMUM LIMITS FOR EACH BA TO BA DIRECTIONAL EXCHANGE


