import React, { useState, useEffect, useCallback } from "react";

import DeckGL from "@deck.gl/react";
import { AmbientLight, PointLight, LightingEffect } from "@deck.gl/core";
import { ScatterplotLayer, IconLayer } from "@deck.gl/layers";
import { TripsLayer } from "@deck.gl/geo-layers";
import { Map } from "react-map-gl";

import Slider from "@mui/material/Slider";
import legend from "../img/legend.png";
import "../css/trip.css";

const ambientLight = new AmbientLight({
  color: [255, 255, 255],
  intensity: 1.0,
});

const pointLight = new PointLight({
  color: [255, 255, 255],
  intensity: 2.0,
  position: [-74.05, 40.7, 8000],
});

const lightingEffect = new LightingEffect({ ambientLight, pointLight });

const DEFAULT_THEME = {
  buildingColor: [74, 80, 87],
  trailColor0: [253, 128, 93],
  trailColor1: [23, 184, 190],
  effects: [lightingEffect],
};

const INITIAL_VIEW_STATE = {
  longitude: -73.98,
  latitude: 40.74,
  zoom: 12,
  minZoom: 5,
  maxZoom: 16,
  pitch: 20,
  bearing: 0,
};

const ICON_MAPPING = {
  marker: { x: 0, y: 0, width: 128, height: 128, mask: true },
};

const minTime = 0;
const maxTime = 1440;
const animationSpeed = 2;
const mapStyle = "mapbox://styles/spear5306/ckzcz5m8w002814o2coz02sjc";
const MAPBOX_TOKEN = `pk.eyJ1Ijoic3BlYXI1MzA2IiwiYSI6ImNremN5Z2FrOTI0ZGgycm45Mzh3dDV6OWQifQ.kXGWHPRjnVAEHgVgLzXn2g`; // eslint-disable-line

const returnAnimationTime = (time) => {
  if (time > maxTime) {
    return minTime;
  } else {
    return time + 0.01 * animationSpeed;
  }
};

const addZeroFill = (value) => {
  const valueString = value.toString();
  return valueString.length < 2 ? "0" + valueString : valueString;
};

const returnAnimationDisplayTime = (time) => {
  const hour = addZeroFill(parseInt((Math.round(time) / 60) % 24));
  const minute = addZeroFill(Math.round(time) % 60);
  return [hour, minute];
};

const currData = (data, time) => {
  const arr = [];
  data.forEach((v) => {
    const timestamp = v.timestamps;
    const s_t = timestamp[0];
    const e_t = timestamp[timestamp.length - 1];
    if (s_t <= time && e_t >= time) {
      arr.push(v);
    }
  });
  return arr;
};

const Trip = (props) => {
  const [time, setTime] = useState(minTime);
  const [animation] = useState([]);

  const trip = props.trip;
  const empty = currData(props.emptyTaxi, time);
  const ps = currData(props.passenger, time);

  const animate = useCallback(() => {
    setTime((time) => returnAnimationTime(time));
    animation.id = window.requestAnimationFrame(animate);
  }, [animation]);

  useEffect(() => {
    animation.id = window.requestAnimationFrame(animate);
    return () => window.cancelAnimationFrame(animation.id);
  }, [animation, animate]);

  const layers = [
    new TripsLayer({
      id: "trip",
      data: trip,
      getPath: (d) => d.trip,
      getTimestamps: (d) => d.timestamp,
      getColor: (d) =>
        d.vendor === 0 ? DEFAULT_THEME.trailColor0 : DEFAULT_THEME.trailColor1,
      opacity: 1,
      widthMinPixels: 3,
      lineJointRounded: false,
      trailLength: 0.8,
      currentTime: time,
      shadowEnabled: false,
    }),
    new ScatterplotLayer({
      id: "empty",
      data: empty,
      getPosition: (d) => d.loc,
      getFillColor: (d) => [255, 255, 255],
      getRadius: (d) => 10,
      opacity: 0.3,
      pickable: false,
      radiusMinPixels: 2,
      radiusMaxPixels: 2,
    }),
    new IconLayer({
      id: "ps",
      data: ps,
      sizeScale: 10,
      iconAtlas:
        "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png",
      iconMapping: ICON_MAPPING,
      getIcon: (d) => "marker",
      getSize: (d) => 1,
      getPosition: (d) => d.loc,
      getColor: (d) => [255, 255, 0],
      opacity: 0.3,
      pickable: false,
      radiusMinPixels: 2,
      radiusMaxPixels: 2,
    }),
  ];

  const SliderChange = (value) => {
    const time = value.target.value;
    setTime(time);
  };

  const [hour, minute] = returnAnimationDisplayTime(time);

  return (
    <div className="trip-container" style={{ position: "relative" }}>
      <DeckGL
        effects={DEFAULT_THEME.effects}
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      >
        <Map mapStyle={mapStyle} mapboxAccessToken={MAPBOX_TOKEN} />
      </DeckGL>
      <h1 className="time">TIME : {`${hour} : ${minute}`}</h1>
      <Slider
        id="slider"
        value={time}
        min={minTime}
        max={maxTime}
        onChange={SliderChange}
        track="inverted"
      />
      <img className="legend" src={legend} alt="legend"></img>
    </div>
  );
};

export default Trip;
