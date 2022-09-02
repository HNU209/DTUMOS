###import packages 
import numpy as np
import pandas as pd 
import itertools
import warnings 
from ortools.linear_solver import pywraplp
from datetime import datetime
from itertools import repeat
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
def get_taxi_meter(ps_loc_data, taxi_loc_data):
    return list(map(lambda data: haversine(data.y, data.x, taxi_loc_data.y, taxi_loc_data.x).tolist(), ps_loc_data))

#####################################################################################################################
### 배차 알고리즘

def dispatch(passenger_location_data, taxi_location_data, cost_matrix):
    #Calculate cost matrix
    # 모든 빈택시와 모든 승객들에 대해서 각각의 통행거리를 계산
    passenger_cnt = len(passenger_location_data)
    taxi_cnt = len(taxi_location_data)
    
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

# main 배차 함수
def main_dispatch(ps_loc_data, taxi_loc_data):
    if len(ps_loc_data) <= len(taxi_loc_data):  
        costs = list(map(lambda data: get_taxi_meter(ps_loc_data.ride_geometry, data), taxi_loc_data.geometry))
        passenger_iloc, taxi_iloc = dispatch(ps_loc_data, taxi_loc_data, costs)
    elif len(ps_loc_data) > len(taxi_loc_data):
        costs = list(map(lambda data: get_taxi_meter(taxi_loc_data.geometry, data), ps_loc_data.ride_geometry))
        taxi_iloc, passenger_iloc = dispatch(taxi_loc_data, ps_loc_data, costs)
    return passenger_iloc, taxi_iloc


# main 배차 함수
model = pickle.load(open(f"./data/extra_data/ETA_model.pkl", 'rb'))

def main_dispatch_order(ps_loc_data, taxi_loc_data, model=model):
    passenger_iloc = []
    taxi_iloc = []

    # iloc값을 찾기 위해 index를 reset 시킴
    ps_loc_data = ps_loc_data.reset_index(drop=True) 
    taxi_loc_data = taxi_loc_data.reset_index(drop=True) 

    column_names = ["p_x","p_y","d_x","d_y","start_time","straight_km","weekday","holiday", "start_adm", "end_adm"]
    
    test = pd.DataFrame(columns =column_names, index=taxi_loc_data.index)

    ### 택시 정보 채우기
    # p_x, p_y (start_x, start_y) 
    test["p_x"] = [i.x for i in taxi_loc_data.geometry]
    test["p_y"] = [i.y for i in taxi_loc_data.geometry]

    # 시작시간 계산
    test['start_time'] = max(ps_loc_data.ride_dtime)

    # 요일 주말 매핑
    date = datetime.strptime('20220409', "%Y%m%d") if max(ps_loc_data.ride_dtime) > 1440 else datetime.strptime('20220408', "%Y%m%d") 
    weekday = date.weekday()
    holiday = 1 if weekday >= 5 else 0
    test["weekday"] = weekday
    test["holiday"] = holiday

    # 읍면동 정보 매핑
    test["start_adm"] = taxi_loc_data["adm_cn"]

    for row in ps_loc_data.itertuples():
        # 택시 소진시 돌아가지 않기 위함
        if len(test) == 0:
            break
        
        ### 승객 정보 채우기
        # 승객위치
        test["d_x"] = row.ride_geometry.x
        test["d_y"] = row.ride_geometry.y
        
        # 직선거리 계산
        test["straight_km"] = haversine(test["p_y"], test["p_x"], test["d_y"], test["d_x"])
        
        # 도착 읍면동 정보 매핑
        test["end_adm"] = row.adm_cn_start

        #ETA 모델링
        test['eta'] = model.predict(test)

        # 가장 ETA가 낮은 Taxi index 출력
        taxi_index = test.eta.idxmin()
        taxi_index_iloc = taxi_loc_data.index.get_loc(taxi_index)
        
        # 최종 결과물 출력
        passenger_iloc.append(row.Index)
        taxi_iloc.append(taxi_index_iloc)
        
        # 배차된 택시 제외
        test.drop(taxi_index, axis=0, inplace=True)
        # print('passenger %d assigned to taxi %d.' %(row.Index, taxi_index_iloc))
    return passenger_iloc, taxi_iloc