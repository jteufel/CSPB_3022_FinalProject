import numpy as np
import scipy as sp
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
import io
import requests
import json
from categories import month_years,demographics,income_levels,age_distribution,education_levels,houseing_levels


def Get_Online_Data(columns,row_count,file_url):

    #return dataframe with data csv url
    #https://stackoverflow.com/questions/32400867/pandas-read-csv-from-url

    r = requests.get(file_url).content #get content from http request
    decoded_file = io.StringIO(r.decode('utf-8'))
    df = pd.read_csv(decoded_file,nrows = row_count, usecols = columns) # add new csv lines(crimes) to dataframe
    df.FIRST_OCCURRENCE_DATE, df.LAST_OCCURRENCE_DATE = pd.to_datetime(df.FIRST_OCCURRENCE_DATE),pd.to_datetime(df.LAST_OCCURRENCE_DATE)

    return df

def Add_Crime_Columns(census_df,crime_df,crime_string):

        neighborhood_totals = crime_df[crime_df.OFFENSE_CATEGORY_ID == crime_string].groupby("NEIGHBORHOOD_ID")['OFFENSE_ID'].count()
        neighborhood_totals = neighborhood_totals.reset_index()
        neighborhood_totals.rename(columns = {'OFFENSE_ID':crime_string}, inplace = True)

        return census_df.merge(neighborhood_totals, on = 'NEIGHBORHOOD_ID')

def Add_AllCrimes_Columns(census_df,crime_df):

        neighborhood_totals = crime_df.groupby("NEIGHBORHOOD_ID")['OFFENSE_ID'].count()
        neighborhood_totals = neighborhood_totals.reset_index()
        neighborhood_totals.rename(columns = {'OFFENSE_ID':'all_crimes'}, inplace = True)

        return census_df.merge(neighborhood_totals, on = 'NEIGHBORHOOD_ID')

def Add_Crime_Columns_ByYear(census_df,crime_df,crime_string,neighborhoods_difference,years_difference):

        neighborhood_totals = crime_df[crime_df.OFFENSE_CATEGORY_ID == crime_string]
        neighborhood_totals = neighborhood_totals.groupby(["NEIGHBORHOOD_ID","year"])['OFFENSE_ID'].count()
        neighborhood_totals = neighborhood_totals.reset_index()
        neighborhood_totals.rename(columns = {'OFFENSE_ID':crime_string}, inplace = True)

        for n in neighborhoods_difference:
            idx = neighborhood_totals[neighborhood_totals.NEIGHBORHOOD_ID == n].index
            #print(idx)
            neighborhood_totals = neighborhood_totals.drop(idx)

        for y in years_difference:
            idx = neighborhood_totals[neighborhood_totals.year == y].index
            #print(idx)
            neighborhood_totals = neighborhood_totals.drop(idx)

        return census_df.merge(neighborhood_totals, on = ['NEIGHBORHOOD_ID','year'])


def Add_CensusData_ByYear(census_df,neighborhoods_difference):

        for n in neighborhoods_difference:
            idx = census_df[census_df.NEIGHBORHOOD_ID == n].index
            census_df = census_df.drop(idx)

        return census_df#.append([census_df]*2,ignore_index=True)


def Add_Crime_Rates(census_df,crime):

        str = crime +"_rate"
        census_df[str] = census_df[crime]/census_df['TTL_POPULATION_ALL']
        return census_df


if __name__ == "__main__":




    #use this code if you don't want to download the crime csv
    #file_url = "https://www.denvergov.org/media/gis/DataCatalog/crime/csv/crime.csv"
    #crime_df = Get_Online_Data(columns,10000,file_url)

    #paths to all the csv's
    crime_file = "data/crime.csv"
    census_file = "data/american_community_survey_nbrhd_2014_2018.csv"
    zillow_rentals_file = "data/Neighborhood_Zri_AllHomesPlusMultifamily.csv"
    zillow_saleprices_file = "data/Sale_Prices_Neighborhood.csv"


    crime_columns = ["OFFENSE_ID","OFFENSE_TYPE_ID","OFFENSE_CATEGORY_ID","FIRST_OCCURRENCE_DATE","LAST_OCCURRENCE_DATE","NEIGHBORHOOD_ID","INCIDENT_ADDRESS"]

    #columns for the cencus dataframe and zillow housing prices DataFrame
    census_columns = ["NBHD_NAME","TTL_POPULATION_ALL"] + demographics + income_levels + houseing_levels + age_distribution + education_levels
    zillow_columns = ["RegionName","StateName"] + month_years

    #create dataframe from the crime data
    crime_df = pd.read_csv(crime_file, usecols = crime_columns)
    crime_df['NEIGHBORHOOD_ID'] = crime_df['NEIGHBORHOOD_ID'].str.replace('-',' ')
    crime_df['year'] = pd.DatetimeIndex(crime_df["FIRST_OCCURRENCE_DATE"]).year


    #create dataframe from the census data and list of all unique neighborhoods
    census_df = pd.read_csv(census_file, usecols = census_columns)
    census_df.rename(columns = {"NBHD_NAME":"NEIGHBORHOOD_ID"}, inplace = True)
    census_df["NEIGHBORHOOD_ID"] = census_df["NEIGHBORHOOD_ID"].str.lower()

    #add new statistics for minority percentage & percentage of those with a college degree
    census_df["PCT_MINORITY"] = census_df["PCT_HISPANIC"] + census_df["PCT_BLACK"]
    census_df['COLLEGE_RATE'] = census_df['BACHELORS_OR_HIGHER_EDU']/census_df['TTL_POPULATION_ALL']

    #list of crimes tp analyze
    crimes = ["theft-from-motor-vehicle","drug-alcohol","burglary","auto-theft","public-disorder","sexual-assault"]

    #add crime counts & rates  to the dataframe
    for crime in crimes:
        census_df = Add_Crime_Columns(census_df,crime_df,crime)
        census_df = Add_Crime_Rates(census_df,crime)


    census_df = Add_AllCrimes_Columns(census_df,crime_df)
    census_df['ttl_crime_rate'] = census_df['all_crimes']/census_df['TTL_POPULATION_ALL']

    #exploratary data analysis

    ttl_pp = census_df2[["ttl_crime_rate",'MEDIAN_HOME_VALUE','AVG_HH_INCOME',"COLLEGE_RATE","PCT_MINORITY"]]
    autotheft_pp = census_df2[["auto-theft_rate",'MEDIAN_HOME_VALUE','AVG_HH_INCOME',"COLLEGE_RATE","PCT_MINORITY"]]
    burglary_pp = census_df2[["burglary_rate",'MEDIAN_HOME_VALUE','AVG_HH_INCOME',"COLLEGE_RATE","PCT_MINORITY"]]

    plt.figure()

    sns.pairplot(census_df_filtered)

    plt.show()

    #plt.plot(census_df2["MEDIAN_HOME_VALUE"], census_df2["burglary_rate"], 'bo')





    #first model
    #model_burglary = smf.ols(formula='burglary_rate ~ PER_CAPITA_INCOME*AVG_HH_INCOME*MEDIAN_EARNINGS', data=census_df).fit()

    #second model
    #model_burglary = smf.ols(formula='burglary_rate ~ AVG_HH_INCOME*MEDIAN_EARNINGS', data=census_df).fit()

    #census_df = census_df.drop([41,10,21,24,73,53])

    #third model
    #model_burglary = smf.ols(formula='burglary_rate ~ AVG_HH_INCOME*MEDIAN_EARNINGS', data=census_df).fit()

    #final model

    #census_df = census_df.drop([41,10,21,24,73,53,14,68,29,9,19,18,27,20,35,62,43,58,26,25,22,54,57,40,47,52,61,64])

    #model_burglary = smf.ols(formula='burglary_rate ~ PER_CAPITA_INCOME*AVG_HH_INCOME*MEDIAN_EARNINGS', data=census_df).fit()
    #print(model_burglary.summary())

    #plt.figure()

    #plt.plot(census_df["PER_CAPITA_INCOME"], census_df["burglary_rate"], 'bo')

    #sm.graphics.plot_leverage_resid2(model_burglary, alpha=0.05);
    #plt.show()


    #load in zillow sales data
    zillow_sales_df = pd.read_csv(zillow_saleprices_file, usecols = zillow_columns)

    #filter all colorado neighborhoods out of the zillow sales csv
    colorado_sales_df = zillow_sales_df[zillow_sales_df.StateName == "Colorado"]
    colorado_sales_df["RegionName"] = colorado_sales_df["RegionName"].str.lower()

    #get neighborhood & years difference and intersection for dataframe merging
    neighborhoods_zillow = set(colorado_sales_df["RegionName"])
    neighborhoods = set(census_df["NEIGHBORHOOD_ID"])
    years_c = set(crime_df["year"])
    neighborhoods_intersection = list(neighborhoods.intersection(neighborhoods_zillow))
    neighborhoods_difference = list(neighborhoods.difference(neighborhoods_zillow))
    years_difference = list(years_c.difference({2017,2018,2019}))


    #make new dataframe for all the denver sales data
    denver_sales_df = pd.DataFrame([], columns = colorado_sales_df.columns)


    for neighborhood in neighborhoods_intersection:
        denver_sales_df = denver_sales_df.append(colorado_sales_df[colorado_sales_df.RegionName == neighborhood])

    #not proud of these 3 lines of code
    #make a column for annual sales averages
    denver_sales_df["2017"] = (denver_sales_df["2017-01"] + denver_sales_df["2017-02"] + denver_sales_df["2017-03"] + denver_sales_df["2017-04"] + denver_sales_df["2017-05"] + denver_sales_df["2017-06"] + denver_sales_df["2017-07"] + denver_sales_df["2017-08"] + denver_sales_df["2017-09"] + denver_sales_df["2017-10"] + denver_sales_df["2017-11"] + denver_sales_df["2017-12"])/12
    denver_sales_df["2018"] = (denver_sales_df["2018-01"] + denver_sales_df["2018-02"] + denver_sales_df["2018-03"] + denver_sales_df["2018-04"] + denver_sales_df["2018-05"] + denver_sales_df["2018-06"] + denver_sales_df["2018-07"] + denver_sales_df["2018-08"] + denver_sales_df["2018-09"] + denver_sales_df["2018-10"] + denver_sales_df["2018-11"] + denver_sales_df["2018-12"])/12
    denver_sales_df["2019"] = (denver_sales_df["2019-01"] + denver_sales_df["2019-02"] + denver_sales_df["2019-03"] + denver_sales_df["2019-04"] + denver_sales_df["2019-05"] + denver_sales_df["2019-06"] + denver_sales_df["2019-07"] + denver_sales_df["2019-08"] + denver_sales_df["2019-09"] + denver_sales_df["2019-10"] + denver_sales_df["2019-11"] + denver_sales_df["2019-12"])/12


    #make new census dataframe that includes annual sales dataframe
    #rather than a row for each neighborhood - there is a row for each year-neightborhood combo
    #we'll use only 2017, 2018 and 2019 because those are the only complete years in the crime csv

    census_df2 = pd.DataFrame([], columns = [])

    idx = 0
    for year in [2017,2018,2019]:
        for neighborhood in neighborhoods_intersection:
            try:
                temp = int(denver_sales_df[denver_sales_df.RegionName == neighborhood][str(year)])
            except:
                temp = denver_sales_df[denver_sales_df.RegionName == neighborhood][str(year)]

            temp_df = pd.DataFrame({"NEIGHBORHOOD_ID":neighborhood,"year":year,"MEDIAN_HOME_VALUE":temp}, index=[idx])
            census_df2 = census_df2.append(temp_df, ignore_index=True)
            idx +=1

    #add crime statistics for 2017,2018,and 2019 for each neighborhood
    for crime in crimes:
        census_df2 = Add_Crime_Columns_ByYear(census_df2,crime_df,crime,neighborhoods_difference,years_difference)

    #add census data from original census dataframe
    census_df_m = census_df[["TTL_POPULATION_ALL","PCT_MINORITY","COLLEGE_RATE",'PER_CAPITA_INCOME','AVG_HH_INCOME','AVG_FAM_INCOME','MEDIAN_EARNINGS','NEIGHBORHOOD_ID']]
    census_df2 = census_df2.merge(Add_CensusData_ByYear(census_df_m,neighborhoods_difference), on = 'NEIGHBORHOOD_ID')

    #need to add ttl crimes column
    for crime in crimes:
        census_df2 = Add_Crime_Rates(census_df2,crime)

    #crimes = ["theft-from-motor-vehicle","drug-alcohol","burglary","auto-theft","public-disorder","sexual-assault"]

    census_df_filtered = census_df2[["burglary_rate",'MEDIAN_HOME_VALUE','AVG_HH_INCOME',"COLLEGE_RATE","PCT_MINORITY"]]


    plt.figure()

    sns.pairplot(census_df_filtered)

    #plt.plot(census_df2["MEDIAN_HOME_VALUE"], census_df2["burglary_rate"], 'bo')

    plt.show()



    #new model
    #model_burglary = smf.ols(formula='burglary_rate ~ MEDIAN_HOME_VALUE', data=census_df2).fit()


    """

    #get crime totals
    neighborhood_totals = crime_df[crime_df.OFFENSE_CATEGORY_ID == "theft-from-motor-vehicle"].groupby("NEIGHBORHOOD_ID")['OFFENSE_ID'].count()
    neighborhood_totals = neighborhood_totals.reset_index()
    neighborhood_totals['NEIGHBORHOOD_ID'] = neighborhood_totals['NEIGHBORHOOD_ID'].str.replace('-',' ')
    neighborhood_totals.rename(columns = {'OFFENSE_ID':'TOTAL_CRIMES'}, inplace = True)

    print(census_df.head(200))
    print(neighborhood_totals.head(200))

    census_df = census_df.merge(neighborhood_totals, on = 'NEIGHBORHOOD_ID')

    print(census_df['TOTAL_CRIMES'].head())

    zillow_sales_df = pd.read_csv(zillow_saleprices_file, usecols = zillow_columns)
    colorado_sales_df = zillow_sales_df[zillow_sales_df.StateName == "Colorado"]
    neighborhoods_zillow = set(colorado_sales_df["RegionName"])

    neighborhoods_intersection = list(neighborhoods.intersection(neighborhoods_zillow))

    denver_sales_df = pd.DataFrame([], columns = colorado_sales_df.columns)

    for neighborhood in neighborhoods_intersection:
        denver_sales_df = denver_df.append(colorado_sales_df[colorado_sales_df.RegionName == neighborhood])
        """
