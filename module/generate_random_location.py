import osmnx as ox
from numpy import random 
from shapely.geometry import Point
import warnings 

warnings.filterwarnings("ignore")

#택시 위치 좌표 랜덤 생성 (base 데이터 로드 시간이 오래 걸림... 다른건 오래 안걸리는데)
def Generate_taxi_random_location(place, CNT):   #place : 관심지역,  cnt: 차량 수
    #관심 지역 base 데이터 추출
    G = ox.graph_from_place(place, network_type="drive_service", simplify=True)
    _, edges = ox.graph_to_gdfs(G)

    #Meter -> Euclid : 단위 변환
    def euclid_distance_cal(meter):
        ###유클리드 거리와 실제 거리를 기반으로 1미터당 유클리드 거리 추출
        #점 쌍 사이의 유클리드 거리를 계산
        dis_1 = ox.distance.euclidean_dist_vec(36.367658 , 127.447499, 36.443928, 127.419678)
        #직선거리 계산
        dis_2 = ox.distance.great_circle_vec(36.367658 , 127.447499, 36.443928, 127.419678)
        return dis_1/dis_2 * meter


    #택시 위치 좌표 랜덤 생성
    taxi_locations = []
    for i in random.choice(range(len(edges)), size = CNT, replace = False):
        #교차로 중심에 생성되지 않게 고정 미터로 생성이 아닌 해당 링크 길이로 유동적인 미터 생성
        random_num = random.choice([0.1,0.2,0.3,0.4,0.5])
        random_meter = edges.iloc[i]["length"] * random_num
        #좌표 생성
        new_node = list(ox.utils_geo.interpolate_points(edges.iloc[i]["geometry"], euclid_distance_cal(random_meter)))
        #좌표의 처음과 끝은 노드이기 때문에 제거하고 선택
        del new_node[0], new_node[-1]
        #랜덤으로 선택한 하나의 링크에서 하나의 택시 좌표 선택 
        idx = random.choice(len(new_node), size = 1)
        taxi_location = new_node[idx[0]]
        taxi_locations.append(taxi_location)
        
    taxi_locations = list(map(lambda data: Point(data),taxi_locations))

    return taxi_locations

