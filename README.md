# DTUMOS

[DTUMOS](https://github.com/HNU209/DTUMOS) is a digital twin framework for urban mobility operating systems. It is an open-source framework that can easily and flexibly apply to any city and mobility system worldwide. The proposed DTUMOS has distinct strengths in scalability, speed, and visualization compared to the existing state-of-the-art mobility digital twins.  We verified the performance of DTUMOS quantitatively using real-world data. DTUMOS can be utilized to develop various operation algorithms in mobility systems, including re-balancing empty vehicles, advanced dispatch, and ride-sharing algorithms, dynamic pricing, and fleet size controls. A lightweight and open-source environment is particularly advantageous when iterative learning is required, such as reinforcement learning. Furthermore, DTUMOS can also be exploited to provide quantitative evaluations and guidelines for policies and plans.

![fig1](https://user-images.githubusercontent.com/70340230/188314565-93bcc94c-2b07-4753-b7c5-db409758b1d6.png)

## How to use DTUMOS

### Prerequisites

- Available on Linux
- Use WSL2 for Window users
- [osrm-backend](https://github.com/Project-OSRM/osrm-backend)
- Python version >= 3.8

### Getting Started
1. Clone DTOMOS
    ```
    git clone https://github.com/HNU209/DTUMOS.git
    ```
2. Install requirements.txt  
    ```
    pip install requirements.txt
    ```
3. Run main.ipynb
4. Load result-data in visualization folder
5. Load result-data in report folder

## Architecture
The framework consists of four parts: 1) Data; 2) Deep learning and Machine learning models; 3) Operate mobility system; 4) Outputs

- **Data**: It represents the mobility pattern of passengers and goods. Various historical mobility data such as taxi trip records, smart card data, mobile phone cellular signaling data, and delivery and logistics data can be utilized. The road network is used in routing vehicles and predicting the travel time of vehicles. In DTUMOS, Open Street Map, which is open-source and easily applicable to various cities worldwide, was used.

- **DL/ML models**: It is essential to calculate the exact travel time when vehicles move from origins to destinations. The similarity of the digital twin to reality will be low, if temporal and spatial characteristics of travels, such as traffic congestion, peak hours, and day-of-week, time-of-day information, are not considered. For this reason, a novel framework that corrects the locations and travel time of vehicles is proposed. Based on deep learning, an Estimated Time of Arrival (ETA) was trained and utilized to improve the accuracy and simulation speed of DTUMOS.

- **Operating mobility system**: The third part is the process of operating a mobility system in the digital twin. Based on historical trip records, supply and demand can be generated exactly as in reality, and user customization (e.g., spatial and temporal randomness, increase/decrease in demand and supply) can also be applied. After determining the distributions of passengers and vehicles, a dispatch algorithm that matches passengers and vehicles is required, and the simulation is running as dispatch, and vehicle routing are operated sequentially. [The Open Street Route Machine (OSRM)](http://project-osrm.org/) is utilized for routing vehicles, which is open source and fast. 

- **Outputs**:  simulation visualizations and reports for the performance of the mobility system are derived as final outputs of DTUMOS. We utilize [deck.gl](https://deck.gl/) for visualization. In particular, we use TripLayer for rendering vehicles' paths that are suitable to represent a movement of a large number of vehicles smoothly. The system performance report provides overall results of the operation. It contains a level of service (LOS), vehicle operation information, and spatial analysis.

![architecture](https://user-images.githubusercontent.com/70340230/187696367-cd93a438-1f86-4e41-9ee7-f0486584057f.png)

## Implementation of DTUMOS
### Seoul - [Seoul visualization](https://hnu209.github.io/Seoul-visualization/) | [Seoul report](https://hnu209.github.io/Seoul-report/)
(The first loading could be slow due to the process of loading data from github pages)
- Data description: 
    - Data : Seoul, Republic of Korea (private)
    - Date : 2022-04-08
### New York - [New York visualization](https://hnu209.github.io/NewYork-visualization/) | [New York report](https://hnu209.github.io/NewYork-report/)
- Data description:
    - Data : [NewYork](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), [NYC](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)   
    - Date : 2016-04-08   
### Chicago - [Chicago visualization](https://hnu209.github.io/Chicago-visualization/)   
- Data description:   
    - Data : [Chicago](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew)   
    - Date : 2019-07-19   
### Jeju - [Jeju visualization](https://hnu209.github.io/Jeju-delivery-management-system/)
- Data description: 
    - Data : Jeju-do, Republic of Korea (private)
    - Date : 2022-04-01
