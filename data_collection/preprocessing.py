# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 10:11:11 2019

@author: Shengan
"""

import pandas as pd
import numpy as np

def get_race_performance(results, race_name,abbrev):
    df_results = results
    df_race = df_results.loc[df_results['Race'].str.contains(race_name.decode('utf-8')),:]
    riders = df_race['Rider'].unique()
    points_sum = []
    wins = []
    podiums = []
    top_tens = []
    for r in riders:
        df_r = df_race[df_race['Rider']==r]
        points_sum.append(df_r['CQ'].sum())
        wins.append(df_r.loc[df_r['Rank']==1,'Race'].count())
        podiums.append(df_r.loc[df_r['Rank'].between(1,3),'Race'].count())
        top_tens.append(df_r.loc[df_r['Rank'].between(1,10),'Race'].count())

    df_race_performance = pd.DataFrame(
        {'riders': riders,
         'win': wins,
         'podium': podiums,
         'top_ten': top_tens,
         'points': points_sum,
        },columns=['riders','win','podium','top_ten','points'])
    df_race_performance = df_race_performance.add_suffix('_{}'.format(abbrev))
    
    return df_race_performance

def get_pre_tdf_performance(year):
    df_riders = pd.read_csv(r'E:\cycling\cycling\data\riders_{}.csv'.format(year),encoding='iso-8859-1')
    df_rider_results = pd.read_csv(r'E:\cycling\cycling\data\rider_results_{}.csv'.format(year),encoding='iso-8859-1')
    
    df_results = df_rider_results.merge(df_riders,on='Rider',how='inner',suffixes=('_l','_r'))
    
    df_results['Rank'] = df_results['Rank'].replace('leader',0)
    df_results['Rank'] = df_results['Rank'].replace('DNF',-1)
    df_results['Rank'] = df_results['Rank'].replace('OOT',-2)
    df_results['Rank'] = df_results['Rank'].replace('-',np.nan)
    df_results['Rank'] = df_results['Rank'].replace('DNS',-5)
    df_results['Rank'] = df_results['Rank'].replace('DQ',-10)
    df_results['Rank'] = df_results['Rank'].astype(float)
    
    df_results['Date'] = pd.to_datetime(df_results['Date'],format='%d/%m/%Y')
    
    df_tdf_gc = df_results.loc[df_results['Race']=='Tour de France',['Rider','Rank','rank_start','point_start']]
    
    tdf_riders = df_tdf_gc.Rider.values
    
    mask = (df_results['Date'] < '{}-07-01'.format(year))
    df_pre_tdf = df_results.loc[mask]
    
    points_sum = []
    race_days = []
    wins = []
    podiums = []
    top_tens = []
    for r in tdf_riders:
        df_r = df_pre_tdf[df_pre_tdf['Rider']==r]
        points_sum.append(df_r['CQ'].sum())
        race_days.append(df_r['Race'].count())
        wins.append(df_r.loc[df_r['Rank']==1,'Race'].count())
        podiums.append(df_r.loc[df_r['Rank'].between(1,3),'Race'].count())
        top_tens.append(df_r.loc[df_r['Rank'].between(1,10),'Race'].count())
       
    df_performance = pd.DataFrame(
        {'riders': tdf_riders,
         'win': wins,
         'podium': podiums,
         'top_ten': top_tens,
         'points': points_sum,
         'race_days': race_days,
        },columns=['riders','win','podium','top_ten','points','race_days'])
        
    df_dauphine_perform = get_race_performance(df_results, 'Critérium du Dauphiné', 'dauphine')
    df_swiss_perform = get_race_performance(df_results, 'Tour de Suisse', 'swiss')
    
    df_pre_perform = df_tdf_gc.merge(df_performance,left_on='Rider',right_on='riders',how='left',suffixes=('_l','_r'))
    df_pre_perform = df_pre_perform.merge(df_dauphine_perform,left_on='Rider',right_on='riders_dauphine',how='left')
    df_pre_perform = df_pre_perform.merge(df_swiss_perform,left_on='Rider',right_on='riders_swiss',how='left')
    df_pre_perform['riders_dauphine'].fillna(df_pre_perform['riders_swiss'],inplace=True)
    df_pre_perform['win_dauphine'].fillna(df_pre_perform['win_swiss'],inplace=True)
    df_pre_perform['podium_dauphine'].fillna(df_pre_perform['podium_swiss'],inplace=True)
    df_pre_perform['top_ten_dauphine'].fillna(df_pre_perform['top_ten_swiss'],inplace=True)
    df_pre_perform['points_dauphine'].fillna(df_pre_perform['points_swiss'],inplace=True)
    
    df_pre_perform_clean = df_pre_perform.drop(df_pre_perform.columns[-5:],axis=1)
    df_pre_perform_clean.drop(['riders','riders_dauphine'],axis=1,inplace=True)
    df_pre_perform_clean['tdf_top10'] = (df_pre_perform_clean['Rank'] <= 10).astype(int)
    df_pre_perform_clean.dropna(inplace=True)
    df_pre_perform_clean.set_index('Rider', inplace=True)
    
    df_X = df_pre_perform_clean.iloc[:,1:-1]
    df_y = pd.DataFrame(df_pre_perform_clean.iloc[:,-1])
    
#    df_X.to_csv('E:\cycling\cycling\data\X_train.csv',encoding='iso-8859-1')
#    df_y.to_csv('E:\cycling\cycling\data\y_train.csv',encoding='iso-8859-1')
    
    return df_X, df_y