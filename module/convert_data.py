import pandas as pd 
from datetime import datetime
from shapely.geometry import Point
from module.generate_random_location import create_random_point_based_on_place

'''
### generate_simulation_base_data 함수 설명 
- 제공된 데이터를 기준으로 passenger의 정보와 taxi 정보를 분리하여 구성
- Simulation의 시간 단위는 분으로 구성되기 때문에, passenger와 taxi 정보를 분 단위로 변환해준다. (e.g. 2022-04-01 5:40:00 -> 340 minutes)
    - taxi data
        - raw_data의 정보를 바탕으로 택시의 운영 시간을 추정하여, business time을 구성해준다.
        - 최초 택시 위치 정보는 시뮬레이션의 타겟인 지역에 랜덤하게 만들어 준다.
    - passenger data
        - raw_data의 정보를 바탕으로 passenger data를 구성한다.
        
- Extra fuction explanation
    - change_time_unit : 시간을 분 단위로 변경 
    - generate_taxi_schedule : raw data를 기반으로 택시 스케줄 생성
'''

def generate_simulation_base_data(taxi_raw_data, target_place='서울 대한민국'):
    # change_time_unit
    taxi_raw_data, YMD = change_time_unit(taxi_raw_data)
    taxi_raw_data['ride_geometry'] = [Point(i[0],i[1]) for i in taxi_raw_data[['ride_lon', 'ride_lat']].values]
    taxi_raw_data['alight_geometry'] = [Point(i[0],i[1]) for i in taxi_raw_data[['alight_lon', 'alight_lat']].values]
    
    ### passenger 
    passenger = taxi_raw_data[['ride_time', 'ride_geometry', 'alight_geometry']]
    passenger = passenger.reset_index(drop=True)
    passenger['dispatch_time'] = 0   # dispatch_time이란 taxi를 잡기 전 까지 걸리는 시간!
    
    ### taxi
    taxi = taxi_raw_data[['taxi_id', 'ride_time', 'alight_time']]
    # generate_simulation_base_data
    taxi = apply_taxi_schedule(taxi, target_place)
    return passenger, taxi, YMD


def change_time_unit(taxi_raw_data):
    YMD_ride = taxi_raw_data['ride_time'].dt.strftime('%Y%m%d').tolist()
    YMD_alight = taxi_raw_data['alight_time'].dt.strftime('%Y%m%d').tolist()
    YMD = YMD_ride + YMD_alight
    YMD = set(YMD)

    if len(YMD) == 1: 
        YMD = list(YMD)
        target_YMD = min([datetime.strptime(i,'%Y%m%d') for i in YMD])    
        
    elif len(YMD) == 2:
        YMD = list(YMD)
        target_YMD = min([datetime.strptime(i,'%Y%m%d') for i in YMD])    
        
    taxi_raw_data['ride_time'] = taxi_raw_data['ride_time'] - target_YMD
    taxi_raw_data['ride_time'] = taxi_raw_data['ride_time']/pd.Timedelta(minutes=1)
    taxi_raw_data['ride_time'] = round(taxi_raw_data['ride_time']).astype('int')
    
    taxi_raw_data['alight_time'] = taxi_raw_data['alight_time'] - target_YMD
    taxi_raw_data['alight_time'] = taxi_raw_data['alight_time']/pd.Timedelta(minutes=1)
    taxi_raw_data['alight_time'] = round(taxi_raw_data['alight_time']).astype('int')
    
    return taxi_raw_data, YMD

def apply_taxi_schedule(taxi_data, target_place):
    # taxi_id 별 최소 탑승 시간과 최대 하차 시간으로 taxi_schedule을 생성한다.
    taxi_schedule_dict = dict()

    for i in taxi_data.groupby('taxi_id'):
        taxi_schedule_dict[i[0]] = [i[1]['ride_time'].min(), i[1]['alight_time'].max()]
        
    taxi_schedule = pd.DataFrame(taxi_schedule_dict).T.reset_index()
    taxi_schedule.columns = ['taxi_id', 'work_start', 'work_end']

    taxi_schedule['board_status'] = 1  # 승객 탑승 상태 - 1 :미탑승, 0 : 탑승
    taxi_schedule['geometry'] = create_random_point_based_on_place(target_place, len(taxi_schedule_dict)) 
    
    taxi = taxi_schedule
    return taxi