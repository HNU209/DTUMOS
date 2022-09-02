###import packages 
import requests
import numpy as np
import polyline
import math
import itertools
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import warnings 

warnings.filterwarnings('ignore')

# routes step 추출 
def get_res(point):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    steps = "?steps=true"
    loc = "{},{};{},{}".format(point[0], point[1], point[2], point[3]) # lon, lat, lon, lat
    url = "http://127.0.0.1:5000/route/v1/driving/"
    r = session.get(url + loc + steps) 
    if r.status_code!= 200:
        return {}
  
    res = r.json()   
    all_steps = res["routes"][0]["legs"][0]["steps"]
    all_steps = all_steps[:-1]
    return all_steps

### routes 
# routes의 한 step의 geometry 추출
def get_part_route(step):
    location_part = polyline.decode(step["geometry"])
    location_part = list(map(lambda data: [data[1],data[0]] ,location_part))
    return location_part
    
# routes의 전체 step에 대한 geometry 추출
def get_total_route(all_step):
    total_route = list(map(lambda data: get_part_route(data), all_step))
    last_location = total_route[-1][-1]
    total_route = list(map(lambda data: data[:-1], total_route))
    total_route = list(itertools.chain(*total_route))
    total_route.append(last_location)
    return total_route

### timestamp 
def compute_straight_distance(lat1, lon1, lat2, lon2):
    # haversine
    km_constant = 3959* 1.609344
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    km = km_constant * c
    return km

def get_part_timestamp(step):
    duration_part = math.ceil((step["duration"] / 60)*100)/100
    location_part = polyline.decode(step["geometry"])
    
    duration_part = [duration_part] * (len(location_part) - 1)

    if len(location_part) - 1 == 1: 
        pass
    else: 
        # 길이 별 시간 차등 분배
        location_part = np.array(location_part)
        location_part = np.hstack([location_part[:-1,:], location_part[1:,:]])
        per = compute_straight_distance(location_part[:,0], location_part[:,1], location_part[:,2], location_part[:,3])
        per = per / np.sum(per)
        duration_part = np.array(duration_part) * per
        duration_part = duration_part.tolist()

    return duration_part

def get_total_timestamp(all_step):
    total_time = list(map(lambda data: get_part_timestamp(data), all_step))
    total_time = list(itertools.chain(*total_time))
    total_time = list(itertools.accumulate(total_time)) 
    start_time = [0]
    start_time.extend(total_time)
    total_time = start_time
    return total_time 

### distance
def get_distance(all_step):
    total_distance = list(map(lambda data: data["distance"], all_step))
    total_distance = sum(total_distance)
    return total_distance

### delivery time
def get_duration(all_step):
    total_duration = list(map(lambda data: data["duration"], all_step))
    total_duration = sum(total_duration)
    return total_duration