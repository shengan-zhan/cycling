# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:25:00 2019

@author: Shengan
"""

import requests
import lxml
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
from unidecode import unidecode

def rider_results(year):
    cq_url = 'https://cqranking.com/men/asp/gen/searchResults.asp'
    
    df_riders = pd.read_csv('riders_{}.csv'.format(year),encoding='iso-8859-1')
    rider = list(df_riders['Rider'])
    
    year = year
    
    df_rider_results = pd.DataFrame([])
    
    for r in rider:
        payload = {
                'listYears':year,
                #'includeStages': "0",
                'ridercontains': unidecode(r),
                'includeStages': 'on',
                'butSearch':' Search '
                }
        print(r)
        r = requests.post(cq_url,data=payload)
        soup = bs(r.text.encode('iso-8859-1'),'lxml')
        table = soup.find(lambda t: 'Date' in t).find_parent('table')
        df = pd.read_html(table.prettify(),header=0)[0]
        #df_race = pd.read_html(soup.find_all('table')[-1].prettify(),header=0)[0]
        df.dropna(axis=1, how='all', inplace=True)
        df_rider_results = pd.concat([df_rider_results,df],ignore_index=True,sort=False)
    
    # clean up mismatches
    for r in list(df_rider_results['Rider'].unique()):
        if r not in rider:
    #        df_rider_results.drop(df_rider_results[df_rider_results['Rider']==r].index,axis=0,inplace=True)
            print('Mismatches: ' + r)
            
    df_rider_results.to_csv('rider_results_{}.csv'.format(year),index=False,encoding='iso-8859-1')
    print(df_rider_results.head())
    
    return df_rider_results