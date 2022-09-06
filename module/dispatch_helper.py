###import packages 
import pandas as pd
import numpy as np
from tqdm import tqdm
import itertools
from multiprocessing import Pool 

from module.dispatch import *
# from module.ETA import *
from module.osrm_api import *

######################################################################################################
### 운행 중인 차량 데이터 생성
def generate_drive_taxi(success):
    success["geometry"] = success["alight_geometry"]
    success = success[['taxi_id', 'work_start', 'work_end', 'board_status', "end_time",'geometry']]
    return success

### simulation_trip data 생성
def generate_trip_data(success):
    # 병렬처리 cpu 30개 스레스 사용 
    p = Pool(processes=30)
    
    #
    ### to_O (승객의 출발지로 가는 경로)
    #
    to_O = [[o.x,o.y,d.x,d.y] for o,d in zip(success['geometry'], success['ride_geometry'])]

    # osrm을 통한 routes, timestamps 생성
    O_step = p.map(get_res, to_O)
    O_route = p.map(get_total_route, O_step)
    O_timestamps = p.map(get_total_timestamp, O_step)
    O_timestamps = [((np.array(ts)/ts[-1])*i[1]['wait_time']) + (i[1]['board_time'] - i[1]['wait_time']) for ts, i in zip(O_timestamps, success.iterrows())]

    # 시각화 데이터 형식으로 변환
    O_trips = [{'vendor':1, 'trip': tp, 'timestamp': ts.tolist()} for tp, ts in zip(O_route, O_timestamps)]

    #
    ### to_D (승객의 목적지로 가는 경로 )
    #
    to_D = [[o.x,o.y,d.x,d.y] for o,d in zip(success['ride_geometry'], success['alight_geometry'])]
    # osrm을 통한 routes, timestamps 생성
    D_step = p.map(get_res, to_D)
    D_route = p.map(get_total_route, D_step)
    D_timestamps = p.map(get_total_timestamp, D_step)
    D_timestamps = [((np.array(ts)/ts[-1])*i[1]['drive_time']) + i[1]['board_time'] for ts, i in zip(D_timestamps, success.iterrows())]
    # 시각화 데이터 형식으로 변환
    D_trips = [{'vendor':0, 'trip': tp, 'timestamp': ts.tolist()} for tp, ts in zip(D_route, D_timestamps)]

    # 배차 성공 택시 승객한테 가는 경로, 승객의 목적지로 가는 경로 route, timestamp 생성
    trip = O_trips + D_trips
    
    return trip 

def generate_passenger_simulation_data(success):
    success_passenger_data = pd.DataFrame(success["ride_geometry"])
    success_passenger_data["time"] = [[i[1]["ride_time"], i[1]["board_time"]] for i in success.iterrows()]
    success_passenger_data.columns = ["path", "time"]

    passenger_simulation_data = [{'path':[i[1]['path'].x, i[1]['path'].y], 'timestamp':i[1]['time'], 'fail':0} for i in success_passenger_data.iterrows()]
    return passenger_simulation_data



### 빈 차량 데이터를 기반으로 빈 차량 simulation data 생성
def make_up_empty_taxi_1(empty_taxi): 
    
    empty_taxi_location = pd.DataFrame([empty_taxi[1]["taxi_id"].values, empty_taxi[1]["geometry"].values,
                                  np.array([empty_taxi[0]] * len(empty_taxi[1]))]).T
    empty_taxi_location.columns = ["taxi_id", "geometry", "time"]
    
    return empty_taxi_location

def make_up_empty_taxi_2(empty_taxi_location):
    
    empty_taxi_geometry = []
    
    while len(empty_taxi_location) != 0:
        sub_data= empty_taxi_location.loc[empty_taxi_location.geometry == empty_taxi_location.geometry.iloc[0]]
        empty_taxi_location = empty_taxi_location.loc[empty_taxi_location.geometry != empty_taxi_location.geometry.iloc[0]]
        if len(sub_data) == 1:
            empty_taxi_geometry.extend([{"path" :[sub_data.iloc[0]["geometry"].x, sub_data.iloc[0]["geometry"].y], "timestamp" : [int(sub_data.iloc[0]["time"])]}])
        else:
            empty_taxi_geometry.extend([{"path" :[sub_data.iloc[0]["geometry"].x, sub_data.iloc[0]["geometry"].y], "timestamp" : [int(min(sub_data["time"])), int(max(sub_data["time"]))]}])
    
    return empty_taxi_geometry

def generate_empty_taxi_simulation_data(empty_taxi_accumulate):
    
    empty_taxi_accumulate = pd.concat(list(map(lambda data: make_up_empty_taxi_1(data), empty_taxi_accumulate)))
    empty_taxi_geometry_data = list(map(lambda data : make_up_empty_taxi_2(data[1]) ,empty_taxi_accumulate.groupby("taxi_id")))
    empty_taxi_geometry_data = list(itertools.chain(*empty_taxi_geometry_data))
    
    return empty_taxi_geometry_data


#택시 운행 정보 및 승객 정보 생성
def generate_statistics_information(taxi_loc, taxi_stat_inf):
    taxi_final_inf = pd.DataFrame()
    ps_final_inf = pd.DataFrame()

    for i in taxi_stat_inf.groupby("taxi_id"):
        taxi_subset = pd.DataFrame([i[1]["taxi_id"].values[0], sum(i[1].wait_time) ,sum(i[1].drive_time), len(i[1])]).T
        taxi_subset.columns = ["taxi_id", "total_to_ps_drive_time", "total_ps_drive_time", "drive_cnt"] 
        taxi_final_inf = pd.concat([taxi_final_inf,taxi_subset])
        ps_subset = pd.DataFrame([i[1].dispatch_time.values, i[1].wait_time.values, i[1].time.values]).T
        ps_subset.columns = ["dispatch_time", "wait_time", "time"]
        ps_final_inf = pd.concat([ps_final_inf,ps_subset])
        
    not_work_taxi = pd.DataFrame(taxi_loc.loc[list(map(lambda data: data not in taxi_final_inf.taxi_id.tolist(), taxi_loc.taxi_id))].taxi_id.tolist(), columns=["taxi_id"])
    not_work_taxi["drive_cnt"] = 0

    taxi_final_inf = pd.concat([taxi_final_inf, not_work_taxi])
    taxi_final_inf = taxi_final_inf.fillna(0)
    return ps_final_inf, taxi_final_inf

########################################################################################################
def base_dispatch_match(call_passenger, empty_taxi, YMD, dispatch_mode):
    if dispatch_mode == 'ETA':
        passenger_iloc ,taxi_iloc = dispatch_based_on_ETA_duration(call_passenger, empty_taxi, YMD)
    elif dispatch_mode == 'OSRM':
        passenger_iloc ,taxi_iloc = dispatch_based_on_OSRM_distance(call_passenger, empty_taxi)
    elif dispatch_mode == 'ortools':
        passenger_iloc ,taxi_iloc = dispatch_based_on_ortools(call_passenger, empty_taxi)
    
    
    #남은 차량 또는 남은 승객
    remain_taxi_mask = list(set(range(len(empty_taxi))) - set(taxi_iloc))
    remain_passenger_mask = list(set(range(len(call_passenger))) - set(passenger_iloc))

    remain_taxi = empty_taxi.iloc[remain_taxi_mask]
    remain_passenger = call_passenger.iloc[remain_passenger_mask]

    #배차 성공 차량 또는 승객
    success_taxi = empty_taxi.iloc[taxi_iloc]
    success_passenger = call_passenger.iloc[passenger_iloc]
    success_passenger["taxi_id"] = success_taxi["taxi_id"].tolist()

    success = pd.merge(success_taxi, success_passenger)

    # 승객한테 까지 이동시간
    if dispatch_mode == 'ETA':
        to_O_time = ETA_to_O_result(success, YMD)
        success['to_O_time'] = to_O_time
        to_D_time = ETA_to_D_result(success, YMD)
        success['to_D_time'] = to_D_time
    elif (dispatch_mode == 'OSRM') | (dispatch_mode == 'ortools'):
        p = Pool(processes=30)
        to_O = [[i[0].x, i[0].y, i[1].x, i[1].y] for i in success[['geometry', 'ride_geometry']].values]
        to_O_time = p.map(osrm_duration, to_O)
        success['to_O_time'] = to_O_time
        to_D = [[i[0].x, i[0].y, i[1].x, i[1].y] for i in success[['ride_geometry', 'alight_geometry']].values]
        to_D_time = p.map(osrm_duration, to_D)
        success['to_D_time'] = to_D_time

    # 승객 대기시간, 운행 시간, 운행 종료 시간(dispatch_time, ride_time, wait_time, drive_time)
    success["wait_time"] = to_O_time
    success["drive_time"] = to_D_time
    success['board_time'] = success['dispatch_time'] + success['ride_time'] + success['wait_time']
    success["end_time"] = success['dispatch_time'] + success['ride_time'] + success['wait_time'] + success['drive_time']

    # 배치 실패 고객  배치대기시간 더해주기
    if len(remain_passenger) > 0:
        remain_passenger["dispatch_time"] = remain_passenger['dispatch_time'] + 1
    
    return success, remain_passenger, remain_taxi


def dispatch_module(passenger, taxi, YMD, fail_time=30, dispatch_mode='OSRM'):
    
    ##############################################################################################
    # 빈 차량, 운행 중인 차량
    empty_taxi, driving_taxi = pd.DataFrame(), pd.DataFrame()
    
    # 실패 승객 정보 누적
    all_fail_data = pd.DataFrame()
    
    # simulation data (trips, passenger_geometry, empty_taxi)
    trips_simulation_data, passenger_simulation_data, empty_taxi_accumulate = [],[],[]
    
    # 대기 고객, 실패 고객, 빈 차량, 운행 중인 차량 분 단위 기록
    waiting_passenger_list, fail_passenger_list, empty_taxi_list, drive_taxi_list = [],[],[],[] 
    
    # 운행 정보 누적 (전체적인 운행 정보 파악을 위해)
    taxi_statistics_information = pd.DataFrame()
    ##############################################################################################
    
    
    ##############################################################################################
    for i in tqdm(range(0, 1440)):
        
        ####TAXI DATA#############################################################################
        
        # driving_taxi(운행 중인 차량)에서 고객이 내린 차량은 빈 택시로 전환
        if len(driving_taxi) > 0:
            #목적지까지 운행완료한 택시
            drive_end = driving_taxi.loc[driving_taxi["end_time"] <= i]
            drive_end = drive_end[["taxi_id","work_start","work_end","board_status","geometry"]]
            #운행 중인 택시
            driving_taxi = driving_taxi.loc[driving_taxi["end_time"] > i]
            #목적지까지 운행완료한 택시 빈 택시에 추가
            empty_taxi = pd.concat([empty_taxi ,drive_end])
        
        # 운행 종료 택시 제거 (20분 정도 여유롭게 조기 퇴근)
        if i != 0:
            empty_taxi = empty_taxi.loc[(empty_taxi.work_end > i) | (empty_taxi.work_end > i+20)] 

        # 영업 시작 택시
        start_taxi = taxi.loc[taxi.work_start == i]
        # 빈 택시 
        empty_taxi = pd.concat([start_taxi, empty_taxi])
        empty_taxi = empty_taxi.reset_index(drop=True)
        ##########################################################################################
        
        
        ####PASSENGER DATA########################################################################
        # 콜호출 고객 데이터 업데이트
        call_passenger = passenger.loc[passenger.ride_time == i]
        
        if i != 0:
            call_passenger = pd.concat([remain_passenger, call_passenger])

        # 콜 대기시간 30분 이상, 콜실패로 정의 
        if len(call_passenger) > 0:
            fail_data = call_passenger.loc[call_passenger["dispatch_time"] >= fail_time]
            fail_data = fail_data[["ride_time", "ride_geometry"]]
            all_fail_data = pd.concat([all_fail_data, fail_data])
            
            call_passenger = call_passenger.loc[call_passenger["dispatch_time"] < fail_time]
    
        call_passenger = call_passenger.reset_index(drop=True)
        ###########################################################################################
        
        
        ####Dispatch RULE##########################################################################
        # 고객이 있을 때 또는 빈 차량이 있을때 -> 알고리즘 실행

        if (len(call_passenger) > 0) & (len(empty_taxi) > 0):
            success, remain_passenger, remain_taxi = base_dispatch_match(call_passenger, empty_taxi, YMD, dispatch_mode)
            empty_taxi = remain_taxi
            driving_taxi = pd.concat([driving_taxi, generate_drive_taxi(success)])
                        
            # simulation data
            trips_simulation_data.extend(generate_trip_data(success))
            passenger_simulation_data.extend(generate_passenger_simulation_data(success))

            # 운행 통계 정보를 추적하기 위해 정보 누적
            taxi_statistics_inf = success[["taxi_id","dispatch_time","wait_time", "drive_time"]].copy()
            taxi_statistics_inf["time"] = i
            taxi_statistics_information = pd.concat([taxi_statistics_information, taxi_statistics_inf])

        # empty_taxi simulation data 만들기 위해 누적
        empty_taxi_accumulate.append([i, empty_taxi])


        # 분 단위 dispatch list 정보
        waiting_passenger_list.extend([len(remain_passenger)])
        empty_taxi_list.extend([len(empty_taxi)])
        drive_taxi_list.extend([len(driving_taxi)])
        fail_passenger_list.extend([len(fail_data)])
        ############################################################################################
    
    # empty_taxi simulation data
    empty_taxi_simulation_data = generate_empty_taxi_simulation_data(empty_taxi_accumulate)
    # 기존 승객 데이터에 fail passenger simulation 정보 추가
    passenger_simulation_data.extend(list(map(lambda data: {"loc": [data[1]["ride_geometry"].x, data[1]["ride_geometry"].y], "timestamp": [data[1]["ride_time"], data[1]["ride_time"] + fail_time], "fail":1} ,all_fail_data.iterrows())))

    ################################################################################################
    # statistics_information (passenger, taxi)
    passenger_final_information, taxi_final_information = generate_statistics_information(taxi, taxi_statistics_information)

    return [trips_simulation_data, passenger_simulation_data , empty_taxi_simulation_data], [waiting_passenger_list ,empty_taxi_list, drive_taxi_list, fail_passenger_list], [passenger_final_information, taxi_final_information], all_fail_data