# Webscraper for daily information on Temperature
# and Relative Humidity in the Philippines
# source: http://bagong.pagasa.dost.gov.ph/weather

# Import needed libraries
import requests, bs4
import pandas as pd
from datetime import datetime, timedelta

def scrape_DailyWeather():
    # Request and download webpage
    # Create a request object connecting to PAGASA Website
    # and downloading its webpage contents.
    res = requests.get('http://bagong.pagasa.dost.gov.ph/weather')
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    # Create an html file store there the contents of the requested webpage    
    temp = open('temp.html','w')
    temp.write(res.text)
    temp.close()

    # Use BeautifulSoup4 to parse from temp.html
    soup = bs4.BeautifulSoup(open('temp.html'), features='lxml')
    # Parse the tables on the webpage
    str_tables = str(soup.select('table.table'))

    # Parse further separating the different tables
    str_tables_split = str_tables[1:-1].split('>,')
    _01_forecast_weather            = str_tables_split[0] + '>' # Forecast Weather Conditions
    _02_forecast_wind_coastalwater  = str_tables_split[1] + '>' # Forecast Wind and Coastal Water Conditions
    _03_temp_RH                     = str_tables_split[2] + '>' # Temperature and Relative Humidity
    _04_tides_astro_info            = str_tables_split[3] + '>' # Tides and Astronomical Information Over Metro Manila

    # Create initial DataFrame:
    TempRH = pd.read_html(_03_temp_RH)

    # DATA CLEANING
    # Apparently the whole dataframe got enclosed on a square bracket
    # which makes it a python list having only one element-- the DataFrame.
    # Since the whole dataframe is the only element on the list...
    TempRH = TempRH[0]

    # Correct column headers
    # Create a dictionary to map the corrections on column names
    col_rename = {}
    new_cols = ['Parameter', 'Max Value', 'Max Time', 'Min Value', 'Min Time']
    i = 0
    for col in list(TempRH.columns):
        col_rename[col] = new_cols[i]
        i += 1
    # Apply corrections
    TempRH = TempRH.rename(columns=col_rename)

    # Add a column stating the date of observation which is yesterday
    # So we'll just have to subract 1 day from current date
    date_observed = datetime.now() - timedelta(days=1)
    TempRH['Date of Observation'] = date_observed.strftime("%m/%d/%Y")

    # Add a column stating the date and time of data issuance
    datetime_issued = soup.find_all('h5',class_='pull-right dev')[0].get_text().split(',')
    date_issued = datetime_issued[1]
    time_issued = ' '.join(datetime_issued[0].split()[2:])
    TempRH['Data Issued'] = "{}, {}".format(date_issued,time_issued)

    # Parse dates under 'Date & Time' column
    TempRH['Data Issued'] = pd.to_datetime(TempRH['Data Issued'])

    # Rearrange columns making 'Date of Observation as the first column
    TempRH = TempRH[['Date of Observation', 'Parameter', 'Max Value', 'Max Time', 'Min Value', 'Min Time','Data Issued']]

    # Convert pandas dataframe to csv file
    # filename must have a datestamp appended.
    # Create a filename for the csv containing a timestamp
    datetime_split = str(date_observed).split() # ['yyyy-mm-dd','hh:mm:ss.xxxxxx']
    datestamp = datetime_split[0] # 'yyyy-mm-dd'
    filename = "PH_TempRH_" + datestamp + ".csv"

    # Convert pandas dataframe into a csv file
    TempRH.to_csv(filename, sep=',', header=True, index=False)

    # Report output:
    print("File created last " + str(datetime.now()) + ": " + filename)
    print(TempRH)
