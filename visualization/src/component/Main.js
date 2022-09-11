import React, { useEffect, useState } from 'react';
import Trip from './Trip';
import '../css/main.css';
import Slider from '@mui/material/Slider';
import Splash from './Splash';

const axios = require('axios');

const getTripData = time => {
  const res = axios.get(`https://raw.githubusercontent.com/HNU209/NewYork-visualization/main/src/data/visual_data/newyork_trips.json`);
  const data = res.then(r => r.data);
  return data;
};

const getRestData = type => {
  const res = axios.get(`https://raw.githubusercontent.com/HNU209/NewYork-visualization/main/src/data/visualization_data/newyork_${type}.json`);
  const result = res.then(r => r.data);
  return result
}

export default function Main() {
  const minTime = 0;
  const maxTime = 1400;

  const [load, setLoad] = useState(false);
  const [time, setTime] = useState(minTime);
  const [trip, setTrip] = useState([]);
  const [ps, setPs] = useState([]);
  const [empty, setEmpty] = useState([]);

  useEffect(() => {
    async function getFetchData() {
      const trip = await getTripData();
      const empty = await getRestData('empty_taxi');
      const ps = await getRestData('ps_location');
      
      if (trip && empty && ps) {
        setTrip(trip);
        setPs(ps);
        setEmpty(empty);
        setLoad(true)
      }
    }

    getFetchData();
  }, [])
  
  const SliderChange = value => {
    const time = value.target.value;
    setTime(time);
  };

  return (
    <div className="container">
      {load ? 
      <>
        <Trip trip={trip} empty={empty} ps={ps} minTime={minTime} maxTime={maxTime} time={time} setTime={setTime}></Trip>
        <Slider id="slider" value={time} min={minTime} max={maxTime} onChange={SliderChange} track="inverted"/>
      </>
      :
      <Splash></Splash>
      }
    </div>
  );
}