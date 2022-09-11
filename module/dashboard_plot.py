from shapely.geometry import Point
import numpy as np 
import pandas as pd
import geopandas as gpd
import plotly.io as pio
import plotly.graph_objects as go 
import plotly.express as px

pio.templates["custom_dark"] = pio.templates["plotly_dark"]
pio.templates["custom_dark"]['layout']['font']['color'] = '#c3c4c7'

def make_dashboard_plot(result, path=''):
    trips_simulation_data, passenger_simulation_data , empty_taxi_simulation_data = result[0]
    waiting_passenger_list ,empty_taxi_list, drive_taxi_list, fail_passenger_list = result[1]
    passenger_final_information, taxi_final_information, passenger, taxi, YMD = result[2]
    all_fail_data = result[3]
    
    ######################PAGE1
    ### fig1
    bins = [i*60 for i in range(0,25)]
    labels = [i for i in range(0,24)]

    all_fail_data["ride_time"] = all_fail_data["ride_time"] + 30
    all_fail_data = all_fail_data.rename(columns={'ride_time':'fail_time', 'ride_geometry':'geometry'})

    fail_passenger_distribution = pd.DataFrame(pd.cut(all_fail_data["fail_time"], bins = bins, right=False, labels = labels).value_counts(sort=False)).reset_index()
    call_passenger_distribution = pd.DataFrame(pd.cut(passenger["ride_time"], bins = bins, right=False, labels = labels).value_counts(sort=False)).reset_index()
    fail_passenger_distribution.columns = ["fail_time", "cnt"]
    call_passenger_distribution.columns = ["ride_time", "cnt"]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=call_passenger_distribution["ride_time"], y=call_passenger_distribution["cnt"],
                            mode="lines+markers", 
                            name="calling passenger"))
    fig1.add_trace(go.Scatter(x=fail_passenger_distribution["fail_time"], y=fail_passenger_distribution["cnt"],
                            mode="lines+markers",
                            name="Passengers who failed to call"))
    fig1.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [i for i in range(0,24)],
            ticktext = [f"{i}".zfill(2)+':00' for i in range(0,24)]
        )
    )
    fig1.update_xaxes(
        range=[-0.5, 24.5],
        title_text = "Time")
    fig1.update_yaxes(
            title_text = "Number of passengers")

    fig1.update_layout(
        legend={"x": 0.9, "y":1},
        margin={"l":0,"r":0,"b":0,"t":0,"pad":0},
        template="plotly_dark")

    fig1.write_html(f"{path}fig1.html")


    ### fig3
    waiting_time = pd.DataFrame([(passenger_final_information["dispatch_time"] + passenger_final_information["wait_time"]).tolist(), passenger_final_information["time"].tolist()]).T
    waiting_time.columns = ["waiting_time", "time"]

    fail_waiting = pd.DataFrame(all_fail_data["fail_time"].values - 30, columns=["time"])
    fail_waiting["waiting_time"] = 30

    waiting_time = pd.concat([waiting_time, fail_waiting], axis=0).reset_index(drop=True)
    waiting_time["waiting_time"] = np.round(waiting_time["waiting_time"].values,2)

    fig3 = go.Figure()
    fig3.add_trace(go.Box(y=waiting_time["waiting_time"],hoverinfo='x+y'))
    fig3.update_layout(
        title={'text': f"Average passenger waiting time over the entire period - {round(np.mean(waiting_time['waiting_time']))}minute",
            'x':0.5,
            'y':0.9},
        title_font={'size':12},
        margin={"l":0,"r":0,"b":0,"t":50,"pad":0},
        template="plotly_dark")
    fig3.update_xaxes(
            visible = False)
    fig3.update_yaxes(
            title_text = "waiting time",
            visible=True)

    fig3.write_html(f"{path}fig3.html")

    ### fig2
    waiting_time["time_cut"] = pd.cut(waiting_time["time"], bins = bins, right=False, labels = labels).tolist()

    top_5per_waiting_time = []
    time = []

    for i in waiting_time.groupby(["time_cut"]):
        sample = round(len(waiting_time.loc[waiting_time["time_cut"] == i[0]]) * 0.05)
        sample = 1 if sample < 1 else sample
        subset = i[1].sort_values("waiting_time", ascending=False).head(sample)
        top_5per_waiting_time.extend([np.mean(subset["waiting_time"])])
        time.extend([i[0]])
        
    fig2 = go.Figure()
    fig2.add_trace(go.Box(x=waiting_time["time_cut"], y=waiting_time["waiting_time"], showlegend=False))
    fig2.add_trace(go.Scatter(x=time, y=top_5per_waiting_time,showlegend=True, name = "top 5%"))
    fig2.update_yaxes(
            title_text = "minute")
    fig2.update_layout(showlegend=False)
    fig2.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [i for i in range(0,24)],
            ticktext = [f"{i}".zfill(2)+':00' for i in range(0,24)] ,
            range=[-1, 24]),
        title={'text': 'Passenger waiting time by hour',
            'x':0.5,
            'y':0.9},
        showlegend = True,
        legend= dict(x=0.9, y=0.9),
        margin={"l":0,"r":0,"b":0,"t":50,"pad":0},
        template="plotly_dark"
    )

    fig2.write_html(f"{path}fig2.html")
    #################################################################


    ####PAGE2####################################################

    ### fig4
    page2_wating_ps = waiting_passenger_list
    page2_empty_tx = empty_taxi_list
    page2_driving_tx = drive_taxi_list
    page2_time = list(range(1440))


    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=page2_time, y=page2_wating_ps,
                            mode="lines", 
                            name="Waiting passengers"))
    fig4.add_trace(go.Scatter(x=page2_time, y=page2_empty_tx,
                            mode="lines",
                            name="Idle vehicles"))
    fig4.add_trace(go.Scatter(x=page2_time, y=page2_driving_tx,
                            mode="lines",
                            name="In-service vehicles"))
    fig4.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [i for i in range(0,1440, 120)],
            ticktext = [f"{int(i/60)}".zfill(2) + ':00' for i in range(0,1440, 120)]
        )
    )

    fig4.update_xaxes(
        title_text = "Time(hour)")
    fig4.update_yaxes(
            title_text = "Number of vehicles and passengers")

    fig4.update_layout(
        legend={"x": 0.74, "y":1},
        margin={"l":0,"r":0,"b":0,"t":0,"pad":0},
        template="plotly_dark")

    fig4.write_html(f"{path}fig4.html")

    ### fig5
    taxi_final_information["total_drive_time"] = taxi_final_information["total_to_ps_drive_time"] + taxi_final_information["total_ps_drive_time"]

    taxi_driving_nm = (np.array(drive_taxi_list) + np.array(empty_taxi_list)).tolist()
    taxi_driving_nm = taxi_driving_nm[::60]

    fig5 = px.bar(x=list(range(24)), y=taxi_driving_nm)

    fig5.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [i for i in range(0,24,2)],
            ticktext = [f"{i}".zfill(2)+':00' for i in range(0,24,2)],
            title="Time(hour)"),
        yaxis = dict(
            title="number of vehicles"),
        margin={"l":0,"r":20,"b":0,"t":0,"pad":0},
        template="plotly_dark")


    fig5.write_html(f"{path}fig5.html")

    ##############################################################

    ###PAGE3######################################################
    ### Page 3
    #start, end information
    ps_start_inf, ps_end_inf  = [],[]
    for i in trips_simulation_data:
        if i["vendor"] == 1:
            ps_start_inf.append([i["timestamp"][0] , i["trip"][-1][0], i["trip"][-1][1]])
        elif i["vendor"] == 0:
            ps_end_inf.append([i["timestamp"][-1], i["trip"][-1][0], i["trip"][-1][1]])
            
    ps_start_inf = pd.DataFrame(ps_start_inf, columns = ["start_time","long","lat"])
    ps_end_inf = pd.DataFrame(ps_end_inf, columns = ["end_time","long","lat"])

    bins = [i*60 for i in range(0, 25)]
    labels = [i*60 for i in range(0, 24)]
    time_list = [i for i in range(0, 1440, 60)]

    # 1_1
    ps_start_inf["time"] = pd.cut(ps_start_inf["start_time"], right=False, bins = bins, labels = labels).tolist()

    start_inf = []
    for i in time_list:
        subset_start_inf = ps_start_inf.loc[ps_start_inf["time"] == i]
        start_inf.append(subset_start_inf)
        
    frames = [{   
        'name':f'frame_{idx}',
        'data':[{
            'type':'densitymapbox',
            'lat':i["lat"].tolist(),
            'lon':i["long"].tolist(),
            'showscale': False,
            'radius':5}],           
    } for idx,i in enumerate(start_inf)]  

    sliders = [{
        'transition':{'duration': 0},
        'x':0.11, 
        'y':0.04,
        'len':0.80,
        'steps':[
            {
                'label':f"{idx}".zfill(2)+':00',
                'method':'animate',
                'args':[
                    ['frame_{}'.format(idx)],
                    {'mode':'immediate', 'frame':{'duration':100, 'redraw': True}, 'transition':{'duration':50}}
                ],
            } for idx,i in enumerate(start_inf)]
    }]

    play_button = [{
        'type':'buttons',
        'showactive':True,
        'x':0.1, 'y':-0.05,
        'buttons':[{ 
            'label': 'Play',
            'method':'animate',
            'args':[
                None,
                {
                    'frame':{'duration':200, 'redraw':True},
                    'transition':{'duration':100},
                    'fromcurrent':True,
                    'mode':'immediate',
                }
            ]
        }]
    }]

    # Defining the initial state
    data = frames[0]['data']

    # Adding all sliders and play button to the layout
    layout = go.Layout(
        sliders=sliders,
        updatemenus=play_button,
        mapbox={
            'accesstoken':"pk.eyJ1IjoiZHVzZ3Vyd24iLCJhIjoiY2wzbW9yNjdsMDZ0djNpbW9vbnhsZXBobCJ9.KDVqndg88Clx3Bq3_GTF4Q",
            'center':{"lat": 40.713120072648174, "lon":-74.00024959840161},
            'zoom':10,
            'style':'dark'},
        margin = {'l':0, 'r':0, 'b':80, 't':0},
        template="custom_dark"
    )

    # Creating the figure
    fig6 = go.Figure(data=data, layout=layout, frames=frames)

    fig6
    fig6.write_html(f"{path}fig6.html")

    ### fig7
    # 3-1-1-a
    data = go.Densitymapbox(lat=ps_start_inf.lat, lon=ps_start_inf.long,
                                    radius=2)

    layout_basic = go.Layout(
        mapbox={
            'accesstoken':"pk.eyJ1IjoiZHVzZ3Vyd24iLCJhIjoiY2wzbW9yNjdsMDZ0djNpbW9vbnhsZXBobCJ9.KDVqndg88Clx3Bq3_GTF4Q",
            'center':{"lat":  40.713120072648174, "lon":-74.00024959840161},
            'zoom':10,
            'style':'dark'},
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        template="plotly_dark"
    )

    fig7 = go.Figure(data=data, layout=layout_basic)
    fig7
    fig7.write_html(f"{path}fig7.html")

    ###fig8
    # 1-2
    ps_end_inf["time"] = pd.cut(ps_end_inf["end_time"], bins = bins, right=False, labels = labels).tolist()

    end_inf = []
    for i in time_list:
        subset_end_inf = ps_end_inf.loc[ps_end_inf["time"] == i]
        end_inf.append(subset_end_inf)

    frames = [{   
        'name':f'frame_{idx}',
        'data':[{
            'type':'densitymapbox',
            'lat':i["lat"].tolist(),
            'lon':i["long"].tolist(),
            'showscale': False,
            'radius':5}],           
    } for idx,i in enumerate(end_inf)]  

    # Defining the initial state
    data = frames[0]['data']

    # Creating the figure
    fig8 = go.Figure(data=data, layout=layout, frames=frames)

    fig8.write_html(f"{path}fig8.html")

    ### fig9
    data = go.Densitymapbox(lat=ps_end_inf.lat, lon=ps_end_inf.long,
                                    radius=2)

    layout_basic = go.Layout(
        mapbox={
            'accesstoken':"pk.eyJ1IjoiZHVzZ3Vyd24iLCJhIjoiY2wzbW9yNjdsMDZ0djNpbW9vbnhsZXBobCJ9.KDVqndg88Clx3Bq3_GTF4Q",
            'center':{"lat":  40.713120072648174, "lon":-74.00024959840161},
            'zoom':10,
            'style':'dark'},
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        template="plotly_dark"
    )

    fig9 = go.Figure(data=data, layout=layout_basic)

    fig9.write_html(f"{path}fig9.html")

    ### fig10
    all_fail_data["time"] = pd.cut(all_fail_data["fail_time"], bins = bins, right=False, labels = labels).tolist()

    all_fail_data["lat"] = [i.y for i in all_fail_data["geometry"]]
    all_fail_data["long"] = [i.x for i in all_fail_data["geometry"]]

    fail_inf = []
    for i in time_list:
        subset_fail_inf = all_fail_data.loc[all_fail_data["time"] == i]
        fail_inf.append(subset_fail_inf)
        
    frames = [{   
        'name':f'frame_{idx}',
        'data':[{
            'type':'scattermapbox',
            'lat':i["lat"].tolist(),
            'lon':i["long"].tolist()}],           
    } for idx,i in enumerate(fail_inf)]  

    # Defining the initial state
    data = frames[0]['data']

    # Creating the figure
    fig10 = go.Figure(data=data, layout=layout, frames=frames)

    fig10.write_html(f"{path}fig10.html")

    # ### fig11
    # # 3
    # hjd_2018 = gpd.read_file('./data/extra_data/HangJeongDong_ver20180401.geojson')

    # ps_wait_inf = []
    # for i in trips_simulation_data:
    #     if i["vendor"] == 1:
    #         ps_wait_inf.append([i["timestamp"][-1] - i["timestamp"][0] , Point([i["trip"][-1][0], i["trip"][-1][1]])])

    # ps_wait_inf = gpd.GeoDataFrame(ps_wait_inf, columns = ["wait_time", "geometry"])

    # fail_data = all_fail_data[["geometry"]]
    # fail_data["wait_time"] = 30

    # ps_wait_inf = pd.concat([fail_data, ps_wait_inf], axis=0)
    # ps_wait_inf = gpd.GeoDataFrame(ps_wait_inf, geometry='geometry')

    # ps_wait_inf = gpd.sjoin(ps_wait_inf, hjd_2018)

    # ps_wait_inf = ps_wait_inf.groupby(["adm_nm"]).mean(["wait_time"]).reset_index().drop("index_right",axis=1)
    # ps_wait_inf = pd.merge(ps_wait_inf, hjd_2018).set_index("adm_nm")
    # ps_wait_inf["wait_time"] = np.round(ps_wait_inf["wait_time"].values,2)

    # ps_wait_inf.columns = ['Wait Time (min)', 'geometry', 'adm_cd']

    # fig11 = px.choropleth_mapbox(ps_wait_inf,
    #                         geojson=ps_wait_inf.adm_cd,
    #                         locations=ps_wait_inf.index,
    #                         color="Wait Time (min)",
    #                         center={"lat":  40.713120072648174, "lon": -74.00024959840161},
    #                         mapbox_style="carto-positron",
    #                         zoom=10)
    # fig11.update_layout(
    #     mapbox={
    #         'accesstoken':"pk.eyJ1IjoiZHVzZ3Vyd24iLCJhIjoiY2wzbW9yNjdsMDZ0djNpbW9vbnhsZXBobCJ9.KDVqndg88Clx3Bq3_GTF4Q",
    #         'style':'dark'},
    #     margin={"r":0,"t":0,"l":0,"b":0},
    #     template="plotly_dark")

    # fig11.write_html(f"{path}fig11.html")
    
    print('complete_dash_plot!!')
