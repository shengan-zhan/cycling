# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 17:02:23 2019

@author: Shengan
"""
import requests
import lxml
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import numpy as np

def riders(year):
    df_teams = pd.read_csv('teams_{}.csv'.format(year))
    
    year = year
    teamcode = df_teams.Code.values
    df_riders = pd.DataFrame([])
    
    for code in teamcode:
    
        cq_url = 'https://cqranking.com/men/asp/gen/team.asp?year={}&teamcode={}'.format(year, code)
        
        r = requests.get(cq_url)
        
        soup = bs(r.text.encode('iso-8859-1'),'lxml')
        # find the table that contains 'Rider'
        table = soup.find(lambda t: 'Rider' in t).find_parent('table')
        
        data = []
        header_names = []
        
        rows = table.find_all('tr')
        headers = rows[0].find_all('th')
        for header in headers:
            header_names.append(header.text)
        header_names.append('Country')
        #header_names = [h.replace(u'\xa0', u'') for h in header_names]
        #header_names = filter(None, header_names)
        
        for row in rows[1:]:
            cols = row.find_all('td')
        #    cols = [x.encode('iso-8859-1') for x in cols]
            for col in cols:
                #get all children tags of first td
                img = col.find('img',title=True)
                #extracet all tags joined by ,
                if img is not None:
                    a = img['title']
            column = [ele.text.strip() for ele in cols]
        #    column = filter(None, column)
            #add tag value for each row
            column.append(a)
            data.append(column)
        
        df = pd.DataFrame.from_records(data, columns = header_names)
        df['team'] = code
        df.drop(df.tail(1).index,inplace=True)
        df.replace('',np.nan,inplace=True)
        df.dropna(axis=1,how='all',inplace=True)
    
        df_riders = pd.concat([df_riders,df],ignore_index=True,sort=False)
    
    cols = list(df_riders)
    cols.insert(0, cols.pop(cols.index('team')))
    df_riders = df_riders.loc[:,cols]
    df_riders.rename(columns={'A':'rank_start','B':'point_start','C':'rank_end','D':'point_end'},inplace=True)
    
    df_riders.replace('-',np.nan,inplace=True)
    df_riders['rank_start']=df_riders['rank_start'].astype('float')
    df_riders['rank_end']=df_riders['rank_end'].astype('float')
    df_riders['point_start']=df_riders['point_start'].astype('float')
    df_riders['point_end']=df_riders['point_end'].astype('float')
    
    df_riders.to_csv('riders_{}.csv'.format(year),index=False,encoding='iso-8859-1')
    print(df_riders.head())
    
    return df_riders