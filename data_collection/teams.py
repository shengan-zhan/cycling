# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 17:11:40 2019

@author: Shengan
"""

import requests
import lxml
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

def teams(year):
    cq_url = 'https://cqranking.com/men/asp/gen/searchTeams.asp'
    
    year = year
    level = 'WT'
    levels_dict = {'C':1 ,'PC':2 ,'WT':3}
    
    payload = {
            'listYears':year,
            'listNats':0,
            'listClasses':levels_dict[level],
            'butSearch':' Search '
            }
    r = requests.post(cq_url,data=payload)
    soup = bs(r.text.encode('iso-8859-1'),'lxml')
    table = soup.find(lambda t: 'Nbr' in t).find_parent('table')
    
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
            img = col.find('img')
            #extracet all tags joined by ,
            if img is not None:
                a = img['title']
        column = [ele.text.strip() for ele in cols]
    #    column = filter(None, column)
        #add tag value for each row
        column.append(a)
        data.append(column)
    
    df_teams = pd.DataFrame.from_records(data, columns = header_names)
    df_teams.replace('',np.nan,inplace=True)
    df_teams.dropna(axis=1,how='all',inplace=True)
    df_teams.drop('Site',axis=1,inplace=True)
    df_teams.to_csv('teams_{}.csv'.format(year),index=False,encoding='iso-8859-1')
    
    return df_teams