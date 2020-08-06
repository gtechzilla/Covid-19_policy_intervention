## Importing the libraries:
import os, sys

import cachetools.func

import matplotlib
import matplotlib.colors as colors
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

import seaborn as sns
sns.set()

#-----      
#-----
def fix_region_name(df, pairs = [["Mainland China", "China"]]):
  # fix region names
  for p in pairs:
    df['Country/Region'] = df['Country/Region'].str.replace(p[0],p[1])
  return df
#-----
def merge_df_data(df1,df2):
  return pd.merge(df1, df2,how='left' ,on=['Province/State','Country/Region'])
#-----
def str_add_func(*args):      
  out = []
  for x in args:
    if isinstance(x,str):
      out.append(x)
  
  return '_'.join(out)
class covid_data():
  '''
  Python class to obtain global COVID19 data from 
  John Hopkins GIT repository. This data is updated daily, 
  and the most upto date information available on the web.  
  '''
  def __init__(self,**kwargs):
    #
    nrow = kwargs.get('nrow',None)
    self.confirmed, self.dead, self.recovered = self.get_csseg_data(nrow=nrow)
  @staticmethod
  def create_ts(df):
    ts=df
    columns = ts['region']
    ts=ts.drop(['Province/State', 
                'Country/Region',
                'Lat', 
                'Long',
                'Population'], 
               axis=1).set_index('region').T    
    ts.columns = columns 
    ts=ts.fillna(0)
    #
    ts.index.name = 'Date'
    return ts
  def search_agg(self, name,col='Country/Region',ts=True):
    
    if not isinstance(name,list):
      name = [name]
    out = {}
    for k,v in {'confirmed':self.confirmed,
                'dead':self.dead,
                'recovered':self.recovered}.items():
      #pd.columns(columns=)
      df_list= []     
      for n in name:
        df = v[v[col]==n].set_index(col).filter(regex='/20')
        df_list.append(df.sum(axis=0))
      df = pd.concat(df_list,axis=1, sort=False)
      df.columns = name
      out[k] = df
      # if ts:                
      #   out[k] = self.create_ts(df)
      # else:
      #   out[k] = df.T
    return out
  def search(self, name,col='Country/Region',ts=True):
    
    if not isinstance(name,list):
      name = [name]
    out = {}
    for k,v in {'confirmed':self.confirmed,
                'dead':self.dead,
                'recovered':self.recovered}.items():
      if ts:                
        out[k] = self.create_ts(v[v[col].map(lambda x: x in name)])
      else:
        out[k] = v[v[col] in name].T
    
    return out
  @cachetools.func.ttl_cache(maxsize=128, ttl=24 * 60)
  def get_csseg_data(self, nrow=None):
    
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
    path = f'{url}/csse_covid_19_data/csse_covid_19_time_series' 
    # 
    
    url = f'{path}/time_series_covid19_confirmed_global.csv'
    confirmed = fix_region_name(pd.read_csv(url, nrows=nrow, error_bad_lines=False))
    #
    url = f'{path}/time_series_covid19_deaths_global.csv'
    dead = fix_region_name(pd.read_csv(url, nrows=nrow, error_bad_lines=False))
    #
    url = f'{path}/time_series_covid19_recovered_global.csv'
    
    recovered = fix_region_name(pd.read_csv(url, nrows=nrow, error_bad_lines=False))
    print(confirmed.head())
    #
    return confirmed, dead, recovered  

cd = covid_data()
countries = ['Kenya']
mm = cd.search_agg(countries)  

for ix, ctype in enumerate(['confirmed', 'dead', 'recovered']):
  df = mm[ctype].stack().reset_index()
  #print(df.head())
  df = df.rename(columns={'level_0':'date','level_1':'country',0:ctype})     
  if ix==0:
    df['date'] = pd.to_datetime(df['date'])
    dfall = df
  else:
    dfall[ctype] = df[ctype]
dfall.to_csv('kenya_data.csv')