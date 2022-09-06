import numpy as np
from datetime import datetime
import geopandas as gpd
import pickle

def haversine(lat1, lon1, lat2, lon2):
    km_constant = 3959* 1.609344
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    km = km_constant * c
    return km

model = pickle.load(open(f"./data/extra_data/ETA_model.pkl", 'rb'))
hjd_2018 = gpd.read_file('./data/extra_data/HangJeongDong_ver20180401.geojson')

def ETA_data_prepared(self, model=model,HJD=hjd_2018):
    self = self.reset_index(drop=True)
    
    start_point = self[['start_point']]
    start_point.columns = ['geometry']
    start_point = gpd.GeoDataFrame(start_point, geometry='geometry')
    start_point_adm_cd = gpd.sjoin(start_point,HJD)['adm_cd'].tolist()
    
    self["start_adm"] = start_point_adm_cd
    
    end_point = self[['end_point']]
    end_point.columns = ['geometry']
    end_point = gpd.GeoDataFrame(end_point, geometry='geometry')
    end_point_adm_cd = gpd.sjoin(end_point,HJD)['adm_cd'].tolist()
    
    self["end_adm"] = end_point_adm_cd
    
    
    self["p_x"] = [i.x for i in self["start_point"]]       
    self["p_y"] = [i.y for i in self["start_point"]]  
    self["d_x"] = [i.x for i in self["end_point"]]       
    self["d_y"] = [i.y for i in self["end_point"]]
    
    self["straight_km"] = haversine(self["p_y"], self["p_x"], self["d_y"], self["d_x"])
    
    self = self[["p_x","p_y","d_x","d_y","start_time","straight_km","weekday","holiday", "start_adm", "end_adm"]]
    
    self["start_adm"] = self["start_adm"].astype(str)
    self["end_adm"] = self["end_adm"].astype(str)
    self["weekday"] = self["weekday"].astype(str)
    self["holiday"] = self["holiday"].astype(str)
    ETA_result = model.predict(self)
    return ETA_result

def ETA_to_O_result(data, YMD):  # input : success
    data = data.reset_index(drop=True)
    data = data[['dispatch_time', 'ride_time', 'geometry', 'ride_geometry']]
    data['ride_time'] = data['dispatch_time'] + data['ride_time']
    data = data.drop('dispatch_time', axis=1)
    data.columns = ["start_time","start_point", "end_point"] 
    
    date = datetime.strptime(YMD[0], "%Y%m%d")
    weekday = date.weekday()
    holiday = 1 if weekday >= 5 else 0
    data["weekday"] = weekday
    data["holiday"] = holiday
    
    return ETA_data_prepared(data)

def ETA_to_D_result(data ,YMD): # input : success
    data = data.reset_index(drop=True)
    data = data[['dispatch_time', 'ride_time', 'to_O_time', 'ride_geometry', 'alight_geometry']]
    data['ride_time'] = data['dispatch_time'] + data['ride_time'] + data['to_O_time']
    data = data.drop(['dispatch_time','to_O_time'], axis=1)
    data.columns = ["start_time","start_point", "end_point"]
    
    date = datetime.strptime(YMD[0], "%Y%m%d")
    weekday = date.weekday()
    holiday = 1 if weekday >= 5 else 0
    data["weekday"] = weekday
    data["holiday"] = holiday
    
    return ETA_data_prepared(data)
