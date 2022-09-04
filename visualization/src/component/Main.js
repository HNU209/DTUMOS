import React, { useEffect, useState } from 'react';
import Trip from './Trip';
import '../css/main.css';
import Slider from '@mui/material/Slider';
import Splash from './Splash';
import axios from 'axios';

const getTripData = time => {
  const res = axios.get(`https://raw.githubusercontent.com/HNU209/Seoul-visualization/main/src/data/visual_data/trips_${time}.json`);
  const result = res.then(r => r.data);
  return result
}

const getRestData = type => {
  const res = axios.get(`https://raw.githubusercontent.com/HNU209/Seoul-visualization/main/src/data/visualization_data/${type}.json`);
  const result = res.then(r => r.data);
  return result
}

export default function Main() {
  const minTime = 1320;
  const maxTime = 1439;

  const [reset, setReset] = useState(true);
  const [loaded, setLoaded] = useState(false);

  const [time, setTime] = useState(minTime);
  const [trip, setTrip] = useState();
  const [ps, setPs] = useState();
  const [empty, setEmpty] = useState();
  
  const [dataTime, setDataTime] = useState([]);
  const [dataList, setDataList] = useState([]);

  const init = async () => {
    const dataArr = [];
    const dataTimeArr = [];
    for (let time = minTime; time < minTime+3; time++) {
      const returnData = await getTripData(time);
      if (returnData) {
        dataArr.push(...returnData);
        dataTimeArr.push(time);
      }
    }

    const empty = await getRestData('empty_taxi');
    const ps = await getRestData('ps_location');

    if (dataArr && empty && ps) {
      setDataList(dataArr);
      setDataTime(dataTimeArr);
      setPs(ps);
      setEmpty(empty);
      setReset(false);
      setLoaded(true);
    }
  };

  useEffect(() => {
    init();
  }, [])

  useEffect(() => {
    if (reset) {
      init();
      setReset(false);
    }

    const set = new Set(dataTime);
    setDataTime([...set]);

    const t = Math.floor(time);
    if (!(dataTime.includes(t))) {
      setDataTime([...dataTime, t])
      const addData = async () => {
        const returnData = await getTripData(t);
        if (returnData) {
          setDataList([...dataList, ...returnData])

        }
      }
      addData(t);
    }

    const arr = [];
    for (let i = 0; i < dataList.length; i++) {
      const v = dataList[i];
      const s_t = v.timestamps[0];
      const e_t = v.timestamps[v.timestamps.length - 1];
      if ((s_t <= time) && (e_t) >= time) {
        arr.push(v);
      }
    }
    setDataList(arr);
    setTrip(arr);
  }, [time]);

  const clear = async time => {
    setDataList([]);
    setDataTime([]);

    const dataArr = [];
    const dataTimeArr = [];
    for (let t = time; t < time+3; t++) {
      if (time <= maxTime) {
        const returnData = await getTripData(t);
        if (returnData) {
          dataArr.push(...returnData);
          dataTimeArr.push(t);
        };
      };
    };

    setDataList(dataArr);
    setDataTime(dataTimeArr);
  };

  const SliderChange = value => {
    const time = value.target.value;
    clear(time);
    setTime(time);
  };

  return (
    <div className="container">
      {loaded ? 
      <>
        <Trip trip={trip} empty={empty} ps={ps} minTime={minTime} maxTime={maxTime} time={time} setTime={setTime} setReset={setReset}></Trip>
        <Slider id="slider" value={time} min={minTime} max={maxTime} onChange={SliderChange} track="inverted"/>
      </>
      :
      <Splash></Splash>
      }
    </div>
  );
}