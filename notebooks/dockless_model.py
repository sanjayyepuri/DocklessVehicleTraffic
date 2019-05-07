from dockless_data import DocklessData, building_coords
from sklearn.linear_model import LinearRegression
from utils import convert_from_lat_long
from shapely.geometry import Point

import time, datetime
import numpy as np 
import math 

class DocklessBayesNet:

    def __init__(self):
        self.data = None        
        self.scooter_data = None
        self.class_data = None
        self.buildings = None
        self.endpoints = None
        self.sr_dist = None
        self.d_dist = None
    
    def load_data(self):
        self.data = DocklessData()
        self.data.load_and_clean()
        
        self.scooter_data = self.data.scooter_data
        self.class_data = self.data.class_data
        self.buildings = self.data.buildings
        self.endpoints = self.data.transformed_endpoints
    
    # Distributions
    # P(start_time)
    def get_start_time_distribution(self, class_time):
        first_time      = class_time - 0.50
        second_time     = class_time - 0.25
        
        start_time_freq = self.scooter_data[self.scooter_data['Day of Week'] == 3].groupby(['start_hour_decimal'])['start_hour_decimal'].agg('count').to_frame('count').reset_index()
        first  = int(start_time_freq[start_time_freq['start_hour_decimal'] == first_time]['count'].iloc[0])
        second = int(start_time_freq[start_time_freq['start_hour_decimal'] == second_time]['count'].iloc[0])
        third  = int(start_time_freq[start_time_freq['start_hour_decimal'] == class_time]['count'].iloc[0])
        
        first_ln, second_ln, third_ln = np.log(first), np.log(second), np.log(third)
        first_piecewise  = LinearRegression().fit(np.array([0,  15]).reshape((-1, 1)), [first,  second])
        second_piecewise = LinearRegression().fit(np.array([15, 30]).reshape((-1, 1)), [second_ln, third_ln])
        
        distribution = {}
        total = 0.0
        for minute in range(0, 30):
            if minute < 15:
                total += first_piecewise.predict(np.array([minute]).reshape(1, -1))[0]
            else:
                total += np.exp(second_piecewise.predict(np.array([minute]).reshape(1, -1))[0])
                
        for minute in range(0, 30):
            t = first_time + (minute / 60)
            if minute < 15:
                distribution[t] = first_piecewise.predict(np.array([minute]).reshape(1, -1))[0]
            else:
                distribution[t] = np.exp(second_piecewise.predict(np.array([minute]).reshape(1, -1))[0])

            distribution[t] /= total
            
        squished_dist = {first_time: 0.0, second_time: 0.0}
        for minute in range(0, 30):
            t = first_time + (minute / 60)
            if minute < 15:
                squished_dist[first_time] += distribution[t]
            else:
                squished_dist[second_time] += distribution[t]

        return squished_dist


    # P(distance | start_time)
    def get_distance_distribution(self, start_time):
        distances_given_start = self.scooter_data[self.scooter_data["start_hour_decimal"] == start_time]
        distances_given_start = distances_given_start[(distances_given_start['Trip Distance'] > 50) & (distances_given_start['Trip Distance'] < 2000)].sort_values(by=['Trip Distance'])
        distances_freq = distances_given_start.groupby(['Trip Distance'])['Trip Distance'].agg('count').to_frame('count').reset_index()

        # avg pool/smooth data
        distances_freq_pooled = {}
        total = 0.0
        for mid in range(55, 1996, 10):
            distances_freq_pooled[mid] = 0
            window = distances_freq[distances_freq['Trip Distance'].isin(list(range(mid, mid + 10)))]
            val = window['count'].mean()
            if not math.isnan(val):
                distances_freq_pooled[mid] = val
            total += val

        for mid in range(55, 1996, 10):
            distances_freq_pooled[mid] /= total
            
        return distances_freq_pooled

    def get_end_location_distribution(self, class_time_decimal):
        
        class_time = DocklessData.to_class_time(class_time_decimal)
        dist = {b:0 for b in self.buildings} # dictionary for {class_time : {building : probability_distr}}
            
        df = self.class_data.get_group(class_time)

        df = df.groupby('building')['building'].agg('count').to_frame('count').reset_index()
        total_classes = 0.0
        for i in range(len(df)):
            room = df.iloc()[i]['building']
            count = df.iloc()[i]['count']
            dist[room] = count
            total_classes += count
            
        for key, _ in dist.items():
            dist[key] /= total_classes

        return dist


    def get_start_region_distribution(self, class_loc, dist):
        given_distance = self.endpoints[self.endpoints['Trip Distance'].isin(range(dist-10, dist+10))]

        start_tract_freq = given_distance.groupby(['tract_start'])['tract_start'].agg('count').to_frame('count').reset_index()
        
        lat, long = building_coords[class_loc]
        point = Point(lat, long)
        
        total = 0
        distribution = {}
        for i in range(len(start_tract_freq)):
            curr_tract = start_tract_freq.iloc()[i]['tract_start'] # offcampus -> oncampus
                
            geometry = self.data.census_data_raw[self.data.census_data_raw['TRACTCE10'] == str(curr_tract)]['geometry'].iloc()[0]

            if geometry.distance(convert_from_lat_long(point.y, point.x))*0.3048 > dist:   
                distribution[curr_tract] = 5.0
            else:
                distribution[curr_tract] = float(start_tract_freq.iloc()[i]['count'])
            
            total += distribution[curr_tract]
            
        total = float(total)
        
        if total == 0:
            return distribution 
        
        for i in distribution.keys():
            distribution[i] /= total
        
        return distribution


        ## SAMPLING 

    def direct_sampling(self, samples, class_time):
        start = time.time()
        start_time_distribution = self.get_start_time_distribution(class_time)
        end_location_distribution = self.get_end_location_distribution(class_time)

        trips = []
        for _ in range(samples):
            # start_time
            start_time = np.random.choice(list(start_time_distribution.keys()), p=list(start_time_distribution.values()))

            # end_location
            end_location = np.random.choice(list(end_location_distribution.keys()), p=list(end_location_distribution.values()))

            # distances
            distance_distribution = self.get_distance_distribution(start_time)
            distance = np.random.choice(list(distance_distribution.keys()), p=list(distance_distribution.values()))

            # start_region
            start_region_distribution = self.get_start_region_distribution(end_location, distance)
            start_region = np.random.choice(list(start_region_distribution.keys()), p=list(start_region_distribution.values()))
            
            trips.append((class_time, start_time, end_location, distance, start_region))

        #     print("class at %.2f in %s, start in %s at %.2f and travel %dm" % (class_time, end_location, tract_to_name[start_region], start_time, distance))

        print((time.time() - start) / samples)

        return trips

    def compute_start_region_distribution(self):
        self.sr_dist = {}
        for el in self.buildings:
            self.sr_dist[el] = {}
            for d in range(55, 1996, 10):
                self.sr_dist[el][d] = self.get_start_region_distribution(el, d)

    def compute_distance_distribution(self, class_time):
        self.d_dist = {}
        for st in [class_time - 0.25, class_time - 0.5]:
            self.d_dist[st] = self.get_distance_distribution(st)
        

    def gibbs_sample(self, samples, class_time):

        seed = list(self.direct_sampling(1, class_time)[0])

        start = time.time()
        trips = []
        for _ in range(samples):
            # pick random variable to re-sample
            # class_time is always evidence; never re-sample it
            new_variable = np.random.randint(1, 5)
        #     print(resample(new_variable, seed))
            seed[new_variable] = self.resample(new_variable, seed)
            
            class_time, start_time, end_location, distance, start_region = seed
            #print("class at %.2f in %s, start in %s at %.2f and travel %dm" % (class_time, end_location, tract_to_name[start_region], start_time, distance))
            
            trips.append((class_time, start_time, end_location, distance, start_region))
        print((time.time() - start) / samples)
        return trips
    
    def resample(self, new_variable, seed):
        if new_variable == 1: # start_time
            dist = {}
            # P[ST | ct] * P[d | ST]
            ct = seed[0]
            d = seed[3]
            start_time_distribution = self.get_start_time_distribution(ct)
            for st in start_time_distribution.keys():
                if self.d_dist is not None:
                    dist[st] = self.d_dist[st][d] * start_time_distribution[st]
                else:
                    dist[st] = self.get_distance_distribution(st)[d] * start_time_distribution[st]
                
        elif new_variable == 2: # end_location
            dist = {}
            # P[EL | ct] * P[sr | d, EL]
            ct = seed[0]
            d = seed[3]
            sr = seed[4]
            end_location_distribution = self.get_end_location_distribution(ct)
            for el in end_location_distribution.keys():
                if self.sr_dist is not None:
                    dist[el] = end_location_distribution[el] * self.sr_dist[el][d][sr]
                else:
                    dist[el] = end_location_distribution[el] * self.get_start_region_distribution(el, d)[sr]
                
        elif new_variable == 3: # distance
            dist = {}
            # P[D | st] * P[sr | D, el]
            st = seed[1]
            el = seed[2]
            sr = seed[4]
            
            distance_distribution = None

            if self.d_dist is not None:
                keys = self.d_dist[st].keys()
            else:
                distance_distribution = self.get_distance_distribution(st)
                keys = distance_distribution.keys()

            for d in keys:
                if self.d_dist is not None and self.sr_dist is not None:
                    dist[d] = self.d_dist[st][d] * self.sr_dist[el][d][sr]
                elif self.d_dist is not None: 
                    dist[d] = self.d_dist[st][d] * self.get_start_region_distribution(el, d)[sr]
                else:
                    dist[d] = distance_distribution[d] * self.get_start_region_distribution(el, d)[sr]
                
        else: # start_region
            # P[SR | d, el]
            el = seed[2]
            d = seed[3]
                    
            if self.sr_dist is not None:
                dist = self.sr_dist[el][d]
            else:
                dist = self.get_start_region_distribution(el, d)
        
        # normalize
        total = sum(list(dist.values()))
        for key, _ in dist.items():
            dist[key] /= total
        
        # return sampled value
        return np.random.choice(list(dist.keys()), p=list(dist.values()))

# bayes = DocklessBayes()
# bayes.load_data()
# class_time = 9
# print(bayes.direct_sampling(10, class_time))
# bayes.compute_distance_distribution(class_time)
# bayes.compute_start_region_distribution()
# print(bayes.gibbs_sample(10, class_time))