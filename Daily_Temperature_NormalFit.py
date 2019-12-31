#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 16:36:07 2019

@author: Steve
"""
        
## In this sample script I seek to understand how weather variance differs between Chicago and Denver
## I am using two methods...
## 1. Using daily data, the goodness of fit to a normal distribution and levels of skewness and kurtosis are calculated for daily highs and ows
## 2. Using full ASOS data, the power spectrums are determined for temperatuers at each station

import pandas as pd
import scipy
import numpy as np
import math
import scipy.stats 
import matplotlib.pyplot as plt
from datetime import datetime

## Part 1 daily data
## Since this data needs only be updated annually it is downloaded and imported
ORD_Daily=pd.read_csv("ORD_Daily.csv")
DEN_Daily=pd.read_csv("DEN_Daily.csv")

## This function will output the statisics we are looking for
## Moments 1 (mean), 2 (std), 3 (skewness), 4 (kurtosis), an the normal goodness of fit

def dailystats (data):
    avg=np.mean(data)
    std=np.std(data)
    skw=scipy.stats.skew(data)
    kurt=scipy.stats.kurtosis(data)
    norm_p = scipy.stats.normaltest(data)[1]
    return [avg,std,skw,kurt,norm_p]

    
## This one plots the normal distribution over a histogram
def normplot (data,city,month,time):
    '''
    The four inputs are as follows
    1. The array of temperatures
    2. The name of the City the calculations are being produced for (for plot title and output file)
    3. The month of the year
    4. Whether high or low temparetues are being plotted
    Note: The first input is an array, the other three need to be strings
    '''
    avg,std=scipy.stats.norm.fit(data)
    low=math.floor(min(data))
    high=math.ceil(max(data))+1
    x=np.arange(low,high)
    plt.figure(figsize=(12,9))
    plt.hist(data,bins=x,weights=np.ones(len(data))/len(data),edgecolor='k')
    nfit=scipy.stats.norm.pdf(x,avg,std)
    plt.plot(x,nfit,color='r')
    plt.title("Normal fit for {} {} Temperatures in {}\n Mean={} Std={}".format(city,time,month,avg.round(2),std.round(2)),fontsize=20)
    plt.ylabel("Fraction of Days",fontsize=15)
    plt.xlabel("{} Temperatures".format(time.capitalize()),fontsize=15)
    filename = "{}_{}_{}_Temp_normfit.png".format(city,month,time)
    plt.savefig(filename)
    
## The list of city names and assocciated station codes

cities={"Chicago","Denver"}
city_codes={
        "Chicago":"ORD",
        "Denver":"DEN"
        }

HighTemp_Stats=pd.DataFrame(columns=["City","Month","Avg","STD","Skew","Kurt","Norm_PValue"])
LowTemp_Stats=pd.DataFrame(columns=["City","Month","Avg","STD","Skew","Kurt","Norm_PValue"])
    
for city in cities:
    code = city_codes[city]
    
## Open the file
    Daily=pd.read_csv("{}_Daily.csv".format(code))
    
## determine the month of the year from the date field
    Daily["Date"]= [datetime.strptime(date,"%Y-%m-%d").date() for date in Daily["DATE"]]
    Daily["Month"]=[date.strftime("%B") for date in Daily["Date"]]
    
## This line gets all the months in the current data set- there should be 12, but this may not always be the case
    months=np.unique(Daily["Month"])
    
## runs high and low temperature stats and generates charts for each month
    for m in months:
        
## High temperatures
        Highs = Daily["TMAX"][Daily["Month"]==m]
        Highs=Highs.dropna()
        High_data=dailystats(Highs)
        High_data.insert(0,m)
        High_data.insert(0,city)
        HighTemp_Stats.loc[len(HighTemp_Stats),:]=High_data
        
## Low Temperatures
        Lows = Daily["TMIN"][Daily["Month"]==m]
        Lows=Lows.dropna()
        Low_data=dailystats(Lows)
        Low_data.insert(0,m)
        Low_data.insert(0,city)
        LowTemp_Stats.loc[len(LowTemp_Stats),:]=Low_data
        
## Now to produce the charts
        
        normplot(Highs,city,m,"High")
        normplot(Lows,city,m,"Low")
        
        
##Outside the loop we will output the two arrays into an excel file
        
writer = pd.ExcelWriter('./Temperature_Statistics.xlsx', engine='xlsxwriter')
HighTemp_Stats.to_excel(writer,sheet_name="Highs")
LowTemp_Stats.to_excel(writer,sheet_name="Lows")
writer.save()


