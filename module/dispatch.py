###import packages 
import numpy as np
import pandas as pd 
import geopandas as gpd
import itertools
import warnings 
from ortools.linear_solver import pywraplp
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool
from module.osrm_api import *
import pickle

warnings.filterwarnings("ignore")

#####################################################################################################################
### 배차 알고리즘

###costs 뽑는 과정
# cost - 차량과 승객의 직선 거리(meter) 뽑는 함수  
def haversine(lat1, lon1, lat2, lon2):
    km_constant = 3959* 1.609344
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    km = km_constant * c
    return km

# 운행 가능한 모든 차량과 호출 승객의 모든 costs 구하는 함수 
def get_taxi_meter(passenger, taxi):
    return list(map(lambda data: haversine(data.y, data.x, taxi.y, taxi.x).tolist(), passenger))

def ortools_function(passenger, taxi, cost_matrix):
    #Calculate cost matrix
    # 모든 빈택시와 모든 승객들에 대해서 각각의 통행거리를 계산
    passenger_cnt = len(passenger)
    taxi_cnt = len(taxi)
    
    #Declare the MIP solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    taxi_idx = sorted(list(itertools.chain(*list(repeat(list(range(taxi_cnt)), passenger_cnt)))))
    passenger_idx = list(itertools.chain(*list(repeat(list(range(passenger_cnt)), taxi_cnt))))

    #Create the variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for t, p in zip(taxi_idx, passenger_idx):
        x[t, p] = solver.IntVar(0, 1, '')

    #Create the constraints
    #Each worker is assigned to at most 1 task.
    for i in range(taxi_cnt):
        solver.Add(solver.Sum([x[i, j] for j in range(passenger_cnt)]) <= 1)

    # Each task is assigned to exactly one worker.
    for j in range(passenger_cnt):
        solver.Add(solver.Sum([x[i, j] for i in range(taxi_cnt)]) == 1)

    #Create the objective function
    objective_terms = []
    for i in range(taxi_cnt):
        for j in range(passenger_cnt):
            objective_terms.append(cost_matrix[i][j] * x[i, j])

    solver.Minimize(solver.Sum(objective_terms))
    #Invoke the solver
    status = solver.Solve()
    # Print solution
    taxi_iloc = []
    passenger_iloc = []

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        #print('Total distance = ', solver.Objective().Value(), '\n')
        for i in range(taxi_cnt):
            for j in range(passenger_cnt):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                if x[i, j].solution_value() > 0.5:
                    #print('taxi %d assigned to passenger %d.  duration(s) = %d' %
                    #    (i, j, cost_matrix[i][j]))  
                    taxi_iloc.append(i) 
                    passenger_iloc.append(j)
    return passenger_iloc, taxi_iloc


def dispatch_based_on_ortools(passenger, taxi):
    if len(passenger) <= len(taxi):  
        costs = list(map(lambda data: get_taxi_meter(passenger.ride_geometry, data), taxi.geometry))
        passenger_iloc, taxi_iloc = ortools_function(passenger, taxi, costs)
    elif len(passenger) > len(taxi):
        costs = list(map(lambda data: get_taxi_meter(taxi.geometry, data), passenger.ride_geometry))
        taxi_iloc, passenger_iloc = ortools_function(taxi, passenger, costs)
    return passenger_iloc, taxi_iloc
###############################################################################################################

# main 배차 함수
# model = pickle.load(open(f"./data/extra_data/ETA_model.pkl", 'rb'))
# hjd_2018 = gpd.read_file('./data/extra_data/HangJeongDong_ver20180401.geojson')

# def dispatch_based_on_ETA_duration(passenger, taxi, YMD, model=model, HJD=hjd_2018):
    
#     passenger_iloc = []
#     taxi_iloc = []

#     # iloc값을 찾기 위해 index를 reset 시킴
#     passenger = passenger.reset_index(drop=True) 
#     taxi = taxi.reset_index(drop=True) 

#     column_names = ["p_x","p_y","d_x","d_y","start_time","straight_km","weekday","holiday", "start_adm", "end_adm"]
    
#     target_data = pd.DataFrame(columns =column_names, index=taxi.index)

#     ### 택시 정보 채우기
#     # p_x, p_y (start_x, starat_y) 
#     target_data["p_x"] = [i.x for i in taxi.geometry]
#     target_data["p_y"] = [i.y for i in taxi.geometry]

#     # 시작시간 계산
#     target_data['start_time'] = max(passenger['ride_time'])
    
#     # 요일 주말 매핑
#     date = datetime.strptime(YMD[0], "%Y%m%d")
#     weekday = date.weekday()
#     holiday = 1 if weekday >= 5 else 0
#     target_data["weekday"] = weekday
#     target_data["holiday"] = holiday

#     ### 읍면동 정보 매핑
#     # taxi
#     taxi = gpd.GeoDataFrame(taxi, geometry='geometry')
    
#     taxi_adm_cd = gpd.sjoin(taxi,HJD)['adm_cd'].tolist()
#     target_data["start_adm"] = taxi_adm_cd

#     # passenger
#     passenger = passenger.rename(columns={'ride_geometry':'geometry'})
#     passenger = gpd.GeoDataFrame(passenger, geometry='geometry')

#     passenger_ride_adm_cd = gpd.sjoin(passenger,HJD)['adm_cd'].tolist()
#     passenger = passenger.rename(columns={'geometry':'ride_geometry'})
#     passenger['end_adm'] = passenger_ride_adm_cd

#     for row in passenger.itertuples():
#         # 택시 소진시 돌아가지 않기 위함
#         if len(target_data) == 0:
#             break
        
#         ### 승객 정보 채우기
#         # 승객위치
#         target_data["d_x"] = row.ride_geometry.x
#         target_data["d_y"] = row.ride_geometry.y
                
#         # 직선거리 계산
#         target_data["straight_km"] = haversine(target_data["p_y"], target_data["p_x"], target_data["d_y"], target_data["d_x"])
        
#         # 도착 읍면동 정보 매핑
#         target_data["end_adm"] = row.end_adm

#         ###ETA 모델링
#         target_data['eta_result'] = model.predict(target_data)

#         # 가장 ETA가 낮은 Taxi index 출력
#         taxi_index = target_data.eta_result.idxmin()
#         taxi_index_iloc = taxi.index.get_loc(taxi_index)
        
#         # 최종 결과물 출력
#         passenger_iloc.append(row.Index)
#         taxi_iloc.append(taxi_index_iloc)
        
#         # 배차된 택시 제외
#         target_data.drop(taxi_index, axis=0, inplace=True)
        
#     return passenger_iloc, taxi_iloc


#################################################################################################################
def dispatch_based_on_OSRM_distance(passenger, taxi):
    p = Pool(processes=30)
    
    passenger_iloc = []
    taxi_iloc = []

    # iloc값을 찾기 위해 index를 reset 시=킴
    passenger = passenger.reset_index(drop=True) 
    taxi = taxi.reset_index(drop=True) 

    column_names = ["p_x","p_y","d_x","d_y"]
    
    target_data = pd.DataFrame(columns =column_names, index=taxi.index)

    ### 택시 정보 채우기
    # p_x, p_y (start_x, start_y) 
    target_data["p_x"] = [i.x for i in taxi.geometry]
    target_data["p_y"] = [i.y for i in taxi.geometry]

    for row in passenger.itertuples():
        # 택시 소진시 돌아가지 않기 위함
        if len(target_data) == 0:
            break
        
        ### 승객 정보 채우기
        # 승객위치
        target_data["d_x"] = row.ride_geometry.x
        target_data["d_y"] = row.ride_geometry.y
        
        all_steps = p.map(get_res, target_data[['p_x','p_y', 'd_x', 'd_y']].values)
        osrm_distance = [get_distance(i) for i in all_steps]
        
        target_data['osrm_distance'] = osrm_distance

        # 가장 osrm_distance가 낮은 Taxi index 출력
        taxi_index = target_data.osrm_distance.idxmin()
        taxi_index_iloc = taxi.index.get_loc(taxi_index)
        
        # 최종 결과물 출력
        passenger_iloc.append(row.Index)
        taxi_iloc.append(taxi_index_iloc)
        
        # 배차된 택시 제외
        target_data.drop(taxi_index, axis=0, inplace=True)
    
    return passenger_iloc, taxi_iloc