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
![architecture](https://user-images.githubusercontent.com/70340230/187696367-cd93a438-1f86-4e41-9ee7-f0486584057f.png)

## Implementation of DTUMOS
### Seoul - [Seoul visualization](https://hnu209.github.io/Seoul-visualization/) | [Seoul report](https://hnu209.github.io/Seoul-report/)
- Data description: 
    - Data : Seoul, Republic of Korea
    - Date : 2022-04-08
### New York - [New York visualization](https://hnu209.github.io/NewYork-visualization/)   
- Data description:   
    - Data : [NewYork](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), [NYC](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)   
    - Date : 2016-04-09   
### Chicago - [Chicago visualization](https://hnu209.github.io/Chicago-visualization/)   
- Data description:   
    - Data : [Chicago](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew)   
    - Date : 2019-07-19   
### Jeju - [Jeju visualization](https://hnu209.github.io/Jeju-delivery-management-system/)
- Data description: 
    - Data : Jeju-do, Republic of Korea
    - Date : 2022-04-01
