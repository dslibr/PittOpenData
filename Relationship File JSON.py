#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 11:38:09 2019

@author: lisaover
"""

import urllib.request
import csv
import pandas as pd

# download the text file from the Census Bureau
rFileURL = 'https://www2.census.gov/geo/docs/maps-data/data/rel/trf_txt/pa42trf.txt'
urllib.request.urlretrieve(rFileURL, '/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Data/pa42trf.txt')
    
"""
https://stackoverflow.com/questions/20347766/pythonically-add-header-to-a-csv-file
"""
# create header fields
header = ['STATE00', 'COUNTY00', 'TRACT00', 'GEOID00', 'POP00', 'HU00', 'PART00', 'AREA00', 'AREALAND00', 'STATE10', 'COUNTY10', 'TRACT10', 'GEOID10', 'POP10', 'HU10', 'PART10', 'AREA10', 'AREALAND10', 'AREAPT', 'AREALANDPT', 'AREAPCT00PT', 'AREALANDPCT00PT', 'AREAPCT10PT', 'AREALANDPCT10PT','POP10PT', 'POPPCT00', 'POPPCT10', 'HU10PT', 'HUPCT00', 'HUPCT10']

# open a new CSV file and write the header fields
# open the downoaded text file and write the contents to the new CSV file
with open('/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Data/pa42trf.csv', 'wt', newline ='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(i for i in header)
    with open('/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Data/pa42trf.txt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            writer.writerow(row)     
file.close()

# get CSV file into a dataframe
data = pd.read_csv("/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Data/pa42trf.csv")

# sort the data by 2010 tract and then 2000 tract
sorted_df = data.sort_values(['TRACT10','TRACT00'])

# create a dataframe from the sorted data with only Allegheny County records
# either TRACT00 or TRACT10 are Allegheny County
allegheny_df = sorted_df.loc[(data['COUNTY00'] == 3) | (data['COUNTY10'] == 3)]

# create two dataframes, one wtih 2000 tracts only in Allegheny and 
# one with 2010 tracts only in Allegheny
allegheny00_df = sorted_df.loc[data['COUNTY00'] == 3]
allegheny10_df = sorted_df.loc[data['COUNTY10'] == 3]
  
# write Allegheny dataframe to CSV - this is the relationship file for Allegheny County 
allegheny_df.to_csv(r'/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Data/pa_allegheny_42003.csv')

"""
https://stackoverflow.com/questions/23330654/update-a-dataframe-in-pandas-while-iterating-row-by-row
https://stackoverflow.com/questions/30673209/pandas-compare-next-row
https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
"""

# create list of 2000 tracts - only those in allegheny
# create a copy of allegheny00_df and take only the TRACT00 column and then only unique values
tracts00 = allegheny00_df.loc[: , ['TRACT00']].copy()
tract_list00 = tracts00['TRACT00'].unique()
tract_list00.sort()

# create list of 2010 tracts - only those in allegheny
# create a copy of allegheny10_df and take only the TRACT10 column and then only unique values
tracts10 = allegheny10_df.loc[: , ['TRACT10']].copy()
tract_list10 = tracts10['TRACT10'].unique()
tract_list10.sort()

# from the above tract lists, create a list of all Allegheny tracts - 2000 or 2010
tract_list = []
for t in tract_list00:
    tract_list.append(t)
for t in tract_list10:
    if t not in tract_list:
        tract_list.append(t)
tract_list.sort()
        
# return index of element in array        
def index_of(elem, a):
    a_e = enumerate(a)
    a_f = list(filter(lambda x: x[1] == elem, a_e))
    if a_f:
        return a_f[0][0]
    else:
        return -1
    
# write JSON file
    
json='{'
for t in tract_list:
    subset_to2010 = allegheny_df.loc[data['TRACT10'] == t]
    subset_from2010 = allegheny_df.loc[data['TRACT00'] == t]
    if (subset_to2010.shape[0] != 0):
        if subset_to2010['COUNTY10'].values[0]==3:
            county='Allegheny'
        elif subset_to2010['COUNTY10'].values[0]==7:
            county='Beaver'
        elif subset_to2010['COUNTY10'].values[0]==19:
            county='Butler'
        elif subset_to2010['COUNTY10'].values[0]==129:
            county='Westmoreland'
    elif (subset_from2010.shape[0] != 0):
        if subset_from2010['COUNTY00'].values[0]==3:
            county='Allegheny'
        elif subset_from2010['COUNTY00'].values[0]==7:
            county='Beaver'
        elif subset_from2010['COUNTY00'].values[0]==19:
            county='Butler'
        elif subset_from2010['COUNTY00'].values[0]==129:
            county='Westmoreland'
    json=json+'"Summary for Tract '+str(t/100)+' ('+county+')" : {'
    json=json+'"Area" : {'
    if (t in tract_list10) & (t not in tract_list00):
            json=json+'"2010 Area" : "'+str(subset_to2010['AREA10'].values[0])+'"'
            json=json+', "Standardized Area" : "Not a Census 2000 tract"'
    elif (t not in tract_list10) & (t in tract_list00):
        json=json+' "2010 Area" : "Not a Census 2010 tract"'
        json=json+', "Standardized Area" : "'+str(subset_from2010['AREA00'].values[0])+'"'
    else:
        json=json+'"2010 Area" : "'+str(subset_to2010['AREA10'].values[0])+'"'
        json=json+', "Standardized Area" : "'+str(subset_from2010['AREA00'].values[0])+'"'
    if (subset_to2010.shape[0] != 0):
        json=json+', "Areas incorporated into tract '+str(t/100)+'" : {'
        for row in subset_to2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')." : '
            else:
                json=json+'"Tract '+str(t2000)+' ('+county00+')." : '
            json=json+'{"Quantity" : "'+str(row.AREAPT)+'"'
            json=json+', "Percentage of 2010" : "'+str(row.AREAPCT10PT)+'"}'
            if (row.Index != subset_to2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    if (subset_from2010.shape[0] != 0):
        json=json+', "Areas transferred out of tract '+str(t/100)+'" : {'
        for row in subset_from2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            json=json+'{"Quantity" : "'+str(row.AREAPT)+'"'
            json=json+', "Percentage of Standardized" : "'+str(row.AREAPCT00PT)+'"}'
            if (row.Index != subset_from2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    json=json+'}, "Land Area" : {'
    if (t in tract_list10) & (t not in tract_list00):
        json=json+'"2010 Land Area" : "'+str(subset_to2010['AREALAND10'].values[0])+'"'
        json=json+', "Standardized Land Area" : "Not a Census 2000 tract"'
    elif (t not in tract_list10) & (t in tract_list00):
        json=json+' "2010 Land Area" : "Not a Census 2010 tract"'
        json=json+', "Standardized Land Area" : "'+str(subset_from2010['AREALAND00'].values[0])+'"'
    else:
        json=json+'"2010 Land Area" : "'+str(subset_to2010['AREALAND10'].values[0])+'"'
        json=json+', "Standardized Land Area" : "'+str(subset_from2010['AREALAND00'].values[0])+'"'
    if (subset_to2010.shape[0] != 0):
        json=json+', "Land areas incorporated into tract '+str(t/100)+'" : {'
        for row in subset_to2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2000)+' ('+county00+')" : '
            json=json+'{"Quantity" : "'+str(row.AREALANDPT)+'"'
            json=json+', "Percentage of 2010" : "'+str(row.AREALANDPCT10PT)+'"}'
            if (row.Index != subset_to2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    if (subset_from2010.shape[0] != 0):
        json=json+', "Land areas transferred out of tract '+str(t/100)+'" : {'
        for row in subset_from2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            json=json+'{"Quantity" : "'+str(row.AREALANDPT)+'"'
            json=json+', "Percentage of Standardized" : "'+str(row.AREALANDPCT00PT)+'"}'
            if (row.Index != subset_from2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    json=json+'}, "Population" : {'
    if (t in tract_list10) & (t not in tract_list00):
        json=json+'"2010 Population" : "'+str(subset_to2010['POP10'].values[0])+'"'
        json=json+', "Standardized Population" : "Not a Census 2000 tract"'
    elif (t not in tract_list10) & (t in tract_list00):
        json=json+' "2010 Population" : "Not a Census 2010 tract"'
        json=json+', "Standardized Population" : "'+str(subset_from2010['POP00'].values[0])+'"'
    else:
        json=json+'"2010 Population" : "'+str(subset_to2010['POP10'].values[0])+'"'
        json=json+', "Standardized Population" : "'+str(subset_from2010['POP00'].values[0])+'"'
    if (subset_to2010.shape[0] != 0):
        json=json+', "Population incorporated into tract '+str(t/100)+'" : {'
        for row in subset_to2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2000)+' ('+county00+')" : '
            json=json+'{"Quantity" : "'+str(row.POP10PT)+'"'
            json=json+', "Percentage of 2010" : "'+str(row.POPPCT10)+'"}'
            if (row.Index != subset_to2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    if (subset_from2010.shape[0] != 0):
        json=json+', "Population transferred out of tract '+str(t/100)+'" : {'
        for row in subset_from2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            json=json+'{"Quantity" : "'+str(row.POP10PT)+'"'
            json=json+', "Percentage of Standardized" : "'+str(row.POPPCT00)+'"}'
            if (row.Index != subset_from2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    json=json+'}, "Housing Units" : {'
    if (t in tract_list10) & (t not in tract_list00):
        json=json+'"2010 Housing Units" : "'+str(subset_to2010['HU10'].values[0])+'"'
        json=json+', "Standardized Housing Units" : "Not a Census 2000 tract"'
    elif (t not in tract_list10) & (t in tract_list00):
        json=json+' "2010 Housing Units" : "Not a Census 2010 tract"'
        json=json+', "Standardized Housing Units" : "'+str(subset_from2010['HU00'].values[0])+'"'
    else:
        json=json+'"2010 Housing Units" : "'+str(subset_to2010['HU10'].values[0])+'"'
        json=json+', "Standardized Housing Units" : "'+str(subset_from2010['HU00'].values[0])+'"'
    if (subset_to2010.shape[0] != 0):
        json=json+', "Housing units incorporated into tract '+str(t/100)+'" : {'
        for row in subset_to2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2000)+' ('+county00+')" : '
            json=json+'{"Quantity" : "'+str(row.HU10PT)+'"'
            json=json+', "Percentage of 2010" : "'+str(row.HUPCT10)+'"}'
            if (row.Index != subset_to2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    if (subset_from2010.shape[0] != 0):
        json=json+', "Housing units transferred out of tract '+str(t/100)+'" : {'
        for row in subset_from2010.itertuples():
            t2000 = row.TRACT00/100
            t2010 = row.TRACT10/100
            if row.COUNTY00==3:
                county00='Allegheny'
            elif row.COUNTY00==7:
                county00='Beaver'
            elif row.COUNTY00==19:
                county00='Butler'
            elif row.COUNTY00==129:
                county00='Westmoreland'
            if row.COUNTY10==3:
                county10='Allegheny'
            elif row.COUNTY10==7:
                county10='Beaver'
            elif row.COUNTY10==19:
                county10='Butler'
            elif row.COUNTY10==129:
                county10='Westmoreland'
            if (row.TRACT00 == row.TRACT10):
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            else:
                json=json+'"Tract '+str(t2010)+' ('+county10+')" : '
            json=json+'{"Quantity" : "'+str(row.HU10PT)+'"'
            json=json+', "Percentage of Standardized" : "'+str(row.HUPCT00)+'"}'
            if (row.Index != subset_from2010.index[-1]):
                json=json+','
            else:
                json=json+'}'
    json=json+'}}'
    if tract_list.index(t) == len(tract_list)-1:
        json=json+'}'
    else:
        json=json+','

with open("/Users/lisaover/Google Drive/_MLIS/Open Data/WPRDC Data Sharing Project 12_3/Allegheny Project Final/Documentation/pa_allegheny_42003.json", "w") as file:
    file.write(json)
