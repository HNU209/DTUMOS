import osmnx as ox
from numpy import random 
import numpy as np
import pandas as pd 
import geopandas as gpd 
import itertools
from shapely.geometry import Point
from tqdm import tqdm 
import pickle
from module.generate_random_location import create_random_point_based_on_edges


'''
KT 이동 데이터를 기반으로 fake passenger를 만들어 낸다. 
cf. 0.01는 약 107755명을 반환함.
'''

def generate_fake_passenger_based_on_KTdata(passenger):
    #KT 이동량 데이터 기준 일 평균 서울지역 읍면동 별 유동 인구 RAW DATA
    KT_data = pd.read_csv("./data/extra_data/fake_passenger_raw_data.csv")
    KT_data = KT_data.loc[KT_data['도착 행정동 코드'] < 2000000]
    # 서울 시 이동 인구수에 0.01만 생성
    KT_data["이동인구(합)"] = KT_data["이동인구(합)"] * 0.01

    #포아송 분포로 만든 이동 분포
    rng = np.random.default_rng()
    s = rng.poisson(KT_data["이동인구(합)"].values)

    KT_data["이동인구(합)"] = s

    KT_data["출발 행정동 코드"] = list(map(str, KT_data["출발 행정동 코드"]))
    KT_data["도착 행정동 코드"] = list(map(str, KT_data["도착 행정동 코드"]))

    # # 이동인구 없는 행 제거
    KT_data = KT_data.loc[KT_data["이동인구(합)"] != 0]

    # KT_data -> O-D 수 기준으로 데이터 재구성
    KT_data = pd.DataFrame(list(itertools.chain(*[[i.tolist()] * j  for i,j in zip(KT_data.values[:,:2], KT_data.values[:,2])])), columns = ["origin_code","dest_code"])
    
    # 필요한 adm_cd 별 랜덤 좌표 갯수
    fake_OD_list = KT_data['origin_code'].tolist() + KT_data['dest_code'].tolist()
    fake_OD_list = pd.DataFrame(pd.Series(fake_OD_list).value_counts()).reset_index()
    fake_OD_list.columns = ['adm_cd', 'cnt']

    # adm_cd에 맞는 행정동 geometry 부여
    hjd_2018 = gpd.read_file('./data/extra_data/HangJeongDong_ver20180401.geojson')
    fake_OD_list = pd.merge(fake_OD_list, hjd_2018)
    fake_OD_list = fake_OD_list.drop('adm_nm', axis=1)
    fake_OD_list = gpd.GeoDataFrame(fake_OD_list, geometry='geometry')

    # 행정 구역 별 랜덤 좌표를 edges 위에서 뽑기 위해  edges 추출 (해당 과정은 1분 이상 걸리기 때문에 미리 pickle로 저장해 놓음)
    # G = ox.graph_from_place('서울 대한민국', network_type="drive_service", simplify=True)
    # _, edges = ox.graph_to_gdfs(G)

    with open('./data/extra_data/seoul_simplify_T_edges.pickle', 'rb') as f:
        edges = pickle.load(f)
        
    new_location = generate_point(edges, fake_OD_list)
    fake_OD_list['point_list'] = new_location

    adm_point_list = dict()
    for adm, OD_list in zip(fake_OD_list['adm_cd'], fake_OD_list['point_list']):
        adm_point_list[adm] = OD_list
        
    O_point = [adm_point_list[i].pop() for i in KT_data['origin_code']]
    D_point = [adm_point_list[i].pop() for i in KT_data['dest_code']]

    KT_data['ride_lon'] = [i.x for i in O_point]    
    KT_data['ride_lat'] = [i.y for i in O_point]
    KT_data['alight_lon'] = [i.x for i in D_point]    
    KT_data['alight_lat'] = [i.y for i in D_point]
    
    time_data = existing_passenger_time_distribution(passenger)
    
    KT_data['ride_time'] = np.random.choice(time_data["time"].tolist() ,size = len(KT_data), p= time_data["ratio"].tolist())
    KT_data['dispatch_time'] = 0
    KT_data = KT_data.drop(['origin_code','dest_code'], axis=1)
    
    return KT_data


### 기존의 데이터의 시간 분포를 추출
def existing_passenger_time_distribution(passenger):
    passenger_ratio = passenger["ride_time"].value_counts().reset_index() 
    passenger_ratio.columns = ["time", "cnt"]
    passenger_ratio["ratio"] = [i/sum(passenger_ratio["cnt"]) for i in passenger_ratio["cnt"]]
    return passenger_ratio

def generate_point(edges, fake_OD_list): 
    
    locations = []

    for i in tqdm(range(len(fake_OD_list))):
        sub_edges = gpd.sjoin(edges, fake_OD_list.iloc[[i]])
        sub_loc = create_random_point_based_on_edges(sub_edges, fake_OD_list.iloc[i].cnt)
        locations.append(sub_loc)
        
    return locations