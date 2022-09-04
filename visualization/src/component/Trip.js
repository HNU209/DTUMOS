import React, { useState, useEffect } from 'react';
import { StaticMap } from 'react-map-gl';
import { AmbientLight, PointLight, LightingEffect } from '@deck.gl/core';
import DeckGL from '@deck.gl/react';
import { PolygonLayer, ScatterplotLayer, IconLayer } from '@deck.gl/layers';
import { TripsLayer } from '@deck.gl/geo-layers';
import '../css/trip.css';
import legend from '../img/legend.png';

const MAPBOX_TOKEN = `pk.eyJ1Ijoic3BlYXI1MzA2IiwiYSI6ImNremN5Z2FrOTI0ZGgycm45Mzh3dDV6OWQifQ.kXGWHPRjnVAEHgVgLzXn2g`; // eslint-disable-line

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

const material = {
  ambient: 0.1,
  diffuse: 0.6,
  shininess: 32,
  specularColor: [60, 64, 70],
};

const DEFAULT_THEME = {
  buildingColor: [74, 80, 87],
  trailColor0: [253, 128, 93],
  trailColor1: [23, 184, 190],
  material,
  effects: [lightingEffect],
};

const INITIAL_VIEW_STATE = {
  longitude: 127,
  latitude: 37.55,
  zoom: 11,
  minZoom: 5,
  maxZoom: 16,
  pitch: 20,
  bearing: 0,
};

const landCover = [
  [
    [-74.0, 40.7],
    [-74.02, 40.7],
    [-74.02, 40.72],
    [-74.0, 40.72],
  ],
];

const ICON_MAPPING = {
  marker: {x: 0, y: 0, width: 128, height: 128, mask: true}
};

const currData = (data, time) => {
  const arr = [];
  data.forEach(v => {
    const timestamp = v.timestamps;
    const s_t = timestamp[0];
    const e_t = timestamp[timestamp.length - 1];
    if ((s_t <= time) && (e_t >= time)) {
      arr.push(v)
    }
  })
  return arr;
}

function renderLayers(props) {
  const theme = DEFAULT_THEME;
  const time = props.time;
  const trip = props.trip;
  const empty = props.empty;
  const ps = props.ps;

  const currEmpty = currData(empty, time);
  const currPs = currData(ps, time);

  return [
    new PolygonLayer({
      id: 'ground',
      data: landCover,
      getPolygon: (f) => f,
      stroked: false,
      getFillColor: [0, 0, 0, 0],
    }),
    new TripsLayer({
      id: 'trip',
      data: trip,
      getPath: (d) => d.trips,
      getTimestamps: (d) => d.timestamps,
      getColor: (d) => 
      d.vendor === 0 ? theme.trailColor0 : theme.trailColor1,
      opacity: 0.5,
      widthMinPixels: 2,
      lineJointRounded: false,
      trailLength: 0.5,
      currentTime: time,
      shadowEnabled: false,
    }),
    new ScatterplotLayer({
      id: 'empty',
      data: currEmpty,
      getPosition: (d) => d.loc,
      getFillColor: (d) => [255, 255, 255],
      getRadius: (d) => 1,
      opacity: 0.3,
      pickable: false,
      radiusMinPixels: 1,
      radiusMaxPixels: 1,
    }),
    new IconLayer({
      id: 'ps',
      data: currPs,
      sizeScale: 10,
      iconAtlas: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png',
      iconMapping: ICON_MAPPING,
      getIcon: (d) => 'marker',
      getSize: d => 0.5,
      getPosition: (d) => d.loc,
      getColor: d => [255, 255, 0],
      opacity: 0.3,
      pickable: false,
      radiusMinPixels: 0.5,
      radiusMaxPixels: 0.5,
    }),
  ];
}

export default function Trip(props) {
  const minTime = props.minTime;
  const maxTime = props.maxTime;

  const animationSpeed = 4;
  const time = props.time;
  const trip = props.trip;
  const empty = props.empty;
  const ps = props.ps;

  const [animationFrame, setAnimationFrame] = useState('');
  const viewState = undefined;
  const mapStyle = 'mapbox://styles/spear5306/ckzcz5m8w002814o2coz02sjc';
  
  function animate() {
    props.setTime(time => {
      if (time > maxTime) {
        props.setReset(true)
        return minTime;
      } else {
        return time + (0.01) * animationSpeed;
      }
    })
    const af = window.requestAnimationFrame(animate);
    setAnimationFrame(af);
  }

  useEffect(() => {
    animate()
    return () => window.cancelAnimationFrame(animationFrame);
  }, [])

  return (
    <div className="trip-container" style={{position:'relative'}}>
      <DeckGL
        layers={renderLayers({'trip':trip, 'empty':empty, 'ps':ps, 'time':time})}
        effects={DEFAULT_THEME.effects}
        viewState={viewState}
        controller={true}
        initialViewState={INITIAL_VIEW_STATE}
      >
        <StaticMap
          mapStyle={mapStyle}
          preventStyleDiffing={true}
          mapboxApiAccessToken={MAPBOX_TOKEN}
        />
      </DeckGL>
      <h1 className="time">
        TIME : {(String(parseInt(Math.round(time) / 60) % 24).length === 2) ? parseInt(Math.round(time) / 60) % 24 : '0'+String(parseInt(Math.round(time) / 60) % 24)} : {(String(Math.round(time) % 60).length === 2) ? Math.round(time) % 60 : '0'+String(Math.round(time) % 60)}
      </h1>
      <img className='legend' src={legend}></img>
    </div>
  );
}