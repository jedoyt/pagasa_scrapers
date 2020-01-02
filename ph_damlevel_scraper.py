# Webscraper for daily information on dams in the Philippines
# source: http://bagong.pagasa.dost.gov.ph/flood

# Import needed libraries
import requests, bs4, datetime
import pandas as pd

def scrape_DamLevel():
    # Request and download webpage
    # Create a request object connecting to PAGASA Website
    # and downloading its webpage contents.
    res = requests.get('http://bagong.pagasa.dost.gov.ph/flood')
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    temp = open('temp.html','w')
    temp.write(res.text)
    temp.close()

    # Parse only the table containing the Dam Information
    # Use BeautifulSoup4 to parse from temp.html the table
    # containing the information on dams.

    # Create a beautifulsoup object and parse the table containing the profiles
    # of all Dams in the Philippines
    soup = bs4.BeautifulSoup(open('temp.html'), features='lxml')
    str_table = str(soup.select('table.table.dam-table'))

    # Convert this html table into a pandas DataFrame
    # Use the pandas library to create the dataframe
    # then convert it to a csv file. A datestamp is
    # appended on its filename: `PH_Dams_yyyy-mm-dd.csv`

    # Create the initial dataframe
    dam_df = pd.read_html(str_table, header=0)

    # DATA CLEANING
    # Apparently the whole dataframe got enclosed on a square bracket
    # which makes it a python list having only one element-- the DataFrame.
    # Since the whole dataframe is the only element on the list...
    dam_df = dam_df[0]

    # The dataframe headers were repeated as the first row the dataframe
    # Better to remove it.
    dam_df = dam_df[1:-1]

    # Select only the columns needed
    dam_df = dam_df[['Dam Name', 'Reservoir Water Level (RWL) (m)', 
                    'Normal High Water Level (NHWL) (m)', 'Deviation from NHWL (m)', 
                    'Rule Curve Elevation (m)', 'Deviation from Rule Curve (m)']]

    # Select only the rows needed
    today_dam_rows = []
    i = 0
    while i < len(dam_df.index):
        today_dam_rows.append(i)
        i += 4    
        
    dam_df = dam_df.iloc[today_dam_rows]

    # Add a column stating the date and time of observation.
    # Time is always 06:00.
    dam_df['Date & Time'] = datetime.datetime.now().strftime('%m-%d-%Y ') + '06:00'

    # Reset index numbers
    dam_df = dam_df.set_index([pd.Index([i for i in range(len(dam_df.index))])])

    # Rearrange columns for the last time. Put 'Date & Time as first column'
    dam_df = dam_df[['Date & Time', 'Dam Name', 'Reservoir Water Level (RWL) (m)', 
                    'Normal High Water Level (NHWL) (m)', 'Deviation from NHWL (m)', 
                    'Rule Curve Elevation (m)', 'Deviation from Rule Curve (m)']]

    # Parse dates under 'Date & Time' column
    dam_df['Date & Time'] = pd.to_datetime(dam_df['Date & Time'])

    # Convert pandas dataframe to csv file
    # filename must have a datestamp appended.
    # Create a filename for the csv containing a timestamp
    now = str(datetime.datetime.now())
    now_split = now.split() # ['yyyy-mm-dd','hh:mm:ss.xxxxxx']
    datestamp = now_split[0] # 'yyyy-mm-dd'
    filename = "PH_Dams_" + datestamp + "_0600.csv"

    # Convert pandas dataframe into a csv file
    dam_df.to_csv(filename, sep=',', header=True, index=False)

    # Report output:
    print("File created last " + str(datetime.datetime.now()) + ": " + filename)
    print(dam_df)
