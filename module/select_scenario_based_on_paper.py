import pandas as pd

'''
위 시나리오와 같이 시나리오 별 택시, 승객 수요 공급 적용
'''
def select_scenario(passenger, taxi, mode='scen_1'):
    if mode == 'scen_1':
        passenger = passenger.sample(n=50000)
        taxi = taxi.sample(n=10000)
    elif mode == 'scen_2':
        passenger = passenger.sample(n=50000).copy()
        taxi = taxi.sample(n=20000).copy()
    elif mode == 'scen_3':
        passenger = passenger.sample(n=100000).copy()
        taxi = taxi.sample(n=20000).copy()
    elif mode == 'scen_4':
        passenger = passenger.sample(n=200000).copy()
        taxi = taxi.sample(n=20000).copy()
    elif mode == 'scen_5':
        passenger = passenger.sample(n=400000).copy()
        taxi = taxi.sample(n=20000).copy()     

    passenger = passenger.sort_values('ride_time').reset_index(drop=True)
    taxi = taxi.sort_values('work_start').reset_index(drop=True)
    
    print(f'{mode} - passenger: {len(passenger)}, taxi: {len(taxi)}')
    return passenger, taxi