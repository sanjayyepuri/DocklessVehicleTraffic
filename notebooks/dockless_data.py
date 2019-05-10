import pandas as pd 
import geopandas as gpd
import shapely

import time, datetime
import math 

# tract ids are based off us census data created in 2010
# dictionaries to name the regions
tract_to_name = {
    '000204': "Triangle",
    '000500': "North Campus",
    '000700': "South Campus",
    '000401': "East Campus",
    '000604': "Lower West Campus",
    '000603': "Upper West Campus",
    '000601': "Campus"
}

oncampus  = ['000601', '000401']
offcampus = ['000204', '000500', '000700', '000604', '000603']

building_coords = {
'EER': (30.288374, -97.735322), 
'BUR': (30.288836, -97.738415), 
'UTC': (30.283224,-97.738817), 
'ECJ': (30.289065,-97.735392), 
'CPE': (30.290272, -97.736160), 
'RLM': (30.288933, -97.736434), 
'MEZ': (30.284443, -97.738986), 
'CBA': (30.284154, -97.737841), 
'GSB': (30.284140, -97.738380), 
'ART': (30.286265, -97.732985), 
'ETC': (30.289938, -97.735431),  
'CMA': (30.289246, -97.740727), 
'RLP': (30.284948, -97.735549), 
'JGB': (30.285900, -97.735731), 
'PHR': (30.288032, -97.738575), 
'SZB': (30.281665, -97.738753), 
'WAG': (30.285059, -97.737567), 
'PAR': (30.284915, -97.740110), 
'PAI': (30.287162, -97.738742), 
'GDC': (30.286233, -97.736536), 
'FNT': (30.287863, -97.737987), 
'WMB': (30.285434, -97.740401), 
'GOL': (30.285324, -97.741174), 
'BTL': (30.285445, -97.740412), 
'SUT': (30.284988, -97.740816), 
'DFA': (30.285950, -97.731741), 
'SEA': (30.290002, -97.737332), 
'GAR': (30.285173, -97.738551), 
'CAL': (30.284514, -97.740121), 
'GEA': (30.287791, -97.739214), 
'BAT': (30.284840, -97.738993), 
'BEN': (30.283986, -97.739040), 
'MRH': (30.287110, -97.730553)}

# data paths
scooter_data_path = '../data/Dockless_Vehicle_Trips.csv'
census_data_path = '../data/census_tracts_2010_msa/census_tracts_2010_msa.shp'

class DocklessData:

    def __init__(self):
        self.scooter_data_raw = None
        self.census_data_raw = None
        self.class_data_raw = None
        self.scooter_data = None
        self.transformed_endpoints = None


    def load(self):
        print('Loading Scooter Data ...')
        self.scooter_data_raw = pd.read_csv(scooter_data_path)
        print('Scooter Data Loaded.')

        print('Loading Census Data ...')
        self.census_data_raw = gpd.GeoDataFrame.from_file(census_data_path)
        print('Census Data Loaded.')

        print('Loading Class Data ...')
        self.class_data_raw = pd.read_csv('../data/Course_Info.csv')

    def clean_scooter_data(self):    
        # Cleaning Scooter Data 
        print('Cleaning Scooter Data ...')
        scooter_data = self.scooter_data_raw.dropna(subset=['Census Tract Start'])
  
        scooter_data = scooter_data[scooter_data['Census Tract Start'] != 'OUT_OF_BOUNDS']
        scooter_data = scooter_data[scooter_data['Census Tract End'] != 'OUT_OF_BOUNDS']

        scooter_data['Census Tract Start'] = pd.to_numeric(scooter_data['Census Tract Start'])
        scooter_data['Census Tract End'] = pd.to_numeric(scooter_data['Census Tract End'])

        # Dropping first 6 digit sof GEOID in scooter data
        trim_id = lambda id : "%06d" % (int(id) % 1000000)
        scooter_data['tract_start'] = scooter_data['Census Tract Start'].apply(trim_id)
        scooter_data['tract_end'] = scooter_data['Census Tract End'].apply(trim_id)

        # get only rides in the region in the regions of interest
        scooter_data_starting = scooter_data[scooter_data['tract_start'].isin(oncampus + offcampus)]
        scooter_data_ending = scooter_data[scooter_data['tract_end'].isin(oncampus + offcampus)]

        print(scooter_data_starting.shape, scooter_data_ending.shape)
        scooter_data = scooter_data_starting[scooter_data_starting['ID'].isin(scooter_data_ending['ID'])]
        print(scooter_data.shape)
        
        # Converting date string to datetime
        start_time = pd.to_datetime(scooter_data['Start Time'], format="%m/%d/%Y %I:%M:%S %p")
        end_time = pd.to_datetime(scooter_data['End Time'],   format="%m/%d/%Y %I:%M:%S %p")
        scooter_data['Start Time'] = start_time
        scooter_data['End Time'] = end_time

        def to_decimal(strtime):
            hour, minute = map(int, strtime.strftime("%H:%M").split(':'))
            return hour + (minute / 60)

        start_decimal = scooter_data['Start Time'].apply(to_decimal)
        end_decimal = scooter_data['End Time'].apply(to_decimal)
        scooter_data['start_hour_decimal'] = start_decimal
        scooter_data['end_hour_decimal'] = end_decimal
        
        self.scooter_data = scooter_data
        print('Finished Cleaning Scooter Data.')


    def clean_class_data(self):
        print('Cleaning Class Data ...')
        get_building = lambda s: s.split(" ")[0]
        self.class_data_raw['building'] = self.class_data_raw['Room'].apply(get_building)
        self.buildings = self.class_data_raw['building'].unique().tolist()
        self.class_data = self.class_data_raw.groupby(['Begin Time'])
        print('Finished Cleaning Class Data.')


    def transform_endpoints(self):
        print('Transforming Endpoints ...')
        correct_endpoints_forward = self.scooter_data[self.scooter_data['tract_start'].isin(offcampus)]
        correct_endpoints_forward = correct_endpoints_forward[correct_endpoints_forward['tract_end'].isin(oncampus)]

        correct_endpoints_backward = self.scooter_data[self.scooter_data['tract_start'].isin(oncampus)]
        correct_endpoints_backward = correct_endpoints_backward[correct_endpoints_backward['tract_end'].isin(offcampus)]
        correct_endpoints_backward.rename(columns={'tract_start': 'tract_end', 'tract_end': 'tract_start'}, inplace=True)

        self.transformed_endpoints = pd.concat([correct_endpoints_forward, correct_endpoints_backward], sort=False)
        print('Finished Transforming Endpoints.')

    @staticmethod
    def to_class_time(hour):
        minute, _ = math.modf(hour)
        return datetime.datetime(2017, 11, 28, int(hour), int(minute * 60), 0, 0).strftime("%I:%M %p").lstrip("0").replace(" 0", " ")

    def load_and_clean(self):
        self.load()
        self.clean_class_data()
        self.clean_scooter_data()
        self.transform_endpoints()
